"""Behavioral tests for coverage, time, city boundaries and law-change cases.

Synthetic laws isolate decisions from incomplete real extraction inputs.
Real-data acceptance is performed separately in test_stage23_acceptance.py.
"""
from __future__ import annotations

import copy
import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from changes import ChangeTracker
from lookup.addresses import CensusResolver, load_addresses, parse_batch, unit_lower_bound
from lookup.common import DISCLAIMER, date_interval, write_json
from lookup.engine import LookupEngine, load_rules


def rule(rid="state", jurisdiction="CA", category="rent_increase_limits", **fields):
    item = {"team_rule_id": rid, "jurisdiction": jurisdiction, "level": "state" if "," not in jurisdiction else "city",
            "category": category, "lifecycle": "enacted", "status": "in_force", "effective_date": None,
            "title": "Synthetic rule", "requirement": "Synthetic requirement", "citation": "Synthetic §1",
            "source_url": "https://example.test/source", "quoted_span": "An explicit synthetic rule for tests.",
            "retrieved": "2026-10-01 00:00 UTC", "applicability": {}}
    item.update(fields)
    return item


def address(state="CA", legal_city="Los Angeles, CA", **facts):
    item = {"state": state, "legal_city": legal_city, "resolved_by": "geocoder", "year_built": 1960,
            "units": 8, "units_at_least": None}
    item.update(facts)
    return item


def engine(rules, addresses=None, precedence=None, review=None):
    return LookupEngine(rules, addresses or {"A": address()}, precedence=precedence or [], review=review)


def open_question(**fields):
    item = {"category": "rent_increase_limits", "state": "CA", "state_rule": {"level": "state"}, "city_rule": {"level": "city"},
            "basis": "The state law bars conflicting local ordinances.", "source": "https://example.test/source#review"}
    item.update(fields)
    return item


def relationship(**fields):
    item = {"category": "rent_increase_limits", "state": "CA", "yielding": {"level": "state"},
            "prevailing": {"level": "city"}, "basis": "The state expressly yields to a lower city cap.",
            "source": "https://example.test/source#precedence"}
    item.update(fields)
    return item


class CoverageTests(unittest.TestCase):
    def test_wrong_state_and_city_are_omitted(self):
        self.assertEqual(engine([rule(jurisdiction="NJ")]).lookup("A"), [])
        self.assertEqual(engine([rule(jurisdiction="San Diego, CA")]).lookup("A"), [])

    def test_unresolved_city_is_unknown_for_same_state_only(self):
        e = engine([rule("ca", "Los Angeles, CA"), rule("nj", "Newark, NJ")], {"A": address(legal_city=None)})
        self.assertEqual([(r["team_rule_id"], r["result"]) for r in e.lookup("A")], [("ca", "unknown")])
        self.assertIn("legal city", e.lookup("A")[0]["explanation"])

    def test_successfully_resolved_unincorporated_address_omits_city_rules(self):
        e = engine([rule(jurisdiction="Los Angeles, CA")], {"A": address(legal_city=None, jurisdiction_known=True)})
        self.assertEqual(e.lookup("A"), [])

    def test_failed_and_withdrawn_are_never_emitted_even_when_city_unknown(self):
        for lifecycle in ["failed", "withdrawn"]:
            for city in ["Los Angeles, CA", None]:
                e = engine([rule(jurisdiction="Los Angeles, CA", lifecycle=lifecycle)], {"A": address(legal_city=city)})
                self.assertEqual(e.lookup("A"), [])

    def test_pending_and_future_effective_stop_before_property_tests(self):
        for lifecycle, date, expected in [("pending_bill", None, "pending"), ("enacted", "2027-07-01", "not_yet_effective")]:
            e = engine([rule(lifecycle=lifecycle, effective_date=date, applicability={"min_units": 100})])
            self.assertEqual(e.lookup("A")[0]["result"], expected)

    def test_status_snapshot_is_ignored_and_effective_day_is_inclusive(self):
        e = engine([rule(status="pending", effective_date="2026-01-01")])
        self.assertEqual(e.lookup("A", "2025-12-31")[0]["result"], "not_yet_effective")
        self.assertEqual(e.lookup("A", "2026-01-01")[0]["result"], "applies")

    def test_missing_enactment_fact_is_unknown_not_guessed_from_status(self):
        e = engine([rule(lifecycle=None)])
        self.assertEqual(e.lookup("A")[0]["result"], "unknown")
        self.assertIn("whether the measure was enacted", e.lookup("A")[0]["explanation"])

    def test_missing_effective_date_is_explained(self):
        self.assertIn("states no effective date", engine([rule()]).lookup("A")[0]["explanation"])

    def test_partial_effective_date_is_not_assigned_an_invented_day(self):
        e = engine([rule(effective_date="2026-03")])
        self.assertEqual(e.lookup("A", "2026-02-28")[0]["result"], "not_yet_effective")
        self.assertEqual(e.lookup("A", "2026-03-15")[0]["result"], "unknown")
        self.assertEqual(e.lookup("A", "2026-03-31")[0]["result"], "applies")
        self.assertEqual(date_interval("2024-02")[1].day, 29)

    def test_invalid_date_and_duplicate_rule_fail(self):
        with self.assertRaises(ValueError):
            engine([rule(), rule()])
        with self.assertRaises(ValueError):
            engine([rule(effective_date="2026-02-30")])
        with self.assertRaises(ValueError):
            engine([rule()]).lookup("A", "2026-1-1")

    def test_malformed_property_facts_and_rule_geography_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "year_built"):
            engine([rule()], {"A": address(year_built="1960")})
        with self.assertRaisesRegex(ValueError, "级别"):
            engine([rule(level="city")])
        with self.assertRaisesRegex(ValueError, "team_rule_id"):
            engine([rule(rid=None)])

    def test_certificate_cutoff_years_earlier_same_later(self):
        for cutoff in ["1979-06-13", "1978-10-01"]:
            year = int(cutoff[:4])
            e = engine([rule(applicability={"built_on_or_before": cutoff, "date_basis": "certificate_of_occupancy"})],
                       {"early": address(year_built=year-1), "boundary": address(year_built=year), "late": address(year_built=year+1)})
            self.assertEqual(e.lookup("early")[0]["result"], "applies")
            self.assertEqual(e.lookup("boundary")[0]["result"], "unknown")
            self.assertEqual(e.lookup("late"), [])

    def test_exact_certificate_date_resolves_year_boundary(self):
        e = engine([rule(applicability={"built_on_or_before": "1979-06-13", "date_basis": "certificate_of_occupancy"})],
                   {"A": address(year_built=1979, certificate_of_occupancy="1979-06-13")})
        self.assertEqual(e.lookup("A")[0]["result"], "applies")

    def test_built_after_is_strict_and_missing_year_is_unknown(self):
        e = engine([rule(applicability={"built_after": "2000-01-01", "date_basis": "construction_date"})],
                   {"same": address(construction_date="2000-01-01"), "after": address(construction_date="2000-01-02"), "missing": address(year_built=None)})
        self.assertEqual(e.lookup("same"), [])
        self.assertEqual(e.lookup("after")[0]["result"], "applies")
        self.assertIn("no year built", e.lookup("missing")[0]["explanation"])

    def test_rolling_cutoff_recomputed_and_handles_leap_day(self):
        e = engine([rule(applicability={"exempt_if_newer_than_years": 15, "date_basis": "certificate_of_occupancy"})], {"A": address(year_built=2011)})
        self.assertEqual(e.lookup("A", "2025-10-01"), [])
        self.assertEqual(e.lookup("A", "2026-10-01")[0]["result"], "unknown")
        self.assertEqual(e.lookup("A", "2027-10-01")[0]["result"], "applies")
        e.lookup("A", "2028-02-29")

    def test_exact_units_and_lower_bounds_do_not_overclaim(self):
        minimum = rule(applicability={"min_units": 5})
        maximum = rule(applicability={"max_units": 4})
        rows = {"5plus": address(units=None, units_at_least=5), "3plus": address(units=None, units_at_least=3), "missing": address(units=None)}
        self.assertEqual(engine([minimum], rows).lookup("5plus")[0]["result"], "applies")
        self.assertEqual(engine([maximum], rows).lookup("5plus"), [])
        self.assertEqual(engine([minimum], rows).lookup("3plus")[0]["result"], "unknown")
        self.assertEqual(engine([maximum], rows).lookup("3plus")[0]["result"], "unknown")
        self.assertEqual(engine([minimum], rows).lookup("missing")[0]["result"], "unknown")

    def test_owner_identity_only_resolved_by_explicit_impossible_exception(self):
        unconditional = rule(applicability={"owner_dependent": True})
        small_owner = rule(applicability={"owner_dependent": True, "owner_exempt_if_units_at_most": 4})
        self.assertEqual(engine([unconditional]).lookup("A")[0]["result"], "unknown")
        self.assertEqual(engine([small_owner]).lookup("A")[0]["result"], "applies")
        self.assertEqual(engine([small_owner], {"A": address(units=None, units_at_least=4)}).lookup("A")[0]["result"], "unknown")

    def test_known_exclusion_wins_over_missing_owner(self):
        self.assertEqual(engine([rule(applicability={"min_units": 9, "owner_dependent": True})]).lookup("A"), [])

    def test_other_condition_remains_unknown_and_is_quoted(self):
        row = engine([rule(applicability={"other": "The tenant receives a subsidy."})]).lookup("A")[0]
        self.assertEqual(row["result"], "unknown")
        self.assertIn("The tenant receives a subsidy.", row["explanation"])

    def test_expired_numeric_period_not_used_on_later_date(self):
        self.assertEqual(engine([rule(valid_through="2026-06-30")]).lookup("A", "2026-10-01"), [])

    def test_explanation_has_citation_retrieval_and_disclaimer(self):
        dated_rule = rule(effective_date="2026-01-01", date_source="override test", overrides_applied=[{"source": "Dated approval document", "after": {"effective_date": "2026-01-01"}}])
        e = engine([dated_rule])
        row = e.lookup("A")[0]
        for text in ["Synthetic §1", "2026-10-01 00:00 UTC", "https://example.test/source", DISCLAIMER, "Dated approval document"]:
            self.assertIn(text, row["explanation"])
        self.assertEqual(e.evaluate("A")[1]["rules"][0]["source"]["fact_corrections"], dated_rule["overrides_applied"])
        self.assertEqual(e.exported_rules()[0]["date_source"], "override test")


class PrecedenceAndAuditTests(unittest.TestCase):
    def test_applicable_city_supersedes_state_and_export_direction(self):
        e = engine([rule(), rule("city", "Los Angeles, CA")], precedence=[relationship()])
        results = {r["team_rule_id"]: r for r in e.lookup("A")}
        self.assertEqual(results["state"]["result"], "superseded")
        self.assertFalse(results["state"]["conflict_flag"])
        exported = {r["team_rule_id"]: r for r in e.exported_rules()}
        self.assertEqual(exported["city"]["overrides"], ["state"])
        self.assertEqual(exported["state"]["overrides"], [])

    def test_uncertain_city_makes_state_unknown_but_future_city_does_not(self):
        e = engine([rule(), rule("city", "Los Angeles, CA", applicability={"owner_dependent": True})], precedence=[relationship()])
        results = {r["team_rule_id"]: r for r in e.lookup("A")}
        self.assertEqual(results["state"]["result"], "unknown")
        e = engine([rule(), rule("city", "Los Angeles, CA", effective_date="2027-01-01")], precedence=[relationship()])
        self.assertEqual(next(r for r in e.lookup("A") if r["team_rule_id"] == "state")["result"], "applies")

    def test_unknown_state_coverage_not_claimed_superseded(self):
        e = engine([rule(applicability={"owner_dependent": True}), rule("city", "Los Angeles, CA")], precedence=[relationship()])
        self.assertEqual(next(r for r in e.lookup("A") if r["team_rule_id"] == "state")["result"], "unknown")

    def test_false_extractor_flags_ignored_conflict_includes_future_enacted_rule(self):
        e = engine([rule(conflict_flag=True)])
        self.assertFalse(e.lookup("A")[0]["conflict_flag"])
        pair = [rule(effective_date="2027-01-01", conflict_flag=False), rule("city", "Los Angeles, CA", conflict_flag=False)]
        e = engine(pair, review=[open_question()])
        self.assertTrue(all(row["conflict_flag"] for row in e.lookup("A")))
        self.assertIn("human review", e.lookup("A")[0]["explanation"])
        self.assertEqual(e.evaluate("A")[1]["conflict_pairs"], [["state", "city"]])
        # A state rule and a city rule in one category are not flagged unless a sourced open question names them.
        self.assertFalse(any(row["conflict_flag"] for row in engine(pair, review=[]).lookup("A")))
        self.assertFalse(any(row["conflict_flag"] for row in engine(pair, review=[open_question(state_rule={"citation_contains": "Other"})]).lookup("A")))
        with self.assertRaisesRegex(ValueError, "依据"):
            engine(pair, review=[open_question(basis="")])

    def test_strict_before_and_on_or_after_cutoffs(self):
        before = rule(applicability={"built_before": "1980", "date_basis": "certificate_of_occupancy"})
        rows = {"y1979": address(year_built=1979), "y1980": address(year_built=1980), "y1981": address(year_built=1981), "none": address(year_built=None)}
        got = {k: engine([before], {k: v}).lookup(k) for k, v in rows.items()}
        self.assertEqual(got["y1979"][0]["result"], "applies")
        self.assertEqual(got["y1980"][0]["result"], "unknown")      # the cutoff year is never decided from a year alone
        self.assertEqual(got["y1981"], [])
        self.assertEqual(got["none"][0]["result"], "unknown")
        after = rule(applicability={"built_on_or_after": "1995-02-01", "date_basis": "construction_date"})
        self.assertEqual(engine([after], {"A": address(year_built=1996)}).lookup("A")[0]["result"], "applies")
        self.assertEqual(engine([after], {"A": address(year_built=1994)}).lookup("A"), [])
        self.assertEqual(engine([after], {"A": address(year_built=1995)}).lookup("A")[0]["result"], "unknown")

    def test_filing_dependent_exemption_is_open_inside_its_reach_and_irrelevant_outside(self):
        deferred = [{"flats": {"exempt_if_newer_than_years": 30, "date_basis": "construction_date"}, "note": "built within the last 30 years"}]
        r = rule(applicability={"deferred": deferred, "contract": 2})
        new = engine([r], {"A": address(year_built=2015)}).lookup("A")[0]
        self.assertEqual(new["result"], "unknown")                           # never "excluded": the data cannot show a filing
        self.assertIn("filed or registered", new["explanation"])
        self.assertEqual(engine([r], {"A": address(year_built=1950)}).lookup("A")[0]["result"], "applies")
        self.assertEqual(engine([r], {"A": address(year_built=None)}).lookup("A")[0]["result"], "unknown")
        units = rule(applicability={"deferred": [{"flats": {"min_units": 5}, "note": "four or fewer units"}], "contract": 2})
        self.assertEqual(engine([units], {"A": address(units=3)}).lookup("A")[0]["result"], "unknown")
        self.assertEqual(engine([units], {"A": address(units=8)}).lookup("A")[0]["result"], "applies")
        # a real exclusion still wins over an open question
        both = rule(applicability={"deferred": deferred, "min_units": 10, "contract": 2})
        self.assertEqual(engine([both], {"A": address(year_built=2015, units=4)}).lookup("A"), [])

    def test_new_format_other_is_unresolved_even_without_keywords_and_per_tenancy_is_a_note(self):
        row = engine([rule(applicability={"other": "any housing accommodation", "contract": 2})]).lookup("A")[0]
        self.assertEqual(row["result"], "unknown")
        row = engine([rule(applicability={"per_tenancy": "when the lease began", "contract": 2})]).lookup("A")[0]
        self.assertEqual(row["result"], "applies")
        self.assertIn("when the lease began", row["explanation"])

    def test_trigger_condition_is_quoted_but_does_not_make_coverage_unknown(self):
        row = engine([rule(applicability={"other": "Temporary displacement for less than 20 days"})]).lookup("A")[0]
        self.assertEqual(row["result"], "applies")
        self.assertIn("Temporary displacement for less than 20 days", row["explanation"])
        row = engine([rule(applicability={"other": "Excludes housing produced in the last 15 years"})]).lookup("A")[0]
        self.assertEqual(row["result"], "unknown")
        row = engine([rule(applicability={"other": "any housing accommodation", "other_kind": "building"})]).lookup("A")[0]
        self.assertEqual(row["result"], "unknown")

    def test_pending_rule_and_different_category_do_not_conflict(self):
        for city in [rule("city", "Los Angeles, CA", lifecycle="pending_bill"), rule("city", "Los Angeles, CA", category="security_deposits")]:
            self.assertFalse(any(row["conflict_flag"] for row in engine([rule(), city], review=[open_question()]).lookup("A")))

    def test_precedence_without_source_and_cycles_are_rejected(self):
        for declarations in [[relationship(source="")], [relationship(), relationship(yielding={"level": "city"}, prevailing={"level": "state"})]]:
            with self.assertRaises(ValueError):
                engine([rule(), rule("city", "Los Angeles, CA")], precedence=declarations)

    def test_audit_records_omitted_rules_and_missing_facts(self):
        e = engine([rule("omitted", "NJ"), rule("unknown", applicability={"owner_dependent": True}), rule("passed")])
        _, audit = e.evaluate("A")
        traces = {t["team_rule_id"]: t for t in audit["rules"]}
        self.assertEqual(traces["omitted"]["stopped_at_step"], 1)
        self.assertEqual(traces["unknown"]["stopped_at_step"], 6)
        self.assertEqual(traces["unknown"]["missing_facts"][0]["field"], "owner_dependent")
        self.assertEqual([s["step"] for s in traces["passed"]["steps"]], list(range(1, 9)))

    def test_output_order_deterministic_with_shuffled_inputs(self):
        rules = [rule("z"), rule("a", lifecycle="pending_bill")]
        rows = {"B": address(), "A": address()}
        first = engine(rules, rows).all()
        second = engine(list(reversed(rules)), dict(reversed(list(rows.items())))).all()
        self.assertEqual(json.dumps(first, ensure_ascii=False), json.dumps(second, ensure_ascii=False))


class ChangeTests(unittest.TestCase):
    def setUp(self):
        self.rows = {"CA": address(), "H": address("NJ", "Hoboken, NJ"), "J": address("NJ", "Jersey City, NJ"),
                     "N": address("NJ", "Newark, NJ"), "B": address("MA", "Boston, MA"), "C": address("MA", "Cambridge, MA")}
        self.rules = [rule("ca-new-id", category="algorithmic_rent_setting", citation="AB 325", effective_date="2026-01-01"),
                      rule("nj-new-id", "NJ", "algorithmic_rent_setting", citation="P.L. 2026, c.43 §4", effective_date="2027-07-01",
                           relations=[{"type": "preempts_local", "quote": "A municipality shall be prohibited from enacting an ordinance that conflicts with this act."}]),
                      rule("hob-new-id", "Hoboken, NJ", "algorithmic_rent_setting", citation="Chapter 192 algorithmic rents"),
                      rule("jc-new-id", "Jersey City, NJ", "algorithmic_rent_setting", citation="§218 algorithmic rents"),
                      rule("h", "MA", "algorithmic_rent_setting", citation="H.5222", lifecycle="pending_bill"),
                      rule("s", "MA", "algorithmic_rent_setting", citation="S.2983", lifecycle="pending_bill"),
                      rule("ballot", "MA", citation="IP 25-21", lifecycle="failed")]

    def test_all_five_cases_use_coverage_and_actual_date_results(self):
        results, audit = ChangeTracker(engine(self.rules, self.rows)).run()
        self.assertEqual(results["T1"]["affected_address_ids"], ["CA"])
        self.assertEqual(results["T2"]["affected_address_ids"], ["H", "J"])
        self.assertIn("Hoboken, NJ 1", results["T2"]["notes"])
        self.assertEqual(results["T3"]["affected_address_ids"], ["H", "J", "N"])
        self.assertEqual(results["T3"]["conflict_flag_address_ids"], ["H", "J"])
        self.assertEqual(results["T4"]["affected_address_ids"], ["B", "C"])
        self.assertEqual(results["T5"]["affected_address_ids"], [])
        self.assertEqual(audit["tests"]["T1"]["rule_mapping"]["CA-ALG-01"], ["ca-new-id"])
        self.assertEqual(audit["tests"]["T1"]["evidence"]["CA"]["before"]["ca-new-id"][0], "not_yet_effective")

    def test_changed_dates_and_coverage_change_affected_sets(self):
        tracker = ChangeTracker(engine(self.rules, self.rows))
        results, _ = tracker.run({"T1": {"as_of_before": "2026-01-02"}, "T3": {"as_of_before": "2027-07-02"}})
        self.assertEqual(results["T1"]["affected_address_ids"], [])
        self.assertEqual(results["T3"]["affected_address_ids"], [])
        self.rules[0]["applicability"] = {"min_units": 100}
        results, audit = ChangeTracker(engine(self.rules, self.rows)).run()
        self.assertNotIn("ca-new-id", audit["tests"]["T1"]["evidence"]["CA"]["after"])

    def test_missing_rules_reported_without_fabricated_cities_or_conflicts(self):
        self.rules = [r for r in self.rules if r["team_rule_id"] not in {"hob-new-id", "jc-new-id", "ballot"}]
        results, audit = ChangeTracker(engine(self.rules, self.rows)).run()
        self.assertEqual(results["T2"]["affected_address_ids"], [])
        self.assertIn("Rules missing", results["T2"]["notes"])
        self.assertEqual(results["T3"]["conflict_flag_address_ids"], [])
        self.assertIn("MA-RENT-P1", audit["tests"]["T5"]["missing_rules"])

    def test_negative_case_rejects_applied_ma_rent_cap(self):
        self.rules.append(rule("bad-cap", "MA"))
        with self.assertRaisesRegex(ValueError, "涨租上限"):
            ChangeTracker(engine(self.rules, self.rows)).run()

    def test_known_precedence_suppresses_only_that_conflict_pair(self):
        rel = relationship(category="algorithmic_rent_setting", state="NJ", yielding={"jurisdiction": "NJ"}, prevailing={"jurisdiction": "Hoboken, NJ"})
        results, _ = ChangeTracker(engine(self.rules, self.rows, [rel])).run()
        self.assertEqual(results["T3"]["conflict_flag_address_ids"], ["J"])

    def test_unrelated_conflict_does_not_flag_named_change_pair(self):
        self.rules.append(rule("other-state", "NJ", "algorithmic_rent_setting", citation="Other statute"))
        rel = relationship(category="algorithmic_rent_setting", state="NJ", yielding={"citation_contains": "P.L. 2026"}, prevailing={"level": "city"})
        results, _ = ChangeTracker(engine(self.rules, self.rows, [rel])).run()
        self.assertEqual(results["T3"]["conflict_flag_address_ids"], [])

    def test_unused_date_override_rejected_instead_of_silently_ignored(self):
        with self.assertRaisesRegex(ValueError, "实际使用"):
            ChangeTracker(engine(self.rules, self.rows)).run({"T1": {"as_of": "2027-01-01"}})


class SupplementReportTests(unittest.TestCase):
    def test_unused_and_overriding_supplements_are_reported(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "rules.json"
            path.write_text(json.dumps([rule("r1", applicability={"min_units": 3, "built_on_or_before": "1980"})]))
            supplements = [
                {"id": "hit", "match": {"jurisdiction": "CA"}, "applicability": {"min_units": 5, "built_on_or_before": "1980"}, "basis": "b", "source": "s"},
                {"id": "miss", "match": {"jurisdiction": "NJ"}, "applicability": {"min_units": 1}, "basis": "b", "source": "s"}]
            report = {}
            rules = load_rules(path, supplements, report)
            self.assertEqual(report["unused"], ["miss"])
            self.assertEqual([(x["field"], x["extracted"], x["supplement_value"]) for x in report["differs"]], [("min_units", 3, 5)])
            self.assertEqual(rules[0]["applicability"]["min_units"], 5)


class AddressResolutionTests(unittest.TestCase):
    def test_explicit_unit_descriptions_and_ambiguous_building_codes(self):
        for text, expected in [("Five or more apartments", 5), ("Apartment 5 to 14 Units", 5), ("4-8-UNIT-APT", 4),
                               ("APT 7-30 UNITS", 7), (">8-UNIT-APT", 9), ("SANDAG asr_landuse 14-16 (5+ units)", 5),
                               ("Apartment 15 Units or more", 15), ("3S-F-D-6U-NH", 6), ("3B-7U/4B-24U-G", 7), ("3SB", None), ("SUBSD HOUSING S- 8", None)]:
            self.assertEqual(unit_lower_bound(text), expected, text)

    def test_batch_parser_checks_complete_ids_and_coordinates(self):
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["A", "input", "Match", "Exact", "matched", "-118.3,34.1", "line", "L"])
        writer.writerow(["B", "input", "No_Match"])
        parsed = parse_batch(buffer.getvalue(), {"A", "B"})
        self.assertEqual(parsed["A"]["longitude"], -118.3)
        self.assertFalse(parsed["B"]["matched"])
        with self.assertRaises(ValueError):
            parse_batch(buffer.getvalue(), {"A", "B", "C"})
        with self.assertRaises(ValueError):
            parse_batch(buffer.getvalue() + buffer.getvalue(), {"A", "B"})
        with self.assertRaises(ValueError):
            parse_batch("<html>Request Rejected</html>", {"A"})

    def test_census_boundary_wins_over_mailing_city_and_wrong_state_not_used(self):
        rows = {"A": {"address_id": "A", "state": "CA", "postal_city": "Los Angeles"},
                "B": {"address_id": "B", "state": "CA", "postal_city": "San Ysidro"}}
        def result(row):
            return {"matched": True}, [{"STATE": "06" if row["address_id"] == "A" else "34", "NAME": "San Diego city", "GEOID": "0666000", "BASENAME": "San Diego"}]
        with patch.object(CensusResolver, "_address", side_effect=result):
            parsed = CensusResolver().resolve(rows)
        self.assertEqual(parsed["A"]["legal_city"], "San Diego, CA")
        self.assertEqual(parsed["A"]["resolved_by"], "geocoder")
        self.assertEqual(parsed["B"]["resolved_by"], "postal_city_fallback")

    def test_no_match_alias_and_unresolved_are_explicit(self):
        rows = {"A": {"address_id": "A", "state": "MA", "postal_city": "Dorchester"},
                "B": {"address_id": "B", "state": "MA", "postal_city": "Unknown Town"}}
        with patch.object(CensusResolver, "_address", return_value=({"matched": False}, [])):
            parsed = CensusResolver().resolve(rows)
        self.assertEqual(parsed["A"]["legal_city"], "Boston, MA")
        self.assertEqual(parsed["A"]["resolved_by"], "postal_city_fallback")
        self.assertEqual(parsed["B"]["resolved_by"], "unresolved")

    def test_cached_resolver_runs_offline_and_changed_address_requires_new_cache(self):
        row = {"address_id": "A", "street_address": "1 Main St", "postal_city": "Boston", "state": "MA", "zip": "02101"}
        raw = {"result": {"addressMatches": [{"matchedAddress": "1 MAIN ST", "coordinates": {"x": -71, "y": 42},
                                               "geographies": {"Incorporated Places": [{"STATE": "25", "NAME": "Boston city", "GEOID": "2507000"}]}}]}}
        with tempfile.TemporaryDirectory() as directory:
            resolver = CensusResolver(directory)
            with patch.object(resolver, "_request", return_value=json.dumps(raw)):
                original = resolver.resolve({"A": row})
            offline = CensusResolver(directory, offline=True)
            with patch.object(offline, "_request", side_effect=AssertionError("network forbidden")):
                self.assertEqual(offline.resolve({"A": row}), original)
                with self.assertRaisesRegex(ValueError, "缓存"):
                    offline.resolve({"A": dict(row, street_address="2 Main St")})

    def test_duplicate_input_address_ids_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"addresses.csv"
            path.write_text("address_id,year_built,units\nA,1960,5\nA,1961,6\n")
            with self.assertRaises(ValueError):
                load_addresses(path)


if __name__ == "__main__":
    unittest.main()
