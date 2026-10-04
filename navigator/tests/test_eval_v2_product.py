"""Independent synthetic end states through shipped ingest/merge/lookup, plus real HTTP checks."""
import copy
import json
import re
import subprocess
import sys
import unittest
import urllib.parse
import urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'eval/v2'))
from suite import Product,load


def rule(rid,jurisdiction='CA',**kw):
    return dict(team_rule_id=rid,jurisdiction=jurisdiction,level='city' if ',' in jurisdiction else 'state',category='rent_increase_limits',
                lifecycle='enacted',citation='Invented §'+rid,requirement='Synthetic test requirement',quoted_span='This is an invented test rule, not a real law.',
                source_url='https://example.test/'+rid,applicability={},**kw)


class ProductOutcomes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.product=Product()
    @classmethod
    def tearDownClass(cls):cls.product.close()
    def engine(self,rules,day='2026-10-01',**kw):
        return self.product.call(op='engine',rules=rules,addresses={'P':dict(state='CA',legal_city='Los Angeles, CA',units=10,year_built=1960)},as_of=day,**kw)[0]['lookups']['P']
    def test_old_rule_expires_as_new_rule_takes_effect(self):
        rules=[rule('old',valid_through='2026-10-01'),rule('new',effective_date='2026-10-02')]
        before=self.engine(rules);after=self.engine(rules,'2026-10-02')
        self.assertEqual({r['team_rule_id']:r['result'] for r in before},{'old':'applies','new':'not_yet_effective'})
        self.assertEqual({r['team_rule_id']:r['result'] for r in after},{'new':'applies'})
        self.assertIn('Invented §new',after[0]['explanation'])
        self.assertNotIn('Invented §old',after[0]['explanation'])
    def test_city_override_is_conditional_on_city_coverage(self):
        rules=[rule('state'),rule('city','Los Angeles, CA')];rules[1]['applicability']={'min_units':12}
        edge={'category':'rent_increase_limits','state':'CA','yielding':{'level':'state'},'prevailing':{'level':'city'},'basis':'Synthetic state clause yields to city rule.','source':'https://example.test/precedence'}
        before=self.engine(rules,precedence=[edge])
        self.assertEqual({r['team_rule_id']:r['result'] for r in before},{'state':'applies'})
        rules[1]['applicability']={'min_units':5}
        after=self.engine(rules,precedence=[edge])
        self.assertEqual({r['team_rule_id']:r['result'] for r in after},{'state':'superseded','city':'applies'})
    def test_two_sources_merge_and_keep_the_missing_condition(self):
        case=next(c for c in load()['cases'] if c.get('group')=='size'); docs=[]; answers=[]
        for did,with_condition in [('Z090',False),('Z091',True)]:
            d=copy.deepcopy(case['document']);d['id']=did;docs.append(d)
            r=copy.deepcopy(case['oracle'][0]);r.update(packet_id=did+'-01',doc_id=did)
            if not with_condition:r['applicability']['conditions']=[]
            answers += [r,dict(packet_id=did+'-01',n_rules=1,note=None)]
        result=self.product.call(op='pipeline',documents=docs,answer='\n'.join(map(json.dumps,answers)),as_of='2026-10-01',
                                addresses={'small':dict(state='MA',legal_city='Cambridge, MA',units=5,year_built=1960),'large':dict(state='MA',legal_city='Cambridge, MA',units=6,year_built=1960)})
        self.assertFalse(result['rejected'],result['rejected']);self.assertEqual(len(result['rules']),1)
        self.assertEqual(result['lookup'][0]['lookups']['small'],[])
        self.assertEqual(result['lookup'][0]['lookups']['large'][0]['result'],'applies')
        self.assertEqual(len(result['rules'][0]['sources']),2)


class RealHttpOutcomes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=subprocess.Popen(['node','dist/web/server.js','--port','0'],cwd=ROOT,stdout=subprocess.PIPE,text=True)
        line=cls.server.stdout.readline();m=re.search(r'http://127\.0\.0\.1:\d+',line)
        if not m:cls.server.terminate();cls.server.wait();raise AssertionError(line)
        cls.base=m.group(0)
    @classmethod
    def tearDownClass(cls):cls.server.terminate();cls.server.wait();cls.server.stdout.close()
    def get(self,path,**query):
        with urllib.request.urlopen(self.base+path+'?'+urllib.parse.urlencode(query)) as r:return json.load(r)
    def test_real_state_rule_before_and_on_effective_date_has_evidence(self):
        # Existing answer key NJ-FAIR supplies the expected date; do not derive expected status from product output.
        meta=self.get('/api/meta');aid=next(a['address_id'] for a in meta['addresses'] if a['state']=='NJ')
        for day,want in [('2027-06-30','not_yet_effective'),('2027-07-01','applies')]:
            payload=self.get('/api/lookup',address_id=aid,as_of=day)
            rows=[r for r in payload['results'] if r['rule']['jurisdiction']=='NJ' and r['rule']['category']=='algorithmic_rent_setting']
            self.assertTrue(rows)
            for row in rows:
                self.assertEqual(row['result'],want)
                self.assertIn(row['rule']['citation'],row['explanation'])
                self.assertTrue(row['rule']['sources'])
                for source in row['rule']['sources']:
                    if source['doc_id'] and source['quoted_span']:
                        page=self.get('/api/source',doc_id=source['doc_id'],quote=source['quoted_span'])
                        self.assertTrue(page['found'],source)
    def test_query_override_does_not_change_the_next_request(self):
        aid=self.get('/api/meta')['addresses'][0]['address_id']
        before=self.get('/api/lookup',address_id=aid)
        entered=self.get('/api/lookup',address_id=aid,year_built=2025,units=3)
        after=self.get('/api/lookup',address_id=aid)
        self.assertEqual(entered['entered_facts'],{'year_built':2025,'units':3})
        self.assertEqual(before['results'],after['results'])
        self.assertEqual(before['address'],after['address'])

if __name__=='__main__':unittest.main()
