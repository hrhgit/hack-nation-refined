"""Exercise actual outgoing HTTP, redirects, cache reuse and offline failures.

Every server is local and every credential and address is invented.
"""
import json
import os
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from migration.oracle import invoke, ROOT

class NetworkContracts(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.status = 200
        self.reply = {"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}]}
        owner = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_POST(self):
                owner.calls.append({"method": "POST", "path": self.path, "authorization": self.headers.get("Authorization"),
                                    "body": json.loads(self.rfile.read(int(self.headers["Content-Length"])))})
                self.respond()
            def do_GET(self):
                owner.calls.append({"method": "GET", "path": self.path})
                self.respond()
            def respond(self):
                self.send_response(owner.status)
                if owner.status == 302:
                    self.send_header("Location", owner.base + "/redirect-target")
                self.end_headers()
                self.wfile.write(owner.reply if isinstance(owner.reply, bytes) else json.dumps(owner.reply).encode())
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.base = "http://127.0.0.1:%d" % self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.process = None
        if os.environ.get("MIGRATION_BACKEND") == "typescript":
            self.process = subprocess.Popen(["node", str(ROOT / "dist/tests/migration/driver.js")],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, cwd=ROOT)

    def tearDown(self):
        if self.process:
            self.process.stdin.close()
            self.process.wait()
            self.process.stdout.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def call(self, op="chat_complete", **args):
        case = {"op": op, "args": {"base_url": self.base, **args}}
        if self.process:
            self.process.stdin.write(json.dumps(case) + "\n")
            self.process.stdin.flush()
            return json.loads(self.process.stdout.readline())
        return invoke(case)

    def test_model_request_and_whole_response(self):
        self.assertEqual(self.call(), {"value": self.reply})
        self.assertEqual(len(self.calls), 1)
        request = self.calls[0]
        self.assertEqual(request["authorization"], "Bearer test-secret")
        self.assertEqual(request["path"], "/chat/completions")
        self.assertEqual(request["body"], {"model": "deepseek-flash", "stream": False, "messages": [
            {"role": "system", "content": "test prompt"}, {"role": "user", "content": "test packet"}]})

    def test_redirect_never_forwards_credentials(self):
        self.status = 302
        self.assertIn("HTTP 302", self.call()["error"])
        self.assertEqual(len(self.calls), 1)
        self.assertNotIn("test-secret", self.call()["error"])

    def test_http_errors_do_not_retry(self):
        for code in [401, 402, 403, 429, 500]:
            with self.subTest(code=code):
                self.status = code
                before = len(self.calls)
                self.assertIn("HTTP %d" % code, self.call()["error"])
                self.assertEqual(len(self.calls) - before, 1)

    def test_malformed_response_is_rejected(self):
        self.reply = b"<html>broken</html>"
        self.assertIn("不是有效 JSON", self.call()["error"])
        self.reply = []
        self.assertIn("应为 JSON 对象", self.call()["error"])

    def test_census_single_cache_and_offline_replay(self):
        row = {"address_id": "A", "street_address": "1 Example St", "postal_city": "Boston", "state": "MA", "zip": "02110", "units": 5, "year_built": 1950}
        self.reply = {"result": {"addressMatches": [{"matchedAddress": "1 EXAMPLE ST, BOSTON, MA", "coordinates": {"x": -71.1, "y": 42.3},
            "geographies": {"Incorporated Places": [{"STATE": "25", "BASENAME": "Boston", "NAME": "Boston city", "GEOID": "2507000"}]}}]}}
        with tempfile.TemporaryDirectory() as directory:
            first = self.call("census", addresses={"A": row}, cache_dir=directory)
            self.assertEqual(first["value"]["A"]["legal_city"], "Boston, MA")
            self.assertEqual(first["value"]["A"]["resolved_by"], "geocoder")
            count = len(self.calls)
            self.assertEqual(self.call("census", addresses={"A": row}, cache_dir=directory, offline=True), first)
            self.assertEqual(len(self.calls), count)

    def test_offline_missing_cache_does_not_request(self):
        row = {"address_id": "A", "street_address": "1 Example St", "postal_city": "Boston", "state": "MA", "zip": "02110"}
        with tempfile.TemporaryDirectory() as directory:
            self.assertIn("离线缓存缺少地址结果", self.call("census", addresses={"A": row}, cache_dir=directory, offline=True)["error"])
            self.assertEqual(self.calls, [])

if __name__ == "__main__":
    unittest.main()
