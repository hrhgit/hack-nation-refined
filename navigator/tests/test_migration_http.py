"""Real HTTP tests shared by both backends, including static assets and bad inputs."""
import json
import os
import subprocess
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

class HttpContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.process = None
        if os.environ.get("MIGRATION_BACKEND") == "typescript":
            cls.process = subprocess.Popen(["node", "dist/web/server.js", "--port", "0"],
                cwd=Path(__file__).resolve().parents[1], stdout=subprocess.PIPE, text=True)
            line = cls.process.stdout.readline()
            import re
            port = re.search(r"127\.0\.0\.1:(\d+)", line)
            if not port:
                raise AssertionError("Server did not report its listening address: " + line)
            cls.base = "http://127.0.0.1:" + port.group(1)
        else:
            from web.server import Handler
            cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
            cls.thread.start()
            cls.base = "http://127.0.0.1:%d" % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        if cls.process:
            cls.process.terminate()
            cls.process.wait()
            cls.process.stdout.close()
        else:
            cls.server.shutdown()
            cls.server.server_close()
            cls.thread.join()

    def request(self, path, method="GET"):
        try:
            response = urllib.request.urlopen(urllib.request.Request(self.base + path, method=method))
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, response.headers, response.read()

    def test_static_assets_are_original_bytes(self):
        static = Path(__file__).resolve().parents[1] / "web" / "static"
        for path, name in [("/", "index.html"), ("/app.js", "app.js"), ("/i18n.js", "i18n.js"), ("/styles.css", "styles.css")]:
            with self.subTest(path=path):
                status, headers, body = self.request(path)
                self.assertEqual(status, 200)
                self.assertEqual(body, (static / name).read_bytes())
                self.assertEqual(int(headers["Content-Length"]), len(body))
                self.assertEqual(headers["Cache-Control"], "no-store")

    def test_all_json_routes(self):
        for path in ["/api/meta", "/api/rules", "/api/lookup?address_id=A0001", "/api/pipeline", "/api/source?doc_id=D024"]:
            with self.subTest(path=path):
                status, headers, body = self.request(path)
                self.assertEqual(status, 200)
                self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
                self.assertIsInstance(json.loads(body), dict)

    def test_invalid_inputs_have_actionable_json_errors(self):
        for path, expected in [("/api/lookup?address_id=missing", 404), ("/api/lookup?address_id=A0001&as_of=2026-02-30", 400),
                               ("/api/lookup?address_id=A0001&units=many", 400), ("/api/source?doc_id=../.env", 400),
                               ("/api/source?doc_id=X999", 404)]:
            with self.subTest(path=path):
                status, headers, body = self.request(path)
                self.assertEqual(status, expected)
                self.assertIn("error", json.loads(body))

    def test_unknown_paths_and_directory_traversal_are_not_served(self):
        for path in ["/missing", "/../server.py", "/../../.env", "/%2e%2e/.env", "/api/missing"]:
            self.assertEqual(self.request(path)[0], 404, path)

    def test_post_is_not_accepted(self):
        self.assertEqual(self.request("/api/meta", "POST")[0], 501)

    def test_extra_query_names_remain_ordinary_input(self):
        for name in ["__proto__", "constructor", "toString"]:
            self.assertEqual(self.request("/api/meta?" + name + "=ignored")[0], 200)

    def test_query_values_are_local_to_one_request(self):
        path = "/api/lookup?address_id=A0001"
        before = json.loads(self.request(path)[2])
        entered = json.loads(self.request(path + "&units=5&year_built=1960")[2])
        after = json.loads(self.request(path)[2])
        self.assertEqual(entered["entered_facts"], {"units": 5, "year_built": 1960})
        self.assertEqual(before["address"], after["address"])
        self.assertEqual(after["entered_facts"], {})

if __name__ == "__main__":
    unittest.main()
