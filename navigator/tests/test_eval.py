"""Tests of the extraction eval itself: known-good and known-bad answers through the grader, and the runner
against a local fake server. Needs the real starter pack on disk (skipped otherwise); nothing here calls a real API.
"""
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

try:
    from common import load_ctx, load_cases
    CTX = load_ctx()
    HAVE = (ROOT / "eval" / "cases.json").exists() and (ROOT / "eval" / "silver.json").exists()
except BaseException:  # no starter pack / no index on this machine
    HAVE = False


def oracle():
    by = {}
    for line in (ROOT / "eval" / "oracle" / "oracle.jsonl").read_text(encoding="utf-8").splitlines():
        by.setdefault(json.loads(line)["packet_id"], []).append(json.loads(line))
    return by


@unittest.skipUnless(HAVE, "needs the starter pack, work/index.json and eval/cases.json")
class GraderTests(unittest.TestCase):
    def grade(self, pid, objs, reason="stop"):
        from grader import grade
        return grade(CTX, pid, "\n".join(json.dumps(o, ensure_ascii=False) for o in objs), reason)

    def test_oracle_scores_full_marks(self):
        for pid, objs in oracle().items():
            r = self.grade(pid, objs)
            self.assertEqual(r["grade"]["score"], 1.0, (pid, r["grade"], r["explanation"]))

    def test_null_answers_score_near_zero(self):
        from grader import grade
        packets = [c["id"] for c in load_cases()]
        for text in ("", None):
            scores = [grade(CTX, p, text or json.dumps({"packet_id": p, "n_rules": 0, "note": None}), "stop")["grade"]["score"]
                       for p in packets]
            self.assertLess(sum(scores) / len(scores), 0.1)

    def test_known_bad_variants_are_caught(self):
        objs = oracle()["D069-01"]
        rec, receipt = copy.deepcopy(objs[0]), objs[1]
        # paraphrased quote -> rejected, packet is not clean
        bad = copy.deepcopy(rec); bad["quoted_span"] = "Landlords may not use pricing software that shares competitor rents."
        r = self.grade("D069-01", [bad, receipt])
        self.assertEqual(r["grade"]["clean"], 0.0)
        # descriptor after the citation
        bad = copy.deepcopy(rec); bad["citation"] = "P.L. 2026, c.43: ban on algorithms"
        self.assertEqual(self.grade("D069-01", [bad, receipt])["grade"]["cite_clean"], 0.0)
        # the same law written twice -> second one sent back
        r = self.grade("D069-01", [rec, copy.deepcopy(rec), {"packet_id": "D069-01", "n_rules": 2, "note": None}])
        self.assertEqual(r["grade"]["clean"], 0.0)
        self.assertEqual(r["grade"]["one_per_law"], 0.5)
        # the act spells out its date; leaving it empty is a miss even though the code can work it out
        bad = copy.deepcopy(rec); bad["effective_date"] = None
        r = self.grade("D069-01", [bad, receipt])
        self.assertEqual(r["grade"]["date_ok"], 0.0)
        self.assertEqual(r["grade"]["fields"], 1.0)  # the pipeline still ends with the right date
        # a pending bill called enacted has the wrong status
        s = oracle()["D046-01"]
        bad = copy.deepcopy(s[0]); bad["lifecycle"] = "enacted"
        r = self.grade("D046-01", [bad, s[1]])
        self.assertEqual(r["grade"]["fields"], 0.0)
        # the expected law is missing
        r = self.grade("D069-01", [{"packet_id": "D069-01", "n_rules": 0, "note": None}])
        self.assertEqual(r["grade"]["recall"], 0.0)
        self.assertEqual(r["grade"]["clean"], 0.0)  # earlier extraction found rules here
        # a record that carries another packet's id
        bad = copy.deepcopy(rec); bad["packet_id"] = "D066-01"
        self.assertEqual(self.grade("D069-01", [bad, receipt])["grade"]["clean"], 0.0)

    def test_varying_the_citation_does_not_hide_a_law_written_many_times(self):
        s = oracle()["D048-01"]
        base = s[0]
        recs = []
        for i, cite in enumerate(["Massachusetts rent control ban", "State law on local rent control (summary)", "https://example.org/rent-control"]):
            r = copy.deepcopy(base)
            r["citation"] = cite
            recs.append(r)
        r = self.grade("D048-01", recs + [{"packet_id": "D048-01", "n_rules": 3, "note": None}])
        self.assertLess(r["grade"]["one_per_law"], 0.5, r["grade"])
        # several distinct numbered laws in one cell are fine
        s = oracle()["D069-01"]
        a, b = copy.deepcopy(s[0]), copy.deepcopy(s[0])
        a["citation"], b["citation"] = "P.L. 2026, c.43 §4", "P.L. 2026, c.43 §6"
        r = self.grade("D069-01", [a, b, {"packet_id": "D069-01", "n_rules": 2, "note": None}])
        self.assertEqual(r["grade"]["one_per_law"], 1.0)

    def test_only_a_missing_answer_fails_the_non_empty_check(self):
        # D023-02 is the second part of a long statute; the earlier extraction wrote nothing there
        r = self.grade("D023-02", [{"packet_id": "D023-02", "n_rules": 0, "note": None}])
        self.assertEqual(r["grade"]["nonempty"], 1.0)
        # writing more than the earlier extraction is never punished
        s = copy.deepcopy(oracle()["D048-01"]); s[0]["packet_id"] = "D023-02"; s[0]["doc_id"] = "D023"
        self.assertEqual(self.grade("D023-02", [s[0], {"packet_id": "D023-02", "n_rules": 1, "note": None}])["grade"].get("nonempty"), 1.0)
        # but writing nothing where the earlier extraction found rules still fails
        self.assertEqual(self.grade("D048-01", [{"packet_id": "D048-01", "n_rules": 0, "note": None}])["grade"]["nonempty"], 0.0)

    def test_invented_numbers_are_caught(self):
        s = copy.deepcopy(oracle()["D066-01"])
        s[0]["key_value"] = "$75"
        r = self.grade("D066-01", s)
        self.assertEqual(r["grade"]["numbers_ok"], 0.0)
        self.assertEqual(self.grade("D066-01", oracle()["D066-01"])["grade"]["numbers_ok"], 1.0)

    def test_zero_padded_session_law_numbers_still_match_the_label(self):
        s = copy.deepcopy(oracle()["D069-01"])
        s[0]["citation"] = "P.L. 2026, c.043"
        self.assertEqual(self.grade("D069-01", s)["grade"]["recall"], 1.0)

    def test_truncated_answer_is_not_scored(self):
        r = self.grade("D069-01", oracle()["D069-01"], "length")
        self.assertEqual((r["status"], r["grade"]), ("truncated", {}))

    def test_labels_point_at_real_packets_and_text(self):
        from labels import LABELS
        for l in LABELS:
            text = CTX.packet_file(l["packet"]).read_text(encoding="utf-8")
            self.assertIn(l["packet"], CTX.index["packets"])
            self.assertTrue(text, l["id"])

    def test_rehearsal_gold_scores_full_marks_and_stays_out_of_the_real_corpus(self):
        by = {}
        for line in (ROOT / "eval" / "rehearsal" / "oracle.jsonl").read_text(encoding="utf-8").splitlines():
            by.setdefault(json.loads(line)["packet_id"], []).append(json.loads(line))
        self.assertEqual(len(by), 4)
        for pid, objs in by.items():
            r = self.grade(pid, objs)
            self.assertEqual(r["grade"]["score"], 1.0, (pid, r["grade"], r["explanation"]))
            self.assertIn(pid, CTX.rehearsal)
            self.assertFalse((CTX.paths.packets_dir / (pid + ".md")).exists())     # never in the production packets
        self.assertTrue(all(c["split"] == "test" for c in load_cases() if c["kind"] == "rehearsal"))

    def test_the_traps_in_the_rehearsal_documents_are_caught(self):
        by = {}
        for line in (ROOT / "eval" / "rehearsal" / "oracle.jsonl").read_text(encoding="utf-8").splitlines():
            by.setdefault(json.loads(line)["packet_id"], []).append(json.loads(line))
        # R003 holds six sections about one law: writing it as several records must be seen
        g = by["R003-01"][0]
        recs = []
        for i, q in enumerate(["The landlord shall hold the deposit in an interest-bearing account at a New Jersey bank and shall pay the tenant the interest earned each year.",
                               "Within thirty (30) days after the tenancy ends, the landlord shall return the deposit with interest, together with an itemized statement of any deductions."]):
            r = copy.deepcopy(g); r["quoted_span"] = q; r["title"] = "part %d" % i; recs.append(r)
        r = self.grade("R003-01", [g] + recs + [{"packet_id": "R003-01", "n_rules": 3, "note": None}])
        self.assertLess(r["grade"]["one_per_law"], 1.0)
        self.assertEqual(r["grade"]["clean"], 0.0)
        # R001: the code can work its date out, but the model leaving it empty is still a miss
        g = copy.deepcopy(by["R001-01"][0]); g["effective_date"] = None
        r = self.grade("R001-01", [g, by["R001-01"][1]])
        self.assertEqual(r["grade"]["date_ok"], 0.0)
        self.assertEqual(r["grade"]["fields"], 1.0)
        # R002 is a pending bill: calling it law gets the status wrong
        g = copy.deepcopy(by["R002-01"][0]); g["lifecycle"] = "enacted"
        self.assertLess(self.grade("R002-01", [g, by["R002-01"][1]])["grade"]["fields"], 1.0)

    def test_every_expected_date_can_be_found_in_the_packet_text(self):
        """A label may only expect a date the packet itself supports; otherwise it would reward guessing."""
        from labels import LABELS
        from nav import facts
        for l in LABELS:
            if not l.get("effective_date"):
                continue
            doc = CTX.docs[CTX.index["packets"][l["packet"]]["doc_id"]]
            found = facts.doc_dates(doc.body)
            act = facts.act_dates(doc.body)
            if act:
                found |= {act.effective, act.effective[:7], act.effective[:4]}
            self.assertIn(l["effective_date"], found, (l["id"], l["effective_date"]))

    def test_split_is_random_by_stratum_not_by_score(self):
        cases = [c for c in load_cases() if c["kind"] != "rehearsal"]   # the invented documents are all test, by design
        self.assertEqual({c["split"] for c in cases}, {"train", "test"})
        train = [c for c in cases if c["split"] == "train"]
        test = [c for c in cases if c["split"] == "test"]
        self.assertLessEqual(abs(len(train) - len(test)), 2)
        self.assertLessEqual(abs(sum(c["labeled"] for c in train) - sum(c["labeled"] for c in test)), 2)


def _packet_id(messages):
    m = re.search(r"packet_id: (\S+)", messages[1]["content"])
    return m.group(1)


@unittest.skipUnless(HAVE and shutil.which("node"), "needs the starter pack and node")
class RunnerTests(unittest.TestCase):
    def setUp(self):
        from stored_answers import stored_answers
        self.tmp = Path(tempfile.mkdtemp())
        self.flow = self.tmp / "flow"
        self.flow.mkdir()
        shutil.copy(ROOT / "eval" / "extraction" / "_state.json", self.flow / "_state.json")
        st = json.loads((self.flow / "_state.json").read_text())
        st["harness_sha"] = None
        (self.flow / "_state.json").write_text(json.dumps(st))
        (self.tmp / "env").write_text("NAV_API_KEY=test-key\n")
        answers = stored_answers(CTX)
        answers.update({pid: "\n".join(json.dumps(o) for o in objs) for pid, objs in oracle().items()})
        self.behaviour = {"D001-01": "length", "D003-01": "http500"}
        test = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                pid = _packet_id(body["messages"])
                mode = test.behaviour.get(pid)
                if mode == "http500":
                    self.send_response(500)
                    self.end_headers()
                    return
                served = "someone-else" if mode == "wrongmodel" else body["model"]
                out = {"model": served, "choices": [{"message": {"content": answers.get(pid, ""), "reasoning_content": "thinking..."},
                                                      "finish_reason": "length" if mode == "length" else "stop"}],
                       "usage": {"prompt_tokens": 1000, "completion_tokens": 200, "prompt_cache_hit_tokens": 800,
                                 "prompt_cache_miss_tokens": 200, "completion_tokens_details": {"reasoning_tokens": 50}}}
                data = json.dumps(out).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *_):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.base = "http://127.0.0.1:%d" % self.httpd.server_port

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_eval(self, *extra):
        import run_eval
        return run_eval.main(["--flow", str(self.flow), "--variant", "baseline", "--base-url", self.base,
                              "--env-file", str(self.tmp / "env"), "--concurrency", "3", *extra])

    def rows(self, name):
        p = self.flow / "baseline" / name
        return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []

    def test_gate_run_resume_errors_and_report(self):
        cases = "D069-01,D066-01,D001-01,D003-01,D004-01"
        with self.assertRaises(SystemExit) as cm:
            self.run_eval("--cases", cases)
        self.assertEqual(cm.exception.code, 2)                      # harness not approved yet
        self.assertEqual(self.run_eval("--approve-harness"), 0)
        self.assertEqual(self.run_eval("--cases", cases, "--reps", "2", "--dry-run"), 0)
        self.assertEqual(self.rows("results.jsonl"), [])             # a dry run writes nothing

        self.assertEqual(self.run_eval("--cases", cases, "--reps", "2"), 3)   # exit 3: some attempts failed
        rows, errors = self.rows("results.jsonl"), self.rows("errors.jsonl")
        self.assertEqual(len(rows), 8)                               # 3 ok cases + 1 truncated, 2 reps each
        self.assertEqual(sorted({r["status"] for r in rows}), ["ok", "truncated"])
        self.assertEqual([e["class"] for e in errors], ["harness_or_serving_error"] * 2)  # not scored as zeros
        self.assertEqual({e["prompt_id"] for e in errors}, {"D003-01"})
        ok = [r for r in rows if r["status"] == "ok"]
        for r in ok:                                                # the row must be complete, not just the score
            self.assertEqual(r["model"], "deepseek-flash")
            self.assertEqual(r["usage"]["input_tokens"], 1000)
            self.assertGreater(r["cost_usd"], 0)
            self.assertIn("score", r["grade"])
            self.assertTrue((self.flow / "baseline" / "traces" / ("%s_rep%d.json" % (r["prompt_id"], r["rep"]))).exists())
        trunc = [r for r in rows if r["status"] == "truncated"]
        self.assertTrue(all(r["grade"] == {} for r in trunc))
        trace = json.loads((self.flow / "baseline" / "traces" / "D069-01_rep0.json").read_text())
        self.assertEqual([t["role"] for t in trace], ["system", "user", "assistant"])
        self.assertEqual(trace[2]["thinking"], "thinking...")
        self.assertEqual({r["grade"]["score"] for r in ok if r["prompt_id"] == "D069-01"}, {1.0})   # oracle answer

        # fix the failing case and run the same command again: only the missing (case, rep) pairs run
        self.behaviour["D003-01"] = None
        self.assertEqual(self.run_eval("--cases", cases, "--reps", "2"), 0)
        rows = self.rows("results.jsonl")
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({(r["prompt_id"], r["rep"]) for r in rows}), 10)    # no duplicate (case, rep)

        # a response served by another model is an error, never a score
        self.behaviour["D004-01"] = "wrongmodel"
        (self.flow / "baseline" / "results.jsonl").write_text("")
        self.assertEqual(self.run_eval("--cases", "D004-01", "--reps", "1"), 3)
        self.assertEqual(self.rows("errors.jsonl")[-1]["class"], "served_model_mismatch")

        # the report builder accepts the layout
        (self.flow / "baseline" / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        builder = Path("/private/tmp/claude-501/bundled-skills")  # located by the caller; skip when absent
        found = sorted(builder.glob("*/*/claude-api/shared/evals/report/build-report-lite.mjs"))
        if found:
            out = subprocess.run(["node", str(found[-1]), str(self.flow)], capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertTrue((self.flow / "report.html").exists())

    def test_explore_mode_skips_the_gate_but_never_touches_the_climb_folder(self):
        explore = self.tmp / "explore"
        import run_eval
        # Existing evaluation results are user data. Check that they stay byte-for-byte
        # unchanged rather than assuming the user's baseline directory is empty.
        climb = ROOT / "eval" / "extraction" / "baseline"
        def snapshot():
            return {str(p.relative_to(climb)): p.read_bytes() for p in climb.rglob("*") if p.is_file()}
        before = snapshot()
        existed = climb.exists()
        common = ["--variant", "baseline", "--base-url", self.base, "--env-file", str(self.tmp / "env"), "--cases", "D069-01", "--reps", "1"]
        self.assertEqual(run_eval.main(["--flow", str(explore), "--explore", *common]), 0)
        self.assertEqual(len((explore / "baseline" / "results.jsonl").read_text().splitlines()), 1)
        self.assertEqual(run_eval.main(["--flow", str(ROOT / "eval" / "extraction"), "--explore", *common]), 1)
        self.assertEqual(climb.exists(), existed)
        self.assertEqual(snapshot(), before)

    def test_changing_the_harness_stops_the_next_run(self):
        self.assertEqual(self.run_eval("--approve-harness"), 0)
        st = json.loads((self.flow / "_state.json").read_text())
        st["harness_paths"] = st["harness_paths"] + ["eval/oracle/oracle.jsonl"]   # any change to the listed set
        (self.flow / "_state.json").write_text(json.dumps(st))
        with self.assertRaises(SystemExit) as cm:
            self.run_eval("--cases", "D069-01", "--reps", "1")
        self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
