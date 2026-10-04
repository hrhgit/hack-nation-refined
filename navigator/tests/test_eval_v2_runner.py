"""Resume, immutable runs, and missing-data denominators, without any paid calls."""
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'eval/v2'))
spec=importlib.util.spec_from_file_location('eval_v2_run',ROOT/'eval/v2/run.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

class StubProduct:
    calls=0
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def call(self,**args):
        if args['op']=='config':return {'model':'test-model','endpoint':'http://127.0.0.1','configured':True}
        StubProduct.calls+=1
        return {'answer':'answer','trace':[{'role':'user','content':'input'},{'role':'assistant','content':'answer'}],
                'model':'test-model','calls':[],'status':'ok'}

class RunnerChecks(unittest.TestCase):
    def test_successful_response_is_reused_after_grading_failure(self):
        suite={'as_of':'2026-10-01','cases':[{'id':'Z001-01','split':'validation','origin':'synthetic','document':{},'citation_scoring_eligible':False}]}
        scored={'grade':{'all_required':1,'format_ok':1},'counts':{},'issues':[],'scope':'test'}
        StubProduct.calls=0
        with tempfile.TemporaryDirectory() as tmp,patch.object(runner,'Product',StubProduct),patch.object(runner,'load',return_value=suite),patch.object(runner,'fingerprint',return_value={'sha256':'one'}),contextlib.redirect_stdout(io.StringIO()):
            args=['--variant','baseline','--flow',tmp,'--reps','1']
            with patch.object(runner,'grade',side_effect=RuntimeError('grader failed')):self.assertEqual(runner.main(args),1)
            with patch.object(runner,'grade',return_value=scored):
                self.assertEqual(runner.main(args),0);self.assertEqual(runner.main(args),0)
            self.assertEqual(StubProduct.calls,1)
            rows=runner.read_rows(Path(tmp)/'baseline/results.jsonl');self.assertEqual(len(rows),1);self.assertIsNone(rows[0]['usage'])
            with patch.object(runner,'fingerprint',return_value={'sha256':'two'}),self.assertRaises(SystemExit):runner.main(args)
    def test_unicode_line_separators_in_a_prompt_do_not_split_json_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'results.jsonl'
            value={'prompt':'first\u2028second\u2029third','rep':0}
            path.write_text(json.dumps(value,ensure_ascii=False)+'\n')
            self.assertEqual(runner.read_rows(path),[value])
    def test_incomplete_batch_is_not_reported_as_complete(self):
        rows=[{'status':'ok','prompt_id':'a','counts':{},'grade':{'all_required':1}}]
        result=runner.summary(rows,4,[{'class':'transport_error'}])
        self.assertEqual(result['completion_rate'],.25);self.assertEqual(result['unique_scored_cases'],1)
        self.assertEqual(result['error_attempts'],1)

if __name__=='__main__':unittest.main()
