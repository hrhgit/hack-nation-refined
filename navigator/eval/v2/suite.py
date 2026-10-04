"""Versioned inputs, provenance, grouping, and a read-only TypeScript adapter."""
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
from common import load_ctx
from cond_labels import COND_LABELS
from synthetic import build
import chain


def dumps(value):
    return json.dumps(value, ensure_ascii=False, indent=2, default=lambda x: sorted(x)) + '\n'


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else dumps(value).encode()).hexdigest()


class Product:
    def __init__(self):
        self.proc = subprocess.Popen(['node', str(HERE/'product.mjs')], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    def call(self, **args):
        self.proc.stdin.write(json.dumps(args, default=lambda x: sorted(x))+'\n'); self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line: raise RuntimeError('TypeScript adapter stopped without a response')
        out = json.loads(line)
        if 'error' in out: raise RuntimeError(out['error'])
        return out['value']
    def close(self):
        self.proc.stdin.close(); self.proc.wait(); self.proc.stdout.close()
    def __enter__(self): return self
    def __exit__(self, *args): self.close()


def prepare():
    ctx = load_ctx(); rows = []; bodies = {}
    for pid, meta in sorted(ctx.index['packets'].items()):
        doc = ctx.docs[meta['doc_id']]
        # Exact normalized duplicate documents share a group (including D046/D047).
        bodyhash = digest(re.sub(r'\s+', '', doc.body).encode())
        group = bodies.setdefault(bodyhash, doc.doc_id)
        labels = [l for l in COND_LABELS if l['packet'] == pid]
        rows.append(dict(id=pid,doc_id=doc.doc_id,group='document:'+group,split='train',origin=doc.origin,
                         citation_scoring_eligible=doc.origin=='starter',input_sha256=digest(ctx.packet_file(pid).read_bytes()),
                         source_sha256=digest(doc.body.encode()),source_path=str(Path(doc.text_path).relative_to(ROOT.parent)) if doc.text_path else None,
                         source_url=doc.url,labels=labels,answer_source='legacy manually authored labels; carried forward, not newly legally verified',
                         exposure='Previously available in this project; development only.'))
    rows += build()
    # Change-test chains: the packets behind T1-T5 (development) and constructed look-alikes (validation / test).
    pack = ctx.paths.data_dir
    resolved = json.loads((ROOT / 'work' / 'addresses_resolved.json').read_text())
    dev_tests = json.loads((pack / 'dev' / 'change_tests.json').read_text())
    rows += chain.real_cases(resolved, dev_tests, lambda pid: digest(ctx.packet_file(pid).read_bytes()))
    rows += chain.constructed_cases()
    # All source documents previously in the project remain development, even if formerly called held_out.
    for c in rows:
        if c['origin']=='synthetic': c['input_sha256']=digest(c['document']); c['source_sha256']=digest(c['document']['text'].encode())
    suite = {'schema':'navigator-eval/v2','as_of':'2026-10-01','cases':rows,
             'policy':'Historical corpus is development. New synthetic families are validation/test. Synthetic scores are not official citation scores.'}
    (HERE/'cases.json').write_text(dumps(suite))
    review = ['# 第二版样本与答案审阅','', '真实材料均保留为开发题；新题为助手构造的人工文本，尚无人独立核对。所有预期都在评分端；模型只收到原文。',
              '本文件包含保留测试题答案，不能交给修改提示词的分析员。当前作者能读到本文件，因此不声称人员之间的盲测隔离。','',
              '|组别|文本包数|说明|','|---|---:|---|']
    for split in ('train','validation','test'):
        review.append(f'|{split}|{sum(c["split"]==split for c in rows)}|按文件/题型整组保留|')
    review += ['', '## 新题原文与预期']
    for c in rows:
        if c['origin']!='synthetic': continue
        review += ['',f'### {c["id"]} · {c["group"]} · {c["split"]}', '', c['document']['text'], '',
                   '预期记录数：'+str(len(c['expected'])), '', dumps(c['probes'])]
    review += ['', '## 变更链题（文本包 → 入库 → 查询 → 变更题）', '',
               '每题让模型提取一组文本包，再走正式的入库、地址查询和变更题，检查变更题的结果。真实链 CHAIN-T1 到 CHAIN-T5 用比赛随包的 `expected_behavior` 和 500 个已解析地址；构造链用虚构文本。预期都在评分端。', '']
    for c in rows:
        if c.get('kind')!='chain': continue
        review += ['', f'### {c["id"]} · {c["group"]} · {c["split"]}', '', '文本包：'+', '.join(c['packets'])+'；变更题：'+c['test']['test_id']+'（'+c['test']['type']+'）']
        if c['origin']=='synthetic_chain':
            for d in c['documents']: review += ['', d['text']]
        else: review += ['', '随包说明：'+c['expected_behavior']]
        shown=[{k:(v if k not in ('ids','by_address') else (v if len(v)<=6 else '%d 项'%len(v))) for k,v in ch.items()} for ch in c['checks']]
        review += ['', dumps(shown)]
    review += ['', '## 真实材料清单', '', '|文本包|来源|条件答案数|随包引用可评分|','|---|---|---:|---|']
    for c in rows:
        if c['origin'] not in ('synthetic','real_chain','synthetic_chain'):review.append(f'|{c["id"]}|{c["origin"]}|{len(c["labels"])}|{c["citation_scoring_eligible"]}|')
    (HERE/'INPUTS.md').write_text('\n'.join(review)+'\n')
    return suite


def load(): return json.loads((HERE/'cases.json').read_text())


def fingerprint(suite, config):
    files = set()
    for folder in ('src/nav','src/lookup','src/changes','dist/nav','dist/lookup','dist/changes','prompts','eval/v2','nav'):
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ('.py','.ts','.js','.mjs','.json','.md') and '__pycache__' not in str(p) and not {'runs','replay'} & set(p.parts) and (folder=='prompts' or p.suffix!='.md') and p.name!='audit.json')
    for rel in ('src/http.ts','src/util.ts','src/types.ts','dist/http.js','dist/util.js','eval/common.py','package-lock.json','eval/cond_labels.py','lookup/precedence.json','lookup/review_pairs.json','lookup/coverage_overrides.json','lookup/coverage_facts.json','changes/test_rule_map.json','work/index.json','work/overrides.json','work/addresses_resolved.json'):
        if (ROOT/rel).exists():files.add(ROOT/rel)
    manifest = {str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in sorted(files)}
    # Actual source and packet contents are hashed, not merely paths or frozen labels.
    ctx=load_ctx()
    for p in (ctx.paths.schema_file, ctx.paths.manifest, ctx.paths.extra_manifest):
        if p.exists():manifest['corpus-config:'+str(p)]=digest(p.read_bytes())
    for c in suite['cases']:
        if c['origin']=='real_chain':
            for pid in c['packets']:
                p=ctx.packet_file(pid); manifest[str(p.relative_to(ROOT))]=digest(p.read_bytes())
        elif c['origin'] not in ('synthetic','synthetic_chain'):
            p=ctx.packet_file(c['id']); manifest[str(p.relative_to(ROOT))]=digest(p.read_bytes())
            manifest['source:'+c['doc_id']]=digest(ctx.docs[c['doc_id']].body.encode())
    return {'sha256':digest({'files':manifest,'config':config}), 'files':manifest, 'config':config}


if __name__=='__main__':
    s=prepare(); print(dict(collections.Counter(c['split'] for c in s['cases'])))
