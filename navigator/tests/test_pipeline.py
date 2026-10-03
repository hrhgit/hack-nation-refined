"""End-to-end test on a tiny invented corpus. Nothing here touches the real starter pack or outputs."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nav import schema as jschema  # noqa: E402
from nav.config import Paths, load_schema  # noqa: E402
from nav.corpus import add_extra_doc, load_corpus  # noqa: E402
from nav.ingest import pending_packets, run_ingest, write_outputs  # noqa: E402
from nav.packets import make_batches, prepare  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"

D100 = """SOURCE: https://example.org/cambridge-ordinance
RETRIEVED: 2026-10-03 12:00 UTC

ORDINANCE NO. 2026-17
Chapter 8.99 Security deposits and pricing software

Section 8.99.010 Security deposits.
A landlord shall not demand or receive a security deposit exceeding one month’s rent.
The landlord shall return the deposit within 30 days after the tenancy ends.

Section 8.99.020 Pricing software.
No landlord shall use an algorithmic device that analyzes nonpublic competitor rental data to set rents.
This Chapter shall take effect on January 1, 2027.
"""
D101 = """SOURCE: https://example.org/bill-h9999
RETRIEVED: 2026-10-03 12:00 UTC

H.9999 An Act relative to rent stabilization.
Section 1. A municipality may adopt rent control under this act.
Status: pending in committee.
"""
D102 = """SOURCE: https://example.org/law-firm-alert
RETRIEVED: 2026-10-03 12:00 UTC

Client alert. Cambridge has capped security deposits at one month’s rent under Chapter 8.99.
The cap takes effect on February 1, 2027, according to the council summary.
"""
MANIFEST = (
    "doc_id,jurisdictions,url,source_type,capture,retrieved_at,sha256,text_file,status\n"
    'D100,"Cambridge, MA",https://example.org/cambridge-ordinance,official,yes,2026-10-03 12:00 UTC,,text/D100.txt,ok\n'
    "D101,MA,https://example.org/bill-h9999,official,yes,2026-10-03 12:00 UTC,,text/D101.txt,ok\n"
    'D102,"Cambridge, MA",https://example.org/law-firm-alert,secondary (law firm / news / mirror),yes,2026-10-03 12:00 UTC,,text/D102.txt,ok\n'
    'D103,"Hoboken, NJ",https://ecode360.com/x,code publisher,check-terms,,,,check-terms\n'
)

APPL = {"built_on_or_before": None, "built_after": None, "date_basis": None, "min_units": None,
        "max_units": None, "owner_dependent": False, "other": None}


def rec(**kw):
    base = {"packet_id": "D100-01", "doc_id": "D100", "jurisdiction": "Cambridge, MA", "category": "security_deposits",
            "lifecycle": "enacted", "title": "Deposit cap", "requirement": "Deposits are capped at one month's rent.",
            "key_value": "1 month's rent", "coverage_conditions": "All rentals", "applicability": APPL,
            "exemptions": None, "penalty": None, "effective_date": "2027-01-01",
            "citation": "Cambridge Mun. Code § 8.99.010", "quoted_span": "x", "interaction": None,
            "confidence": 0.9, "conflict_flag": False, "conflict_note": None}
    base.update(kw)
    return base


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        pack = self.tmp / "pack"
        (pack / "corpus" / "text").mkdir(parents=True)
        (pack / "schema").mkdir()
        shutil.copy(FIX / "rule_record.schema.json", pack / "schema")
        (pack / "corpus" / "corpus_manifest.csv").write_text(MANIFEST, encoding="utf-8")
        for name, body in (("D100", D100), ("D101", D101), ("D102", D102)):
            (pack / "corpus" / "text" / (name + ".txt")).write_text(body, encoding="utf-8")
        self.paths = Paths(data_dir=pack, work_dir=self.tmp / "work", out_dir=self.tmp / "outputs",
                           extra_dir=self.tmp / "extra")
        self.index = prepare(self.paths, "2026-10-01")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def save(self, name, text, mtime):
        f = self.paths.inbox_dir / name
        f.write_text(text, encoding="utf-8")
        os.utime(f, (mtime, mtime))

    def first_answer(self):
        lines = ["Here is the JSON you asked for:", "```json"]
        # D100: one good record (straight apostrophe + collapsed line break), one paraphrase, one bad category
        lines.append(json.dumps(rec(quoted_span="A landlord shall not demand or receive a security deposit exceeding one month's rent.",
                                    jurisdiction="City of Cambridge, MA", effective_date="January 1, 2027")))
        lines.append(json.dumps(rec(category="algorithmic_rent_setting", title="Pricing software ban",
                                    citation="Cambridge Mun. Code § 8.99.020", key_value=None,
                                    quoted_span="Landlords may not use pricing programs that look at private competitor rents.")))
        lines.append(json.dumps(rec(category="rent-control", title="Bad", citation="Cambridge Mun. Code § 8.99.030",
                                    quoted_span="No landlord shall use an algorithmic device that analyzes nonpublic competitor rental data")))
        lines.append(json.dumps({"packet_id": "D100-01", "n_rules": 3, "note": None}))
        # D101: pending bill
        lines.append(json.dumps(rec(packet_id="D101-01", doc_id="D101", jurisdiction="MA", category="rent_increase_limits",
                                    lifecycle="pending_bill", title="H.9999 local rent control", key_value=None,
                                    effective_date=None, citation="H.9999",
                                    quoted_span="A municipality may adopt rent control under this act.")))
        lines.append(json.dumps({"packet_id": "D101-01", "n_rules": 1, "note": None}))
        # D102: secondary source with a different date, and no receipt (answer cut off)
        lines.append(json.dumps(rec(packet_id="D102-01", doc_id="D102", confidence=0.7, effective_date="2027-02-01",
                                    citation="Cambridge Rev. Ord. § 8.99.010",
                                    quoted_span="The cap takes effect on February 1, 2027, according to the council summary.")))
        lines.append("```")
        lines.append('{"packet_id":"D102-01","doc_id":"D102","category":"security_deposits","quoted_span":"cut o')
        return "\n".join(lines)

    def test_full_flow(self):
        self.assertEqual(sorted(self.index["packets"]), ["D100-01", "D101-01", "D102-01"])
        self.assertTrue(self.index["docs"]["D103"]["no_text"])
        self.assertIn("D103", (self.paths.work_dir / "COVERAGE_GAPS.md").read_text())

        self.save("answer1.txt", self.first_answer(), 1000)
        res = run_ingest(self.paths)

        self.assertEqual(res.counts["records_parsed"], 5)
        self.assertEqual(res.counts["accepted"], 3)
        self.assertEqual((res.counts["rejected"], res.counts["rejected_fixed"]), (2, 0))
        self.assertEqual(res.counts["rules"], 2)  # deposit rule merged across D100 + D102
        st = {p: s["state"] for p, s in res.states.items()}
        self.assertEqual(st, {"D100-01": "needs_fix", "D101-01": "done", "D102-01": "incomplete"})
        self.assertTrue(any("truncated" in p for _, p in res.parse_problems))

        reasons = " | ".join("; ".join(r["reasons"]) for r in res.rejected)
        self.assertIn("quoted_span not found", reasons)
        self.assertIn("category", reasons)

        by = {r["citation"]: r for r in res.rules}
        dep = by["Cambridge Mun. Code § 8.99.010"]
        self.assertEqual(dep["jurisdiction"], "Cambridge, MA")
        self.assertEqual(dep["effective_date"], "2027-01-01")
        self.assertEqual(dep["status"], "not_yet_effective")
        self.assertIn(dep["quoted_span"], D100)              # snapped to the source's own characters
        self.assertIn("’", dep["quoted_span"])
        self.assertTrue(dep["conflict_flag"])
        self.assertIn("Sources disagree", dep["conflict_note"])
        self.assertEqual(dep["merged_from"], 2)
        self.assertEqual(dep["source_doc_id"], "D100")        # official source wins over the law-firm alert
        bill = by["H.9999"]
        self.assertEqual((bill["status"], bill["level"], bill["effective_date"]), ("pending", "state", None))

        out = write_outputs(self.paths, res)
        data = json.loads((self.paths.out_dir / "rules.json").read_text())
        schema = load_schema(self.paths)
        self.assertEqual(len(data["rules"]), 2)
        for r in data["rules"]:
            self.assertEqual(jschema.check(r, schema), [])
            self.assertRegex(r["team_rule_id"], r"^r-\d{4}$")
        self.assertTrue((self.paths.work_dir / "report.md").exists())
        self.assertIn("Coverage matrix", (self.paths.work_dir / "report.md").read_text())

        # the paste files cover exactly the open packets and carry the problems back to the model
        pend = pending_packets(res)
        self.assertEqual(list(pend), ["D100-01", "D102-01"])
        names = make_batches(self.paths, pend)
        text = "\n".join((self.paths.paste_dir / n).read_text() for n in names)
        self.assertIn("CORRECTIONS NEEDED for packet D100-01", text)
        self.assertIn("quoted_span not found", text)
        self.assertIn("<<<PACKET D102-01>>>", text)
        self.assertNotIn("<<<PACKET D101-01>>>", text)
        self.assertIn("2026-10-01", text)
        # every batch names its own answer file and tells an agent to run the scripts itself
        self.assertIn("# DELIVERY", text)
        self.assertIn(str(self.paths.inbox_dir / names[0][:-3]) + ".jsonl", text)
        self.assertIn("python3 run.py ingest", text)
        # an answer file that already exists is never reused
        (self.paths.inbox_dir / (names[0][:-3] + ".jsonl")).write_text("{}")
        names2 = make_batches(self.paths, pend)
        self.assertIn(names[0][:-3] + "_r2.jsonl", (self.paths.paste_dir / names2[0]).read_text())

        # the as-of date is only used for derived status
        later = run_ingest(self.paths, "2027-03-01")
        self.assertEqual({r["citation"]: r["status"] for r in later.rules}["Cambridge Mun. Code § 8.99.010"], "in_force")

    def test_fixes_resolve_packets_and_ids_stay_stable(self):
        self.save("answer1.txt", self.first_answer(), 1000)
        before = {r["citation"]: r["team_rule_id"] for r in run_ingest(self.paths).rules}

        fix = [
            json.dumps(rec(category="algorithmic_rent_setting", title="Pricing software ban",
                           citation="Cambridge Mun. Code § 8.99.020", key_value=None,
                           quoted_span="No landlord shall use an algorithmic device that analyzes nonpublic competitor rental data to set rents.")),
            json.dumps({"packet_id": "D100-01", "n_rules": 1, "note": None}),
            json.dumps(rec(packet_id="D102-01", doc_id="D102", confidence=0.7, effective_date="2027-02-01",
                           citation="Cambridge Rev. Ord. § 8.99.010",
                           quoted_span="The cap takes effect on February 1, 2027, according to the council summary.")),
            json.dumps({"packet_id": "D102-01", "n_rules": 1, "note": None}),
        ]
        self.save("answer2.txt", "\n".join(fix), 2000)
        res = run_ingest(self.paths)
        self.assertEqual({p: s["state"] for p, s in res.states.items()},
                         {"D100-01": "done", "D101-01": "done", "D102-01": "done"})
        self.assertEqual(res.counts["rules"], 3)
        self.assertEqual((res.counts["rejected"], res.counts["rejected_fixed"]), (0, 2))  # fixed ones no longer count
        after = {r["citation"]: r["team_rule_id"] for r in res.rules}
        for cite, rid in before.items():
            self.assertEqual(after[cite], rid)
        self.assertEqual(pending_packets(res), {})

    def test_receipt_count_mismatch_and_wrong_doc(self):
        rows = [json.dumps(rec(quoted_span="A landlord shall not demand or receive a security deposit exceeding one month’s rent.")),
                json.dumps({"packet_id": "D100-01", "n_rules": 2, "note": None}),
                json.dumps(rec(packet_id="D101-01", doc_id="D100", jurisdiction="MA", category="rent_increase_limits",
                               quoted_span="A municipality may adopt rent control under this act.")),
                json.dumps({"packet_id": "D101-01", "n_rules": 1, "note": None})]
        self.save("a.txt", "\n".join(rows), 1000)
        res = run_ingest(self.paths)
        self.assertEqual(res.states["D100-01"]["state"], "mismatch")
        self.assertEqual(res.states["D101-01"]["state"], "needs_fix")
        self.assertTrue(any("does not match packet" in "; ".join(r["reasons"]) for r in res.rejected))

    def test_add_doc_for_new_ordinance(self):
        doc_id = add_extra_doc(self.paths, "Section 1. No landlord may charge a screening fee above $25 per applicant.\n",
                               "Cambridge, MA", "https://example.org/new")
        self.assertEqual(doc_id, "X001")
        docs = load_corpus(self.paths)
        self.assertEqual(docs["X001"].origin, "extra")
        self.assertTrue(docs["X001"].body.startswith("Section 1."))
        index = prepare(self.paths, "2026-10-01", only=["X001"])
        self.assertIn("X001-01", index["packets"])
        self.assertIn("D100-01", index["packets"])  # existing packets kept
        self.assertEqual(add_extra_doc(self.paths, "x", "Boston, MA", "u"), "X002")


if __name__ == "__main__":
    unittest.main()
