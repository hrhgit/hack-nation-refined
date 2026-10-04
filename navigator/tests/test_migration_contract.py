"""The same contracts run before and after migration (MIGRATION_BACKEND=typescript).

Comparisons include every field, explanation, omission and reasoning step. Only
the measured HTTP execution time is excluded, because it is not deterministic.
"""
import json
import os
import subprocess
import unittest
from pathlib import Path

from migration.cases import cases
from migration.oracle import invoke, ROOT

class MigrationContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = os.environ.get("MIGRATION_BACKEND", "python")
        cls.process = None
        if cls.backend == "typescript":
            cls.process = subprocess.Popen(["node", str(ROOT / "dist" / "tests" / "migration" / "driver.js")],
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, cwd=ROOT)

    @classmethod
    def tearDownClass(cls):
        if cls.process:
            cls.process.stdin.close()
            cls.process.wait()
            cls.process.stdout.close()

    def check_case(self, case):
        expected = invoke(case)
        if self.process:
            self.process.stdin.write(json.dumps(case, ensure_ascii=False) + "\n")
            self.process.stdin.flush()
            line = self.process.stdout.readline()
            self.assertTrue(line, "TypeScript test driver exited before responding")
            actual = json.loads(line)
            self.assertEqual(actual, expected, case["name"])
        if "expect" in case:
            self.assertEqual(expected, case["expect"], case["name"])
        elif not case.get("error"):
            self.assertNotIn("error", expected, case["name"])

def add_tests():
    for case in cases():
        def test(self, case=case):
            self.check_case(case)
        setattr(MigrationContracts, "test_" + case["name"], test)
add_tests()

if __name__ == "__main__":
    unittest.main()
