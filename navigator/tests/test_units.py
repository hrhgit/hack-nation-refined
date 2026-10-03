import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nav import facts, schema as jschema  # noqa: E402
from nav.config import KNOWN_JURISDICTIONS, STATE_NAMES  # noqa: E402
from nav.parse import classify, extract_json_objects  # noqa: E402
from nav.spans import DocIndex  # noqa: E402
from nav.textutil import Block, clean_text, select_blocks, split_blocks  # noqa: E402


class ParseTests(unittest.TestCase):
    def test_fences_prose_and_pretty_printing(self):
        text = 'Sure! Here you go:\n```json\n{"a": 1,\n "b": {"c": 2}}\n```\nand\n{"packet_id":"D1-01","n_rules":0,"note":null}\n'
        objs, probs = extract_json_objects(text)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0]["b"]["c"], 2)
        self.assertEqual(classify(objs[1]), "receipt")
        self.assertEqual(probs, [])

    def test_braces_inside_strings_and_trailing_comma(self):
        text = '{"category":"x","quoted_span":"a } b { c \\" d",}\n'
        objs, probs = extract_json_objects(text)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0]["quoted_span"], 'a } b { c " d')

    def test_truncated_answer_is_reported(self):
        text = '{"packet_id":"D1-01","n_rules":1}\n{"category":"security_deposits","title":"abc","quoted_span":"never fini'
        objs, probs = extract_json_objects(text)
        self.assertEqual(len(objs), 1)
        self.assertTrue(any("truncated" in p for p in probs))

    def test_stray_brace_in_prose_does_not_swallow_records(self):
        text = 'I used a {placeholder here.\n{"category":"security_deposits","quoted_span":"x y z"}\n'
        objs, _ = extract_json_objects(text)
        self.assertEqual([classify(o) for o in objs], ["record"])


class SpanTests(unittest.TestCase):
    BODY = ("Section 4. A landlord shall not demand or receive a security deposit\n"
            "exceeding one and one-half months’ rent. The landlord must return it\n"
            "within thirty days after the tenant vacates the premises, together with interest.\n"
            "Section 5. Nothing else matters here.")

    def setUp(self):
        self.ix = DocIndex(self.BODY)

    def test_exact_with_whitespace_and_quote_differences(self):
        m = self.ix.locate("A landlord shall not demand or receive a security deposit exceeding one and one-half months' rent.")
        self.assertIsNotNone(m)
        self.assertEqual(m.method, "exact")
        self.assertIn(m.text, self.BODY)
        self.assertTrue(m.text.endswith("rent."))
        self.assertIn("’", m.text)  # snapped to the source's own characters

    def test_ellipsis_spans_two_parts(self):
        m = self.ix.locate("A landlord shall not demand ... must return it within thirty days after the tenant vacates")
        self.assertIsNotNone(m)
        self.assertEqual(m.method, "ellipsis")
        self.assertTrue(m.text.startswith("A landlord"))

    def test_small_edit_is_fuzzy_but_accepted(self):
        m = self.ix.locate("The landlord must return it within thirty days after the tenant vacates the premises, together with all interest.")
        self.assertIsNotNone(m)
        self.assertEqual(m.method, "fuzzy")
        self.assertIn(m.text, self.BODY)

    def test_paraphrase_is_rejected(self):
        self.assertIsNone(self.ix.locate("Landlords can only take a deposit of at most 1.5 times the monthly rent amount."))

    def test_too_short(self):
        self.assertIsNone(self.ix.locate("rent"))


class FactTests(unittest.TestCase):
    def test_normalize_date(self):
        n = facts.normalize_date
        self.assertEqual(n("2026-01-01"), "2026-01-01")
        self.assertEqual(n("2026-01"), "2026-01")
        self.assertEqual(n("2026"), "2026")
        self.assertEqual(n("January 1, 2026"), "2026-01-01")
        self.assertEqual(n("1 Jan 2026"), "2026-01-01")
        self.assertEqual(n("7/1/2024"), "2024-07-01")
        self.assertEqual(n("Jul 2027"), "2027-07")
        self.assertIsNone(n("2026-13-40"))
        self.assertIsNone(n("next spring"))

    def test_status_matches_challenge_cases(self):
        d = facts.derive_status
        # T1: CA AB 325 effective 2026-01-01
        self.assertEqual(d("enacted", "2026-01-01", "2025-12-31"), "not_yet_effective")
        self.assertEqual(d("enacted", "2026-01-01", "2026-01-02"), "in_force")
        # T3: NJ FAIR Act effective 2027-07-01
        self.assertEqual(d("enacted", "2027-07-01", "2026-10-01"), "not_yet_effective")
        self.assertEqual(d("enacted", "2027-07-01", "2027-07-02"), "in_force")
        self.assertEqual(d("enacted", "2026-10-01", "2026-10-01"), "in_force")
        self.assertEqual(d("enacted", "2026-10", "2026-10-01"), "in_force")
        self.assertEqual(d("enacted", "2027", "2026-10-01"), "not_yet_effective")
        self.assertEqual(d("enacted", None, "2026-10-01"), "in_force")
        self.assertEqual(d("pending_bill", "2020-01-01", "2026-10-01"), "pending")  # T4
        self.assertEqual(d("failed", None, "2026-10-01"), "failed")                 # T5

    def test_doc_dates_and_numbers(self):
        text = "Effective July 1, 2024 the cap is one and one-half months. Fee of $1,500 plus 5 percent; see 7/1/2024 and 2026-01-01."
        dates = facts.doc_dates(text)
        for want in ("2024-07-01", "2024-07", "2024", "2026-01-01"):
            self.assertIn(want, dates)
        nums = facts.numbers_in(text)
        for want in ("1.5", "1500", "5"):
            self.assertIn(want, nums)
        self.assertEqual(facts.unsupported_numbers("1.5 months + 9%", nums), ["9"])

    def test_citations(self):
        self.assertEqual(facts.normalize_citation("Cal. Civ. Code section 1947.12(a)(1)"), "Cal. Civ. Code § 1947.12")
        self.assertEqual(facts.normalize_citation("G.L. c. 186, §15B"), "G.L. c. 186, § 15B")
        self.assertEqual(facts.normalize_citation("N.J.S.A. 2A:18-61.1"), "N.J.S.A. 2A:18-61.1")
        self.assertEqual(facts.citation_key("Cal. Civ. Code § 1947.12"), "1947.12")
        self.assertEqual(facts.citation_key("Civil Code section 1947.12 (AB 1482)"), "1947.12")
        self.assertEqual(facts.citation_key("G.L. c. 186, § 15B"), "15b|186")
        self.assertEqual(facts.citation_key("AB 325 (Cal. Bus. & Prof. Code § 16729)"), "325")

    def test_jurisdictions(self):
        n = lambda s: facts.normalize_jurisdiction(s, KNOWN_JURISDICTIONS, STATE_NAMES)
        self.assertEqual(n("California"), "CA")
        self.assertEqual(n("ca"), "CA")
        self.assertEqual(n("City and County of San Francisco, CA"), "San Francisco, CA")
        self.assertEqual(n("san francisco, ca"), "San Francisco, CA")
        self.assertEqual(n("Jersey City, New Jersey"), "Jersey City, NJ")
        self.assertEqual(n("Fresno, CA"), "Fresno, CA")
        self.assertIsNone(n("somewhere"))
        self.assertEqual(facts.level_of("CA"), "state")
        self.assertEqual(facts.level_of("Boston, MA"), "city")


class TextTests(unittest.TestCase):
    def test_nav_junk_removed_but_tables_and_sentences_kept(self):
        nav = "\n".join(["Home", "About", "News", "Contact", "Careers", "Events", "Maps", "Forms", "Login"])
        table = "Effective Period\nAmount of Increase\nMarch 1, 2026 - February 28, 2027\n1.6%\nMarch 1, 2025 - February 28, 2026\n1.4%\n1.7%\n1.9%\n2.0%"
        body = nav + "\nA landlord shall not charge more than the allowable amount.\n" + table + "\n"
        clean, rl, _ = clean_text(body)
        self.assertEqual(rl, 9)
        self.assertNotIn("Careers", clean)
        self.assertIn("[[omitted: page navigation]]", clean)
        self.assertIn("A landlord shall not charge", clean)
        self.assertIn("1.6%", clean)
        self.assertIn("Amount of Increase", clean)

    def test_very_long_lines_are_wrapped_without_losing_words(self):
        words = ["word%d" % i for i in range(600)]
        clean, _, _ = clean_text(" ".join(words) + "\nnext line\n")
        self.assertTrue(all(len(ln) <= 1200 for ln in clean.split("\n")))
        self.assertEqual(clean.split(), words + ["next", "line"])

    def test_cleaning_never_rewrites_characters(self):
        body = "Section 1.\nThe tenant’s deposit shall be returned.\n"
        clean, _, _ = clean_text(body)
        self.assertIn("tenant’s deposit shall", clean)

    def test_block_budget_drops_least_relevant_first(self):
        mk = lambda i, n, sc: Block(i, "x" * n, {"security_deposits": sc})
        blocks = [mk(0, 1000, 10), mk(1, 1000, 0), mk(2, 1000, 5), mk(3, 1000, 1)]
        self.assertEqual(select_blocks(blocks, 10000), [True] * 4)
        self.assertEqual(select_blocks(blocks, 2500), [True, False, True, False])

    def test_split_blocks_cuts_at_headings(self):
        body = "\n".join(["13.63.010 Findings"] + ["words " * 20] * 40 + ["13.63.020 Definitions"] + ["more " * 20] * 5)
        blocks = split_blocks(body)
        self.assertGreaterEqual(len(blocks), 2)
        self.assertTrue(any(b.text.startswith("13.63.020") for b in blocks))


class SchemaTests(unittest.TestCase):
    S = {"type": "object", "required": ["a"], "properties": {
        "a": {"type": "string", "minLength": 3}, "b": {"enum": ["x", "y"]},
        "c": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "d": {"type": ["string", "null"], "pattern": r"^\d{4}$"}}}

    def test_ok(self):
        self.assertEqual(jschema.check({"a": "abc", "b": "x", "c": None, "d": "2026"}, self.S), [])

    def test_errors(self):
        errs = jschema.check({"a": "ab", "b": "z", "c": 2, "d": "26"}, self.S)
        self.assertEqual(len(errs), 4)
        self.assertEqual(len(jschema.check({}, self.S)), 1)
        self.assertEqual(len(jschema.check({"a": 5}, self.S)), 1)


if __name__ == "__main__":
    unittest.main()
