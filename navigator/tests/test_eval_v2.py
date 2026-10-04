"""Independent expected outcomes and deliberate bad answers; no external API calls."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'eval/v2'))
from suite import Product, load
from grading import grade

class EvalV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.product=Product();cls.suite=load()
    @classmethod
    def tearDownClass(cls):cls.product.close()
    def test_groups_and_duplicates_never_cross_splits(self):
        groups={}; hashes={}
        for c in self.suite['cases']:
            for index,key in [(groups,c['group']),(hashes,c['source_sha256'])]:
                self.assertEqual(index.setdefault(key,c['split']),c['split'])
            if c['origin'] not in ('synthetic','synthetic_chain'):self.assertEqual(c['split'],'train')
    def test_synthetic_oracles_pass_and_empty_answers_fail(self):
        # Validate reference answers without calling a model or exposing final model results.
        for c in self.suite['cases']:
            if c['origin']!='synthetic':continue
            with self.subTest(id=c['id']):
                good=grade(self.product,c,'\n'.join(map(json.dumps,c['oracle'])),self.suite['as_of'])
                self.assertEqual(good['grade']['all_required'],1,good)
                bad=grade(self.product,c,'',self.suite['as_of'])
                self.assertEqual(bad['grade']['all_required'],0,bad)
    def test_missing_rules_count_as_wrong_exclusions(self):
        c=next(c for c in self.suite['cases'] if c.get('group')=='size')
        g=grade(self.product,c,json.dumps({'packet_id':c['id'],'n_rules':0}),self.suite['as_of'])
        self.assertEqual(g['counts']['missing_rules'],1)
        self.assertEqual(g['counts']['wrong_exclusions'],3)
    def test_always_applies_and_always_unknown_cannot_pass(self):
        c=next(c for c in self.suite['cases'] if c.get('group')=='size')
        for conditions,metric in [([], 'false_applies'),([{'type':'owner','role':'exempt','who':'owner-occupied'}], 'unnecessary_unknown')]:
            answer=copy.deepcopy(c['oracle']);answer[0]['applicability']['conditions']=conditions
            g=grade(self.product,c,'\n'.join(map(json.dumps,answer)),self.suite['as_of'])
            self.assertEqual(g['grade']['all_required'],0)
            self.assertGreater(g['counts'][metric],0)
    def test_duplicate_and_false_quote_cannot_pass(self):
        c=next(c for c in self.suite['cases'] if c.get('group')=='size')
        duplicated=[c['oracle'][0],c['oracle'][0],{'packet_id':c['id'],'n_rules':2}]
        g=grade(self.product,c,'\n'.join(map(json.dumps,duplicated)),self.suite['as_of'])
        self.assertEqual(g['counts']['extra_rules'],1)
        broken=copy.deepcopy(c['oracle']);broken[0]['quoted_span']='Completely invented unsupported quotation about a different requirement.'
        g=grade(self.product,c,'\n'.join(map(json.dumps,broken)),self.suite['as_of'])
        self.assertEqual(g['grade']['all_required'],0)
        self.assertTrue(g['rejected'])

if __name__=='__main__':unittest.main()
