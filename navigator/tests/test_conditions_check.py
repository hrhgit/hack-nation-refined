"""The conditions answer-key checker: labels, probes, and the way a wrong exclusion is counted."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

PACKET = ROOT / "work" / "packets" / "D041-01.md"


@unittest.skipUnless(PACKET.exists(), "the real packets are not prepared here")
class CheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import conditions_check as cc
        from common import load_ctx
        cls.cc = cc
        cls.ctx = load_ctx()
        text = PACKET.read_text(encoding="utf-8")
        m = re.search(r"Generally, the RSO applies to rental properties that were first built on or before October 1, 1978", text)
        cls.quote = m.group(0)
        cls.label = next(l for l in cc.COND_LABELS if l["id"] == "LA-RSO")

    def answer(self, conditions):
        rec = {"packet_id": "D041-01", "doc_id": "D041", "jurisdiction": "Los Angeles, CA", "category": "rent_increase_limits",
               "lifecycle": "enacted", "title": "Los Angeles Rent Stabilization Ordinance coverage", "requirement": "Rent increases are limited for covered units.",
               "key_value": None, "coverage_conditions": "Buildings first built on or before October 1, 1978", "exemptions": None, "penalty": None,
               "effective_date": None, "citation": "Los Angeles Rent Stabilization Ordinance (L.A.M.C. §151.00 et seq.)",
               "quoted_span": self.quote, "interaction": None, "confidence": 0.8, "conflict_flag": False, "conflict_note": None,
               "applicability": {"conditions": conditions, "per_tenancy": None, "coverage_quotes": [self.quote]}, "relations": []}
        return json.dumps(rec)

    def test_a_correct_cutoff_passes_every_probe(self):
        checks, wrong = self.cc.check_label(self.ctx, self.label, self.answer(
            [{"type": "built", "role": "covered", "op": "on_or_before", "date": "1978-10-01", "basis": "construction"}]))
        self.assertTrue(all(ok for _, ok, _ in checks), [c for c in checks if not c[1]])
        self.assertEqual(wrong, 0)

    def test_an_inverted_cutoff_is_caught_and_counted_as_a_wrong_exclusion(self):
        checks, wrong = self.cc.check_label(self.ctx, self.label, self.answer(
            [{"type": "built", "role": "covered", "op": "after", "date": "1978-10-01", "basis": "construction"}]))
        failed = [name for name, ok, _ in checks if not ok]
        self.assertIn("probe: old building must not be excluded", failed)
        self.assertGreaterEqual(wrong, 1)

    def test_a_missing_law_fails_every_check(self):
        checks, wrong = self.cc.check_label(self.ctx, self.label, json.dumps({"packet_id": "D041-01", "n_rules": 0, "note": None}))
        self.assertFalse(any(ok for _, ok, _ in checks))
        self.assertEqual(wrong, 0)

    def test_every_label_names_a_packet_that_exists_and_probes_are_well_formed(self):
        index = self.ctx.index["packets"]
        for label in self.cc.COND_LABELS:
            self.assertIn(label["packet"], index, label["id"])
            for p in label["probes"]:
                self.assertTrue(p["ok"] <= {"applies", "unknown", "excluded", "not_yet_effective", "pending"})
                self.assertTrue(p["exact"] is None or p["exact"] in p["ok"], (label["id"], p["why"]))
                self.assertTrue(p["basis"], (label["id"], p["why"]))


if __name__ == "__main__":
    unittest.main()
