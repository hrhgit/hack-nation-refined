"""Step-by-step extraction on the invented corpus: cards, self-check, the same ingest, and the failure paths."""
import json
import threading
import unittest

import test_pipeline as fixture
from test_pipeline import rec
from nav.agent import check_record, load_cards, render_core, run_agent_api, tool_specs
from nav.api import ApiError
from nav.ingest import Validator, run_ingest
from nav.config import load_schema
from nav.corpus import load_corpus
from nav.packets import load_index

SPAN = "A landlord shall not demand or receive a security deposit exceeding one month’s rent."


def reply(message, finish="stop"):
    return {"model": "deepseek-flash", "choices": [{"message": message, "finish_reason": finish}],
            "usage": {"prompt_tokens": 30, "completion_tokens": 20}}


def tool_call(tool, **args):
    return reply({"role": "assistant", "content": None, "tool_calls": [
        {"id": "call-%s" % tool, "type": "function", "function": {"name": tool, "arguments": json.dumps(args)}}]}, "tool_calls")


def final_answer():
    return reply({"role": "assistant", "content": json.dumps(rec(quoted_span=SPAN), ensure_ascii=False) + "\n" +
                  json.dumps({"packet_id": "D100-01", "n_rules": 1, "note": None})})


class AgentTest(unittest.TestCase):
    def setUp(self):
        fixture.PipelineTest.setUp(self)

    def tearDown(self):
        fixture.PipelineTest.tearDown(self)

    def script(self, replies):
        seen = []
        queue = list(replies)

        def post(messages, specs):
            seen.append([dict(m) for m in messages])
            nxt = queue.pop(0)
            if isinstance(nxt, Exception):
                raise nxt
            return nxt
        post.seen = seen
        return post

    def test_cards_self_check_and_final_answer_flow_into_ingest(self):
        post = self.script([tool_call("read_card", name="citations"),
                            tool_call("check_record", record_json=json.dumps(rec(quoted_span=SPAN), ensure_ascii=False)),
                            final_answer()])
        lines = []
        code = run_agent_api(self.paths, None, ["D100-01"], post=post, emit=lines.append)
        self.assertEqual(code, 0, lines)
        # the card text and the check result were handed back to the model
        self.assertIn("Card: citations", post.seen[1][-1]["content"])
        self.assertTrue(post.seen[2][-1]["content"].startswith("ACCEPTED."))
        res = run_ingest(self.paths, persist_ids=False)
        self.assertEqual(res.states["D100-01"]["state"], "done")
        self.assertEqual(len(res.rules), 1)
        logs = sorted((self.paths.work_dir / "api").glob("AGENT_D100-01_*.json"))
        self.assertEqual(len(logs), 1)
        log = json.loads(logs[0].read_text(encoding="utf-8"))
        self.assertEqual((log["steps"], log["cards_read"], log["checks"]), (3, ["citations"], 1))

    def test_api_error_stops_cleanly_and_writes_no_answer(self):
        post = self.script([ApiError("HTTP 429")])
        lines = []
        self.assertEqual(run_agent_api(self.paths, None, ["D100-01"], post=post, emit=lines.append), 1)
        self.assertFalse(list(self.paths.inbox_dir.glob("AGENT_*")) if self.paths.inbox_dir.exists() else [])
        self.assertTrue(any("HTTP 429" in l for l in lines))

    def test_an_answer_that_did_not_finish_is_not_imported(self):
        post = self.script([reply({"role": "assistant", "content": "{\"packet_id\": \"D100-01\""}, "length")])
        self.assertEqual(run_agent_api(self.paths, None, ["D100-01"], post=post, emit=lambda l: None), 1)
        self.assertFalse(list(self.paths.inbox_dir.glob("AGENT_*")) if self.paths.inbox_dir.exists() else [])

    def test_rejected_records_are_asked_again_with_the_reasons(self):
        bad = json.dumps(rec(quoted_span="Landlords may never hold more than a month of rent."), ensure_ascii=False)
        wrong = reply({"role": "assistant", "content": bad + "\n" + json.dumps({"packet_id": "D100-01", "n_rules": 1, "note": None})})
        post = self.script([wrong, final_answer()])
        lines = []
        code = run_agent_api(self.paths, None, ["D100-01"], post=post, emit=lines.append)
        self.assertEqual(code, 0, lines)
        self.assertIn("CORRECTIONS NEEDED", post.seen[1][1]["content"])      # the second conversation starts with the reasons
        self.assertEqual(run_ingest(self.paths, persist_ids=False).states["D100-01"]["state"], "done")

    def test_check_record_reports_errors_and_shows_what_conditions_do(self):
        index = load_index(self.paths)
        validator = Validator(load_corpus(self.paths), index, load_schema(self.paths), index["as_of"])
        lock = threading.Lock()
        self.assertIn("NOT VALID JSON", check_record(validator, lock, "{"))
        self.assertTrue(check_record(validator, lock, json.dumps(rec(quoted_span="made up sentence that is not there"))).startswith("REJECTED"))
        conds = {"conditions": [{"type": "built", "role": "covered", "op": "after", "date": "2027-01-01"}], "per_tenancy": None, "coverage_quotes": []}
        text = check_record(validator, lock, json.dumps(rec(quoted_span=SPAN, applicability=conds, effective_date=None), ensure_ascii=False))
        self.assertIn("built_after=2027-01-01", text)
        self.assertIn("built 1950, 5 units -> NOT in the results", text)

    def test_a_record_that_cites_only_federal_law_is_rejected(self):
        index = load_index(self.paths)
        validator = Validator(load_corpus(self.paths), index, load_schema(self.paths), index["as_of"])
        lock = threading.Lock()
        for federal in ("15 U.S.C.A. § 1681m", "24 C.F.R. § 982.310", "42 USC 3604; 24 CFR 100.50"):
            text = check_record(validator, lock, json.dumps(rec(quoted_span=SPAN, citation=federal), ensure_ascii=False))
            self.assertTrue(text.startswith("REJECTED"), federal)
            self.assertIn("federal law", text)
        # a state citation, or one that also mentions federal law next to a state provision, is not touched
        for ok in ("N.J.S.A. 46:8-21.2", "N.J.S.A. 10:5-12; 42 U.S.C. § 3604"):
            self.assertTrue(check_record(validator, lock, json.dumps(rec(quoted_span=SPAN, citation=ok), ensure_ascii=False)).startswith("ACCEPTED"), ok)

    def test_core_and_cards_are_consistent(self):
        core = render_core("2026-10-01")
        self.assertNotIn("{{", core)
        for name in load_cards():
            self.assertIn("`%s`" % name, core)                 # every card is in the index the model sees
        self.assertEqual([s["function"]["name"] for s in tool_specs()], ["read_card", "check_record"])
        self.assertEqual(tool_specs(("cards",))[0]["function"]["parameters"]["properties"]["name"]["enum"], sorted(load_cards()))


if __name__ == "__main__":
    unittest.main()
