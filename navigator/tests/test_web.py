import unittest

from lookup import LookupEngine
from lookup.common import DISCLAIMER
from web import server


class WebApiTest(unittest.TestCase):
    def test_lookup_matches_engine_and_carries_sources(self):
        engine = LookupEngine.from_files()
        payload = server.api_lookup({"address_id": ["A0001"], "as_of": ["2027-07-02"]})
        expected = engine.lookup("A0001", "2027-07-02")
        self.assertEqual(payload["as_of"], "2027-07-02")
        self.assertEqual(payload["disclaimer"], DISCLAIMER)
        self.assertEqual([(r["team_rule_id"], r["result"], r["explanation"], r["conflict_flag"]) for r in payload["results"]],
                         [(r["team_rule_id"], r["result"], r["explanation"], r["conflict_flag"]) for r in expected])
        for row in payload["results"]:
            self.assertTrue(row["steps"])
            self.assertTrue(all(s["doc_id"] and s["quoted_span"] for s in row["rule"]["sources"]))

    def test_entered_facts_are_reported_and_never_replace_file_data(self):
        missing = next(aid for aid, a in LookupEngine.from_files().addresses.items() if a["year_built"] is None)
        payload = server.api_lookup({"address_id": [missing], "year_built": ["1960"]})
        self.assertEqual(payload["entered_facts"], {"year_built": 1960})
        self.assertEqual(server.api_lookup({"address_id": [missing]})["entered_facts"], {})
        self.assertIsNone(LookupEngine.from_files().addresses[missing]["year_built"])

    def test_bad_input_is_refused(self):
        with self.assertRaises(ValueError):
            server.api_lookup({"address_id": ["A0001"], "as_of": ["next week"]})
        with self.assertRaises(ValueError):
            server.api_lookup({"address_id": ["A0001"], "units": ["many"]})
        with self.assertRaises(server.NotFound):
            server.api_lookup({"address_id": ["Z9999"]})
        with self.assertRaises(ValueError):
            server.api_source({"doc_id": ["../.env"], "quote": ["x"]})

    def test_every_quote_is_found_in_its_saved_text(self):
        for rule in server.api_rules({})["rules"]:
            for source in rule["sources"]:
                found = server.api_source({"doc_id": [source["doc_id"]], "quote": [source["quoted_span"]]})
                self.assertTrue(found["found"], "%s %s" % (rule["team_rule_id"], source["doc_id"]))

    def test_changes_agree_with_tracker(self):
        from changes import ChangeTracker
        output, _ = ChangeTracker(LookupEngine.from_files()).run()
        payload = server.api_changes({})
        self.assertEqual({item["test"]["test_id"]: item["output"] for item in payload["tests"]}, output)
        for item in payload["tests"]:
            # Cities in scope are listed even at zero, and together they account for every affected address.
            self.assertTrue(all(0 <= city["affected"] <= city["total"] for city in item["cities"]))
            self.assertEqual(sum(city["affected"] for city in item["cities"]), len(item["output"]["affected_address_ids"]))

    def test_pages_say_how_much_of_the_corpus_the_rules_cover(self):
        for payload in (server.api_lookup({"address_id": ["A0001"]}), server.api_rules({}), server.api_changes({})):
            progress = payload["extraction"]
            self.assertTrue(0 <= progress["done"] <= progress["total"])


if __name__ == "__main__":
    unittest.main()
