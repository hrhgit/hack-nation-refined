"""The change-test chain evaluation: the reference answers pass, and deliberate mistakes in each stage are caught. No model calls."""
import copy
import glob
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'eval/v2'))
from suite import Product, load
from chain import grade_chain, oracle_answers

OUT = ROOT / 'work' / 'out'


def stored(pid):
    files = sorted(glob.glob(str(OUT / ('AGENT_%s_*.jsonl' % pid))))
    return Path(files[-1]).read_text(encoding='utf-8') if files else None


def mutate(text, fn):
    rows = [json.loads(l) for l in text.splitlines() if l.strip()]
    for r in rows:
        if 'category' in r:
            fn(r)
    return '\n'.join(map(json.dumps, rows))


class ChainEval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product, cls.suite = Product(), load()
        cls.cases = {c['id']: c for c in cls.suite['cases'] if c.get('kind') == 'chain'}

    @classmethod
    def tearDownClass(cls):
        cls.product.close()

    def grade(self, cid, answers):
        return grade_chain(self.product, self.cases[cid], answers, self.suite['as_of'])

    def failed(self, g):
        return {i['check'] for i in g['issues'] if 'check' in i}

    def test_every_family_stays_in_one_split_and_real_chains_are_development(self):
        splits = {}
        for c in self.cases.values():
            self.assertEqual(splits.setdefault(c['group'], c['split']), c['split'])
            if c['origin'] == 'real_chain':
                self.assertEqual(c['split'], 'train')
        self.assertEqual({c['test']['test_id'] for c in self.cases.values() if c['origin'] == 'real_chain'}, {'T1', 'T2', 'T3', 'T4', 'T5'})

    def test_constructed_reference_answers_pass_and_empty_answers_fail(self):
        for cid, c in self.cases.items():
            if c['origin'] != 'synthetic_chain':
                continue
            with self.subTest(cid):
                good = self.grade(cid, oracle_answers(c))
                self.assertEqual(good['grade']['all_required'], 1, good['issues'])
                self.assertEqual(self.grade(cid, {})['grade']['all_required'], 0)

    def test_a_wrong_effective_date_or_missing_relation_is_caught(self):
        answers = oracle_answers(self.cases['CHAIN-RELATIVE-0'])
        pid = next(iter(answers))
        wrong = {pid: mutate(answers[pid], lambda r: r.update(effective_date='2026-11-01'))}
        g = self.grade('CHAIN-RELATIVE-0', wrong)           # the model's own wrong date is kept (only a warning), so the chain must notice it
        self.assertEqual(g['grade']['all_required'], 0)
        self.assertIn('rule_field', self.failed(g))
        pre = oracle_answers(self.cases['CHAIN-PREEMPT-0'])
        first = next(iter(pre))
        g = self.grade('CHAIN-PREEMPT-0', dict(pre, **{first: mutate(pre[first], lambda r: r.update(relations=[]))}))
        self.assertEqual(g['grade']['all_required'], 0)
        self.assertIn('conflicts', self.failed(g))

    def test_wrong_lifecycle_stops_or_fails_the_chain(self):
        pend = oracle_answers(self.cases['CHAIN-PENDING-0'])
        pid = next(iter(pend))
        g = self.grade('CHAIN-PENDING-0', {pid: mutate(pend[pid], lambda r: r.update(lifecycle='enacted'))})
        self.assertEqual(g['grade']['all_required'], 0)          # an enacted bill is not reported as pending
        failed = oracle_answers(self.cases['CHAIN-FAILED-0'])
        pid = next(iter(failed))
        g = self.grade('CHAIN-FAILED-0', {pid: mutate(failed[pid], lambda r: r.update(lifecycle='enacted'))})
        self.assertEqual(g['grade']['all_required'], 0)
        self.assertEqual(g['counts']['tracker_stopped'], 1)       # an applicable rent cap in MA stops the negative check

    def test_a_rule_with_the_wrong_city_is_caught_on_the_boundary(self):
        answers = oracle_answers(self.cases['CHAIN-BOUNDARY-0'])
        first = next(iter(answers))
        g = self.grade('CHAIN-BOUNDARY-0', dict(answers, **{first: mutate(answers[first], lambda r: r.update(jurisdiction='Jersey City, NJ'))}))
        self.assertEqual(g['grade']['all_required'], 0)

    @unittest.skipUnless(stored('D069-01') and stored('X101-01') and stored('D022-01'),
                         'the real extraction answers are not present here')
    def test_real_chains_pass_on_the_stored_real_answers_and_catch_mistakes(self):
        for cid in ('CHAIN-T1', 'CHAIN-T2', 'CHAIN-T3', 'CHAIN-T4', 'CHAIN-T5'):
            c = self.cases[cid]
            answers = {p: stored(p) for p in c['packets']}
            with self.subTest(cid):
                self.assertEqual(self.grade(cid, answers)['grade']['all_required'], 1)
        # FAIR act without its preemption sentence: no conflict flags
        a3 = {p: stored(p) for p in self.cases['CHAIN-T3']['packets']}
        a3['D069-01'] = mutate(a3['D069-01'], lambda r: r.update(relations=[]))
        self.assertEqual(self.grade('CHAIN-T3', a3)['grade']['all_required'], 0)
        # the court-struck measure recorded as enacted: the negative check must fail
        a5 = {'X101-01': mutate(stored('X101-01'), lambda r: r.update(lifecycle='enacted'))}
        self.assertEqual(self.grade('CHAIN-T5', a5)['grade']['all_required'], 0)
        # a missing packet answer: the rule behind the test is missing
        self.assertEqual(self.grade('CHAIN-T4', {})['grade']['all_required'], 0)


if __name__ == '__main__':
    unittest.main()
