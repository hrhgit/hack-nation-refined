"""Exercise the actual HTTP path and resumable extraction on invented source documents."""
import json
import os
import threading
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import test_pipeline as pipeline_fixture
from test_pipeline import rec
from nav.api import ApiConfig, ApiError, ChatClient, load_api_config, run_api
from nav.cli import main
from nav.ingest import run_ingest


def response(text, finish="stop"):
    return {"id": "local-test", "model": "deepseek-flash", "choices": [
        {"message": {"role": "assistant", "content": text}, "finish_reason": finish}],
        "usage": {"prompt_tokens": 30, "completion_tokens": 20, "total_tokens": 50}}


def receipt(pid, n=0):
    return json.dumps({"packet_id": pid, "n_rules": n, "note": None})


def deposit_answer(span=None):
    return json.dumps(rec(quoted_span=span or
        "A landlord shall not demand or receive a security deposit exceeding one month’s rent."),
        ensure_ascii=False) + "\n" + receipt("D100-01", 1)


@contextmanager
def server(replies):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append((self.path, dict(self.headers), body))
            status, payload = replies.pop(0)
            self.send_response(status)
            if status == 302:
                self.send_header("Location", "/redirect-target")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

        def log_message(self, *_):
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=lambda: httpd.serve_forever(poll_interval=0.01), daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:%d" % httpd.server_port, requests
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join()


class ApiTests(unittest.TestCase):
    def setUp(self):
        pipeline_fixture.PipelineTest.setUp(self)
        self.config = ApiConfig("test-secret")

    def tearDown(self):
        pipeline_fixture.PipelineTest.tearDown(self)

    def run_api(self, **kwargs):
        return run_api(self.paths, self.config, emit=lambda _: None, **kwargs)

    def files_snapshot(self):
        return {str(f.relative_to(self.tmp)): f.read_bytes() for f in self.tmp.rglob("*") if f.is_file()}

    def test_real_http_extraction_validation_outputs_and_resume(self):
        # A subscription answer is already done, so API skips it.
        old = self.paths.inbox_dir / "subscription.jsonl"
        old.write_text(receipt("D101-01"), encoding="utf-8")
        before = old.read_bytes()
        replies = [(200, response(deposit_answer())), (200, response(receipt("D102-01")))]
        with server(replies) as (url, requests):
            self.config.base_url = url + "/v1/"
            self.assertEqual(self.run_api(), 0)
            self.assertEqual(len(requests), 2)
            path, headers, payload = requests[0]
            self.assertEqual(path, "/v1/chat/completions")
            self.assertEqual(headers["Authorization"], "Bearer test-secret")
            self.assertEqual(payload["model"], "deepseek-flash")
            self.assertEqual(payload["stream"], False)
            self.assertIn("2026-10-01", payload["messages"][0]["content"])
            self.assertIn("<<<PACKET D100-01>>>", payload["messages"][1]["content"])
            self.assertNotIn("# DELIVERY", payload["messages"][1]["content"])
            self.assertNotIn("max_tokens", payload)
            self.assertNotIn("response_format", payload)  # JSONL is not a single JSON object.
            self.assertEqual(self.run_api(), 0)  # no further HTTP calls on resume
            self.assertEqual(len(requests), 2)
        self.assertEqual(old.read_bytes(), before)
        rules = json.loads((self.paths.out_dir / "rules.json").read_text())["rules"]
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]["status"], "not_yet_effective")
        self.assertIn("one month’s rent", rules[0]["quoted_span"])
        archive = list((self.paths.work_dir / "api").glob("*.json"))
        self.assertEqual(len(archive), 2)
        self.assertEqual(json.loads(archive[0].read_text())["response"]["usage"]["total_tokens"], 50)
        self.assertTrue(all("test-secret" not in f.read_text() for f in archive))

    def test_invalid_quote_is_corrected_with_feedback_and_history_preserved(self):
        replies = [(200, response(deposit_answer("The tenant must only ever pay a fictional deposit."))),
                   (200, response(deposit_answer()))]
        with server(replies) as (url, requests):
            self.config.base_url = url
            self.assertEqual(self.run_api(only=["D100"]), 0)
            self.assertEqual(len(requests), 2)
            self.assertIn("quoted_span not found", requests[1][2]["messages"][1]["content"])
        self.assertEqual(len(list(self.paths.inbox_dir.glob("API_*.jsonl"))), 2)
        self.assertEqual(run_ingest(self.paths).states["D100-01"]["state"], "done")

    def test_once_reports_remaining_then_later_run_completes(self):
        replies = [(200, response(deposit_answer().splitlines()[0])),  # no receipt
                   (200, response(deposit_answer()))]
        with server(replies) as (url, requests):
            self.config.base_url = url
            self.assertEqual(self.run_api(only=["D100-01"], once=True), 2)
            self.assertEqual(run_ingest(self.paths).states["D100-01"]["state"], "incomplete")
            self.assertEqual(self.run_api(only=["D100-01"]), 0)
            self.assertIn("no receipt", requests[1][2]["messages"][1]["content"])

    def test_wrong_record_field_type_is_rejected_then_corrected(self):
        wrong = rec(category=["security_deposits"], applicability={"date_basis": []}, quoted_span="text")
        replies = [(200, response(json.dumps(wrong) + "\n" + receipt("D100-01", 1))),
                   (200, response(deposit_answer()))]
        with server(replies) as (url, requests):
            self.config.base_url = url
            self.assertEqual(self.run_api(only=["D100"]), 0)
            self.assertIn("category must be text or null", requests[1][2]["messages"][1]["content"])

    def test_truncated_response_never_becomes_done_even_with_valid_receipt(self):
        with server([(200, response(receipt("D100-01"), "length"))]) as (url, _):
            self.config.base_url = url
            with self.assertRaisesRegex(ApiError, "未正常结束"):
                self.run_api(only=["D100"])
        self.assertEqual(run_ingest(self.paths).states["D100-01"]["state"], "pending")
        self.assertFalse(list(self.paths.inbox_dir.glob("API_*.jsonl")))
        self.assertEqual(len(list((self.paths.work_dir / "api").glob("*.json"))), 1)

    def test_wrong_packet_and_unfinished_json_never_imported(self):
        for text in (receipt("D101-01"), receipt("D100-01") + '\n{"packet_id":"D100-01",',
                     receipt("D100-01") + "\n" + receipt("D100-01"), receipt("D100-01", False)):
            with self.subTest(text=text), server([(200, response(text))]) as (url, _):
                self.config.base_url = url
                with self.assertRaises(ApiError):
                    self.run_api(only=["D100"])
                self.assertFalse(list(self.paths.inbox_dir.glob("API_*.jsonl")))

    def test_http_failure_keeps_completed_progress_and_does_not_retry(self):
        replies = [(200, response(receipt("D100-01"))), (429, {"error": "test-secret"})]
        with server(replies) as (url, requests):
            self.config.base_url = url
            with self.assertRaisesRegex(ApiError, "HTTP 429") as caught:
                self.run_api()
            self.assertNotIn("test-secret", str(caught.exception))
            self.assertEqual(len(requests), 2)
        self.assertEqual(run_ingest(self.paths).states["D100-01"]["state"], "done")
        self.assertTrue((self.paths.out_dir / "rules.json").exists())

    def test_auth_errors_and_redirects_are_not_retried_or_followed(self):
        for status in (401, 302):
            with self.subTest(status=status), server([(status, {"error": "test-secret"})]) as (url, requests):
                self.config.base_url = url
                with self.assertRaises(ApiError) as caught:
                    ChatClient(self.config).complete("prompt", "packet")
                self.assertNotIn("test-secret", str(caught.exception))
                self.assertEqual(len(requests), 1)

    def test_connection_error_has_no_timeout_no_retry_and_no_secret_in_message(self):
        import urllib.error
        client = ChatClient(self.config)
        with patch.object(client.opener, "open", side_effect=urllib.error.URLError("test-secret")) as call:
            with self.assertRaises(ApiError) as caught:
                client.complete("prompt", "packet")
            self.assertNotIn("test-secret", str(caught.exception))
            self.assertEqual(call.call_count, 1)
            self.assertIsNone(call.call_args.kwargs["timeout"])

    def test_malformed_or_empty_api_response_retained_but_not_imported(self):
        for body in ({"error": "bad"}, response("")):
            with self.subTest(body=body), server([(200, body)]) as (url, _):
                self.config.base_url = url
                with self.assertRaises(ApiError):
                    self.run_api(only=["D100"])
        self.assertFalse(list(self.paths.inbox_dir.glob("API_*.jsonl")))
        self.assertEqual(len(list((self.paths.work_dir / "api").glob("*.json"))), 2)

    def test_dry_run_needs_no_key_and_changes_no_files(self):
        before = self.files_snapshot()
        self.config.key = ""
        with patch.object(ChatClient, "complete", side_effect=AssertionError("must not call API")):
            self.assertEqual(self.run_api(dry_run=True), 0)
        self.assertEqual(self.files_snapshot(), before)

    def test_bad_selection_or_changed_packet_fails_before_request(self):
        with patch.object(ChatClient, "complete", side_effect=AssertionError("must not call API")):
            with self.assertRaisesRegex(ApiError, "未知"):
                self.run_api(only=["typo"])
            (self.paths.packets_dir / "D100-01.md").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ApiError, "不一致"):
                self.run_api(only=["D100"])

    def test_environment_overrides_local_file_without_shell_execution(self):
        f = self.tmp / ".env"
        f.write_text('# config\nDEEPSEEK_API_KEY="file-secret"\nNAV_API_MODEL=deepseek-flash\n'
                     'NAV_API_BASE_URL=https://api.deepseek.com\n', encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            config = load_api_config(f)
            self.assertEqual(config.key, "file-secret")
            self.assertEqual(config.endpoint, "https://api.deepseek.com/chat/completions")
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "env-secret", "NAV_API_MODEL": "custom"}, clear=True):
            self.assertEqual(load_api_config(f).key, "env-secret")
            self.assertEqual(load_api_config(f).model, "custom")
            self.assertEqual(load_api_config(f, model="override").model, "override")
        with patch.dict(os.environ, {}, clear=True):
            f.write_text("DEEPSEEK_API_KEY=\n", encoding="utf-8")
            with self.assertRaisesRegex(ApiError, "尚未配置"):
                load_api_config(f)
            self.assertEqual(load_api_config(f, require_key=False).model, "deepseek-flash")

    def test_cli_executes_http_flow_and_missing_key_gives_clean_error(self):
        env_file = self.tmp / ".env"
        env_file.write_text("DEEPSEEK_API_KEY=\n", encoding="utf-8")
        with patch("nav.cli._paths", return_value=self.paths), patch.dict(os.environ, {}, clear=True):
            self.assertEqual(main(["api", "--env-file", str(env_file)]), 1)
            with server([(200, response(deposit_answer()))]) as (url, requests):
                env_file.write_text("DEEPSEEK_API_KEY=test-secret\nNAV_API_BASE_URL=" + url, encoding="utf-8")
                self.assertEqual(main(["api", "--env-file", str(env_file), "--only", "D100"]), 0)
                self.assertEqual(len(requests), 1)

    def test_unencrypted_remote_and_embedded_credentials_rejected(self):
        for url in ("http://api.deepseek.com", "https://secret@api.deepseek.com", "https://api.deepseek.com?key=secret"):
            with self.subTest(url=url), self.assertRaises(ApiError):
                ApiConfig("test", base_url=url).endpoint


if __name__ == "__main__":
    unittest.main()
