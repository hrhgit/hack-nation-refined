"""Coverage conditions (contract version 2): reading, checking against the source, arithmetic, merging."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nav import conditions  # noqa: E402
from nav.config import Paths  # noqa: E402
from nav.ingest import run_ingest  # noqa: E402
from nav.packets import prepare  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"
DATES = {"1979-06-13", "1979-06", "1979", "1980", "1978-10-01", "1978-10", "1978"}
NUMS = {"15", "4", "2", "3", "10"}


def parse(conds, **extra):
    warns = []
    out = conditions.parse(dict(conditions=conds, **extra), warns, DATES, NUMS, None)
    return out, warns


class ArithmeticTests(unittest.TestCase):
    def test_exemption_after_a_date_means_covered_on_or_before_it(self):
        out, w = parse([{"type": "built", "role": "exempt", "op": "after", "date": "June 13, 1979", "basis": "certificate_of_occupancy"}])
        self.assertEqual(out["built_on_or_before"], "1979-06-13")
        self.assertIsNone(out["built_after"])
        self.assertEqual(out["date_basis"], "certificate_of_occupancy")
        self.assertEqual(w, [])

    def test_all_eight_date_directions(self):
        want = {("covered", "on_or_before"): "built_on_or_before", ("covered", "before"): "built_before",
                ("covered", "after"): "built_after", ("covered", "on_or_after"): "built_on_or_after",
                ("exempt", "after"): "built_on_or_before", ("exempt", "on_or_after"): "built_before",
                ("exempt", "before"): "built_on_or_after", ("exempt", "on_or_before"): "built_after"}
        for (role, op), key in want.items():
            out, _ = parse([{"type": "built", "role": role, "op": op, "date": "1980"}])
            self.assertEqual({k for k in conditions.DATE_KEYS if out[k]}, {key}, (role, op))

    def test_unit_counts_are_turned_into_minimum_and_maximum(self):
        cases = [("covered", "at_least", 3, (3, None)), ("covered", "more_than", 4, (5, None)),
                 ("covered", "at_most", 4, (None, 4)), ("covered", "fewer_than", 4, (None, 3)),
                 ("exempt", "at_most", 4, (5, None)), ("exempt", "fewer_than", 4, (4, None)),
                 ("exempt", "at_least", 4, (None, 3)), ("exempt", "more_than", 4, (None, 4))]
        for role, op, n, (lo, hi) in cases:
            out, _ = parse([{"type": "units", "role": role, "op": op, "n": n}])
            self.assertEqual((out["min_units"], out["max_units"]), (lo, hi), (role, op, n))

    def test_rolling_years_and_owner_exemption(self):
        out, _ = parse([{"type": "built_within_years", "role": "exempt", "years": 15, "basis": "certificate_of_occupancy"},
                        {"type": "owner", "role": "exempt", "who": "owner-occupied duplex", "unit_limit": 2}])
        self.assertEqual(out["exempt_if_newer_than_years"], 15)
        self.assertTrue(out["owner_dependent"])
        self.assertEqual(out["owner_exempt_if_units_at_most"], 2)
        self.assertIsNone(out["other"])      # an owner exemption is tested through owner_dependent, not left as free text

    def test_owner_exemption_without_a_size_limit_cannot_be_bounded(self):
        out, _ = parse([{"type": "owner", "role": "exempt", "who": "natural person", "unit_limit": None},
                        {"type": "owner", "role": "exempt", "who": "owner-occupied duplex", "unit_limit": 2}])
        self.assertTrue(out["owner_dependent"])
        self.assertIsNone(out["owner_exempt_if_units_at_most"])

    def test_two_cutoffs_in_one_direction_keep_the_stricter(self):
        out, _ = parse([{"type": "built", "role": "covered", "op": "on_or_before", "date": "1980"},
                        {"type": "built", "role": "covered", "op": "on_or_before", "date": "1978-10-01"}])
        self.assertEqual(out["built_on_or_before"], "1978-10-01")


class ConditionalExemptionTests(unittest.TestCase):
    def test_an_exemption_that_needs_a_filing_is_kept_apart_from_real_exclusions(self):
        out, w = parse([{"type": "built_within_years", "role": "exempt", "years": 15, "basis": "construction", "conditional": True},
                        {"type": "built", "role": "exempt", "op": "after", "date": "1979-06-13", "conditional": True},
                        {"type": "units", "role": "exempt", "op": "at_most", "n": 4, "conditional": True}])
        self.assertIsNone(out["exempt_if_newer_than_years"])
        self.assertIsNone(out["built_on_or_before"])
        self.assertIsNone(out["min_units"])
        self.assertEqual([sorted(i["flats"]) for i in out["deferred"]],
                         [["date_basis", "exempt_if_newer_than_years"], ["built_on_or_before"], ["min_units"]])
        self.assertEqual(out["deferred"][2]["flats"]["min_units"], 5)       # "four or fewer" is exempt, so the rest has 5 or more
        self.assertIsNone(out["other"])
        self.assertEqual(w, [])

    def test_the_flag_does_not_change_coverage_conditions_and_must_be_true(self):
        out, _ = parse([{"type": "units", "role": "covered", "op": "at_least", "n": 3, "conditional": True},
                        {"type": "units", "role": "exempt", "op": "at_most", "n": 2, "conditional": "yes"}])
        self.assertEqual(out["min_units"], 3)      # a coverage condition keeps its meaning; "yes" is not true
        self.assertEqual(out["deferred"], [])


class GroupTests(unittest.TestCase):
    WINDOW = [{"type": "built", "role": "exempt", "op": "after", "date": "1979-06-13", "group": "w"},
              {"type": "built", "role": "exempt", "op": "before", "date": "1980", "group": "w"}]

    def test_conditions_with_one_group_form_one_exemption(self):
        out, _ = parse(self.WINDOW)
        self.assertIsNone(out["built_on_or_before"])             # neither is a separate exclusion
        self.assertIsNone(out["built_on_or_after"])
        self.assertEqual(len(out["deferred"]), 1)
        item = out["deferred"][0]
        self.assertEqual([sorted(m) for m in item["flats_all"]], [["built_on_or_before"], ["built_on_or_after"]])
        self.assertFalse(item["conditional"])

    def test_a_conditional_window_and_a_single_condition_in_a_group(self):
        out, _ = parse([dict(c, conditional=True) for c in self.WINDOW])
        self.assertTrue(out["deferred"][0]["conditional"])
        out, _ = parse([{"type": "units", "role": "exempt", "op": "at_most", "n": 4, "group": "g"}])
        self.assertEqual(out["min_units"], 5)                    # a group of one is an ordinary exclusion
        self.assertEqual(out["deferred"], [])


class OwnerAndScopeTests(unittest.TestCase):
    def test_owner_only_coverage_with_a_size_limit_caps_the_units(self):
        out, _ = parse([{"type": "owner", "role": "covered", "who": "landlord-occupied", "unit_limit": 3}])
        self.assertEqual((out["max_units"], out["owner_dependent"]), (3, True))

    def test_single_homes_and_condominiums_are_a_kind_of_housing_not_an_owner(self):
        out, _ = parse([{"type": "owner", "role": "exempt", "who": "single-family home or condominium owned by a natural person", "unit_limit": None}])
        self.assertFalse(out["owner_dependent"])
        self.assertEqual(len(out["program_notes"]), 1)

    def test_a_scope_limit_stays_open_even_when_it_names_a_program(self):
        out, _ = parse([{"type": "other", "role": "covered", "text": "only housing providers receiving city funding or with income-restricted units"},
                        {"type": "other", "role": "exempt", "text": "housing restricted by deed as affordable"}])
        self.assertEqual(out["other"], "only housing providers receiving city funding or with income-restricted units")
        self.assertEqual(out["program_notes"], ["housing restricted by deed as affordable"])


class ProgramNoteTests(unittest.TestCase):
    def test_kinds_of_housing_are_notes_but_owner_filings_and_other_facts_stay_open(self):
        out, _ = parse([{"type": "other", "text": "housing restricted by deed as affordable for low-income households"},
                        {"type": "other", "text": "public housing owned by a housing authority"},
                        {"type": "other", "text": "single-family home or condominium alienable separate from other titles"},
                        {"type": "other", "text": "only units that the landlord registered with the board before first rental"}])
        self.assertEqual(len(out["program_notes"]), 3)
        self.assertEqual(out["other"], "only units that the landlord registered with the board before first rental")

    def test_a_note_alone_leaves_other_empty(self):
        out, _ = parse([{"type": "other", "text": "units with Section 8 subsidies"}])
        self.assertIsNone(out["other"])
        self.assertEqual(out["program_notes"], ["units with Section 8 subsidies"])


class SourceCheckTests(unittest.TestCase):
    def test_a_number_or_date_not_in_the_source_becomes_an_unresolved_condition(self):
        out, w = parse([{"type": "built", "role": "exempt", "op": "after", "date": "1991-01-01"},
                        {"type": "units", "role": "exempt", "op": "at_most", "n": 40}])
        self.assertIsNone(out["built_on_or_before"])
        self.assertIsNone(out["min_units"])
        self.assertIn("could not be matched", out["other"])
        self.assertEqual(len(w), 2)

    def test_threshold_may_be_stated_as_more_than_n(self):
        out, w = parse([{"type": "units", "role": "covered", "op": "more_than", "n": 4}])
        self.assertEqual(out["min_units"], 5)      # 5 is not in the text, 4 is
        self.assertEqual(w, [])

    def test_bad_items_never_raise(self):
        out, w = parse(["x", {"type": "units"}, {"type": "mystery"}, {"type": "built", "role": "covered"}])
        self.assertEqual(out["contract"], 2)
        self.assertEqual(len(w), 4)
        self.assertFalse(out["owner_dependent"])

    def test_quotes_must_be_verbatim(self):
        warns = []
        locate = lambda q: q if q == "owner-occupied premises of not more than four dwelling units" else None
        out = conditions.parse({"conditions": [], "coverage_quotes": [
            "owner-occupied premises of not more than four dwelling units", "a made up sentence here"]}, warns, None, None, locate)
        self.assertEqual(out["coverage_quotes"], ["owner-occupied premises of not more than four dwelling units"])
        self.assertEqual(len(warns), 1)

    def test_relations(self):
        warns = []
        locate = lambda q: q if q.startswith("A municipality shall be prohibited") else None
        got = conditions.parse_relations([
            {"type": "preempts_local", "quote": "A municipality shall be prohibited from enacting an ordinance that conflicts with this act."},
            {"type": "preempts_local", "quote": "A municipality shall be prohibited from enacting an ordinance that conflicts with this act."},
            {"type": "invented", "quote": "A municipality shall be prohibited from x"},
            {"type": "yields_to_local", "quote": "not in the source at all, so dropped"}], warns, locate)
        self.assertEqual([r["type"] for r in got], ["preempts_local"])
        self.assertEqual(len(warns), 2)


class FirstFormatTests(unittest.TestCase):
    def test_flat_keys_from_an_earlier_answer_still_read(self):
        warns = []
        out = conditions.parse({"built_on_or_before": "1978-10-01", "date_basis": "certificate_of_occupancy",
                                "min_units": 3, "owner_dependent": "true", "other": "only subsidised units"}, warns)
        self.assertEqual((out["built_on_or_before"], out["min_units"], out["owner_dependent"]), ("1978-10-01", 3, True))
        self.assertEqual(out["other"], "only subsidised units")
        self.assertIsNone(out["contract"])
        self.assertEqual(warns, [])

    def test_empty_and_malformed_applicability(self):
        self.assertEqual(conditions.parse(None, []), conditions.empty())
        w = []
        self.assertEqual(conditions.parse("x", w), conditions.empty())
        self.assertEqual(len(w), 1)


class MergeTests(unittest.TestCase):
    def rule(self, doc, **appl):
        a = conditions.empty()
        a.update(appl)
        return {"source_doc_id": doc, "applicability": a, "valid_through": None, "relations": []}

    def test_missing_conditions_are_filled_never_overwritten(self):
        p = self.rule("D1", min_units=3, owner_dependent=False)
        o = self.rule("D2", min_units=5, built_on_or_before="1979-06-13", owner_dependent=True, other="subsidised only")
        o["valid_through"] = "2027-02"
        o["relations"] = [{"type": "preempts_local", "quote": "x" * 20}]
        notes, warns = [], []
        conditions.merge(p, o, "D2", notes, warns)
        a = p["applicability"]
        self.assertEqual((a["min_units"], a["built_on_or_before"], a["owner_dependent"], a["other"]), (3, "1979-06-13", True, "subsidised only"))
        self.assertEqual(p["valid_through"], "2027-02")
        self.assertEqual(len(p["relations"]), 1)
        self.assertTrue(any("min_units differs" in w for w in warns))


ORDINANCE = """SOURCE: https://example.org/springfield
RETRIEVED: 2026-10-03 12:00 UTC

ORDINANCE NO. 2026-31
Chapter 7 Rent increases

Section 7.1 The annual rent increase may not exceed 3 percent for the period March 1, 2026 through February 28, 2027.
Section 7.2 This chapter does not apply to owner-occupied buildings of not more than two dwelling units, or to units that first received a certificate of occupancy after June 13, 1979.
Section 7.3 A municipality shall be prohibited from enacting an ordinance that conflicts with this chapter.
"""
MANIFEST = ("doc_id,jurisdictions,url,source_type,capture,retrieved_at,sha256,text_file,status\n"
            'D200,"Cambridge, MA",https://example.org/springfield,official,yes,2026-10-03 12:00 UTC,,text/D200.txt,ok\n')


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        pack = self.tmp / "pack"
        (pack / "corpus" / "text").mkdir(parents=True)
        (pack / "schema").mkdir()
        shutil.copy(FIX / "rule_record.schema.json", pack / "schema")
        (pack / "corpus" / "corpus_manifest.csv").write_text(MANIFEST, encoding="utf-8")
        (pack / "corpus" / "text" / "D200.txt").write_text(ORDINANCE, encoding="utf-8")
        self.paths = Paths(data_dir=pack, work_dir=self.tmp / "work", out_dir=self.tmp / "outputs", extra_dir=self.tmp / "extra")
        prepare(self.paths, "2026-10-01")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def record(self, **kw):
        base = {"packet_id": "D200-01", "doc_id": "D200", "jurisdiction": "Cambridge, MA", "category": "rent_increase_limits",
                "lifecycle": "enacted", "title": "Annual cap", "requirement": "Rent may rise at most 3 percent a year.",
                "key_value": "3%", "coverage_conditions": "Rentals except small owner-occupied buildings", "exemptions": "owner-occupied, new",
                "penalty": None, "effective_date": "2026-03-01", "valid_through": "2027-02-28",
                "citation": "Cambridge Mun. Code §7.1",
                "quoted_span": "The annual rent increase may not exceed 3 percent for the period March 1, 2026 through February 28, 2027.",
                "interaction": None, "confidence": 0.9, "conflict_flag": False, "conflict_note": None,
                "applicability": {"conditions": [
                    {"type": "owner", "role": "exempt", "who": "owner-occupied", "unit_limit": 2},
                    {"type": "built", "role": "exempt", "op": "after", "date": "1979-06-13", "basis": "certificate_of_occupancy"}],
                    "per_tenancy": None, "coverage_quotes": [
                        "This chapter does not apply to owner-occupied buildings of not more than two dwelling units, or to units that first received a certificate of occupancy after June 13, 1979."]},
                "relations": [{"type": "preempts_local", "quote": "A municipality shall be prohibited from enacting an ordinance that conflicts with this chapter."}]}
        base.update(kw)
        return base

    def ingest(self, *records):
        f = self.paths.inbox_dir
        f.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(r) for r in records] + [json.dumps({"packet_id": "D200-01", "n_rules": len(records), "note": None})]
        (f / "answer.jsonl").write_text("\n".join(lines), encoding="utf-8")
        return run_ingest(self.paths, persist_ids=False)

    def test_new_fields_flow_through(self):
        res = self.ingest(self.record())
        self.assertEqual(len(res.rules), 1, res.rejected)
        r = res.rules[0]
        a = r["applicability"]
        self.assertEqual(a["built_on_or_before"], "1979-06-13")
        self.assertEqual(a["owner_exempt_if_units_at_most"], 2)
        self.assertEqual(a["date_basis"], "certificate_of_occupancy")
        self.assertEqual(a["contract"], 2)
        self.assertEqual(len(a["coverage_quotes"]), 1)
        self.assertEqual(r["valid_through"], "2027-02-28")
        self.assertEqual(r["relations"][0]["type"], "preempts_local")

    def test_wrong_fields_never_reject_the_record(self):
        bad = self.record(valid_through="someday", relations="yes",
                          applicability={"conditions": [{"type": "units", "role": "exempt", "op": "at_most", "n": 99}],
                                         "coverage_quotes": ["not in the document at all"]})
        res = self.ingest(bad)
        self.assertEqual(len(res.rules), 1, res.rejected)
        r = res.rules[0]
        self.assertIsNone(r["valid_through"])
        self.assertEqual(r["relations"], [])
        self.assertIsNone(r["applicability"]["min_units"])
        self.assertIn("could not be matched", r["applicability"]["other"])
        self.assertEqual(r["applicability"]["coverage_quotes"], [])
        self.assertTrue(r["warnings"])


if __name__ == "__main__":
    unittest.main()
