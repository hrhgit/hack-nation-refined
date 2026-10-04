"""Offline acceptance over every supplied address and the actual extracted laws."""
from __future__ import annotations

import contextlib
import csv
import hashlib
import io
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from changes import ChangeTracker
from lookup.addresses import CensusResolver, load_addresses
from lookup.cli import main
from lookup.common import DEFAULT_DATE, DISCLAIMER, PACK, read_json
from lookup.engine import LookupEngine, RESULTS
from nav.schema import check


class SampleAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load_addresses()
        cls.resolved = read_json(ROOT / "work" / "addresses_resolved.json")
        cls.engine = LookupEngine.from_files()
        cls.lookups, cls.audit = cls.engine.all()
        cls.changes, cls.change_audit = ChangeTracker(cls.engine).run()

    def test_all_500_addresses_and_all_emitted_rule_ids_are_valid(self):
        self.assertEqual(len(self.raw), 500)
        self.assertEqual(set(self.lookups["lookups"]), set(self.raw))
        rules = {r["team_rule_id"]: r for r in self.engine.rules}
        for aid, rows in self.lookups["lookups"].items():
            self.assertEqual(len(rows), len({r["team_rule_id"] for r in rows}))
            for result in rows:
                self.assertIn(result["result"], RESULTS)
                rule = rules[result["team_rule_id"]]
                self.assertNotIn(rule["lifecycle"], {"failed", "withdrawn"})
                self.assertIn(rule["citation"], result["explanation"])
                self.assertIn(DISCLAIMER, result["explanation"])

    def test_real_city_boundaries_and_neighborhoods(self):
        counts = Counter(r["legal_city"] for r in self.resolved.values())
        self.assertEqual(counts, {"Los Angeles, CA": 80, "San Francisco, CA": 80, "San Diego, CA": 50,
                                  "Berkeley, CA": 40, "Jersey City, NJ": 50, "Hoboken, NJ": 40, "Newark, NJ": 50,
                                  "Boston, MA": 60, "Cambridge, MA": 50})
        for aid, raw in self.raw.items():
            if raw["postal_city"] in {"Dorchester", "Roxbury", "East Boston", "Brighton", "Allston", "South Boston", "Jamaica Plain", "Hyde Park", "Mattapan"}:
                self.assertEqual(self.resolved[aid]["legal_city"], "Boston, MA")
            if raw["postal_city"] == "San Ysidro":
                self.assertEqual(self.resolved[aid]["legal_city"], "San Diego, CA")
            self.assertIn(self.resolved[aid]["resolved_by"], {"geocoder", "postal_city_fallback"})

    def test_all_census_evidence_can_be_replayed_offline(self):
        resolver = CensusResolver(offline=True)
        with patch.object(resolver, "_request", side_effect=AssertionError("Offline replay must not access a network")):
            self.assertEqual(resolver.resolve(self.raw), self.resolved)

    def test_actual_cutoff_year_rows_are_unknown(self):
        boundary_addresses = []
        for aid, address in self.resolved.items():
            if address["legal_city"] == "Los Angeles, CA" and address["year_built"] == 1978:
                boundary_addresses.append(aid)
                for row in self.lookups["lookups"][aid]:
                    rule = self.engine.by_id[row["team_rule_id"]]
                    if rule["jurisdiction"] == "Los Angeles, CA" and rule["category"] == "rent_increase_limits":
                        self.assertEqual(row["result"], "unknown")
                        self.assertIn("1978", row["explanation"])
        self.assertGreater(len(boundary_addresses), 0)
        # Sample has no San Francisco 1979 rows. Synthetic test covers the absent boundary.

    def test_missing_years_and_owner_dependent_results_have_reasons(self):
        for aid, address in self.resolved.items():
            rows = {r["team_rule_id"]: r for r in self.lookups["lookups"][aid]}
            for trace in self.audit["addresses"][aid]["rules"]:
                rule = self.engine.by_id[trace["team_rule_id"]]
                conditions = rule.get("applicability") or {}
                row = rows.get(rule["team_rule_id"])
                if not row:
                    continue
                if row["result"] == "applies" and conditions.get("owner_dependent"):
                    maximum = conditions.get("owner_exempt_if_units_at_most")
                    self.assertIsNotNone(maximum)
                    self.assertGreater(address["units"] if address.get("units") is not None else address["units_at_least"], maximum)
                if address["year_built"] is None and trace["stopped_at_step"] == 6 and (conditions.get("built_on_or_before") or conditions.get("built_after") or conditions.get("exempt_if_newer_than_years")):
                    self.assertEqual(row["result"], "unknown")
                    self.assertIn("no year built", row["explanation"])
                if row["result"] == "unknown":
                    self.assertTrue(trace["missing_facts"], (aid, rule["team_rule_id"]))

    def test_each_address_rule_has_an_audit_decision(self):
        for aid, address_audit in self.audit["addresses"].items():
            self.assertEqual({r["team_rule_id"] for r in address_audit["rules"]}, set(self.engine.by_id))
            for trace in address_audit["rules"]:
                self.assertIn(trace["stopped_at_step"], range(1, 9))
                self.assertTrue(trace["steps"])

    def test_actual_t1_t3_t4_and_negative_case(self):
        self.assertEqual(set(self.changes), {"T1", "T2", "T3", "T4", "T5"})
        for test_id, state in [("T1", "CA"), ("T3", "NJ"), ("T4", "MA")]:
            expected = sorted(aid for aid, address in self.resolved.items() if address["state"] == state)
            self.assertEqual(self.changes[test_id]["affected_address_ids"], expected)
        self.assertEqual(self.changes["T5"]["affected_address_ids"], [])
        # The supplied negative case is explicitly about its own query date.
        # Newly extracted laws may be in force on DEFAULT_DATE but not on T5's date.
        negative_date = self.change_audit["tests"]["T5"]["query_dates"]["as_of"]
        for aid, address in self.resolved.items():
            if address["state"] == "MA":
                for row in self.engine.lookup(aid, negative_date):
                    rule = self.engine.by_id[row["team_rule_id"]]
                    # a state rule that bars cities from regulating rent (Massachusetts c. 40P) is the opposite of a cap
                    bars_local = any(r.get("type") == "preempts_local" for r in rule.get("relations") or [])
                    self.assertFalse(row["result"] == "applies" and rule["category"] == "rent_increase_limits" and not bars_local)

    def test_missing_laws_are_explicit_and_supplied_dates_are_actually_used(self):
        for test_id, case in self.change_audit["tests"].items():
            if case["missing_rules"]:
                self.assertIn("Rules missing", self.changes[test_id]["notes"])
                for external_id in case["missing_rules"]:
                    self.assertIn(external_id, self.changes[test_id]["notes"])
        for test_id in ["T1", "T3"]:
            for aid, evidence in self.change_audit["tests"][test_id]["evidence"].items():
                self.assertTrue(any(result[0] == "not_yet_effective" for result in evidence["before"].values()))
                self.assertTrue(any(result[0] == "applies" for result in evidence["after"].values()))

    def test_exported_rule_schema_ids_dates_and_precedence(self):
        schema = read_json(PACK / "schema" / "rule_record.schema.json")
        exported = self.engine.exported_rules()
        ids = {r["team_rule_id"] for r in exported}
        for rule in exported:
            self.assertEqual(check(rule, schema), [], rule["team_rule_id"])
            self.assertTrue(set(rule["overrides"]).issubset(ids))
        ca = [r for r in exported if r["jurisdiction"] == "CA" and r["category"] == "algorithmic_rent_setting"]
        nj = [r for r in exported if r["jurisdiction"] == "NJ" and r["category"] == "algorithmic_rent_setting"]
        self.assertTrue(ca and nj)
        self.assertTrue(all(r["effective_date"] == "2026-01-01" for r in ca))
        self.assertTrue(all(r["effective_date"] == "2027-07-01" and r["status"] == "not_yet_effective" for r in nj))

    def test_two_complete_offline_builds_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)/"outputs"
            work = Path(directory)/"work"
            arguments = ["build", "--offline", "--output-dir", str(out), "--work-dir", str(work)]
            hashes = []
            with patch("urllib.request.urlopen", side_effect=AssertionError("build must be offline")), contextlib.redirect_stdout(io.StringIO()):
                for _ in range(2):
                    self.assertEqual(main(arguments), 0)
                    hashes.append({str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest() for path in Path(directory).rglob("*") if path.is_file()})
            self.assertEqual(hashes[0], hashes[1])

    def test_changed_building_fact_rejects_stale_resolved_file(self):
        with (PACK/"data"/"sample_addresses.csv").open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        rows[0]["year_built"] = "1930"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"addresses.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                main(["build", "--addresses", str(path)])
            self.assertEqual(raised.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
