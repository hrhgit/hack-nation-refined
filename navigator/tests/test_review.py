"""The review table counts what each rule's conditions did to the addresses."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lookup.review import collect, render  # noqa: E402
from tests.test_stage23 import address, engine, rule  # noqa: E402


class ReviewTests(unittest.TestCase):
    def setUp(self):
        rows = {"old": address(year_built=1950), "new": address(year_built=2005), "other state": address("NJ", "Newark, NJ")}
        cutoff = rule("cut", applicability={"built_on_or_before": "1979-06-13", "date_basis": "certificate_of_occupancy",
                                            "coverage_quotes": ["units first certified after June 13, 1979 are exempt"], "contract": 2})
        everything = rule("owner", applicability={"owner_dependent": True, "contract": 2})
        self.engine = engine([cutoff, everything], rows)

    def test_counts_applied_omitted_and_out_of_scope(self):
        stats = collect(self.engine)
        self.assertEqual(stats["cut"]["applies"], 1)
        self.assertEqual(stats["cut"]["omitted: a condition excludes it"], 1)
        self.assertEqual(sum(stats["cut"].values()), 2)              # the New Jersey address is not in scope
        self.assertEqual(stats["owner"]["unknown"], 2)

    def test_table_flags_the_rules_a_person_should_check(self):
        text = render(self.engine)
        self.assertIn("条件使它在 1 个地址上消失", text)
        self.assertIn("所有 2 个地址都是不确定", text)
        self.assertIn("units first certified after June 13, 1979", text)
        self.assertLess(text.index("## 优先核对"), text.index("## 全部规则"))


if __name__ == "__main__":
    unittest.main()
