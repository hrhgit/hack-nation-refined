#!/usr/bin/env python3
"""Versioned TypeScript evaluation: live extraction or explicit historical replay.
No retries, time caps, output caps, or automatic final-test execution.
"""
import argparse
import collections
import datetime as dt
import json
import re
import statistics
import sys
import time
from pathlib import Path
from suite import HERE, ROOT, Product, load, dumps, digest, fingerprint
from grading import grade, inputs
from chain import grade_chain


def read_rows(path):
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text().split('\n') if line.strip()]


def write(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(dumps(value));tmp.replace(path)


def append(path, value):
    with path.open('a') as f:f.write(json.dumps(value,ensure_ascii=False)+'\n')


def summary(rows, planned, errors):
    valid=[r for r in rows if r['status']=='ok']
    counts=collections.Counter()
    for r in valid:counts.update(r['counts'])
    groups=collections.defaultdict(list)
    for r in valid:
        for k,v in r['grade'].items():groups[k].append(v)
    repetitions=collections.defaultdict(list)
    for r in valid:
        if 'all_required' in r['grade']:repetitions[r['prompt_id']].append(r['grade']['all_required'])
    per_case={k:statistics.mean(v) for k,v in repetitions.items()}
    return dict(expected_runs=planned,completed_runs=len(valid),completion_rate=len(valid)/planned if planned else None,
                error_attempts=len(errors),error_classes=dict(collections.Counter(e['class'] for e in errors)),
                means={k:statistics.mean(v) for k,v in groups.items()},counts=dict(counts),
                unique_scored_cases=len(per_case),case_mean=statistics.mean(per_case.values()) if per_case else None,
                variable_cases=[k for k,v in repetitions.items() if len(set(v))>1],
                note='Probe checks from the same rule and repeated answers are correlated. No significance or population accuracy claim. Unscored/missing runs are not successes.')


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--variant',required=True)
    ap.add_argument('--flow',type=Path,default=HERE/'runs')
    ap.add_argument('--split',choices=['train','validation','test'],default='validation')
    ap.add_argument('--cases',help='comma-separated IDs within selected split')
    ap.add_argument('--reps',type=int,default=2)
    ap.add_argument('--model')
    ap.add_argument('--replay',type=Path,help='historical directory containing traces; model and usage stay unknown unless recorded in original metadata')
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args(argv)
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.variant) or args.reps<1:ap.error('variant must be a simple name and reps positive')
    if args.replay and args.flow == HERE/'runs':args.flow=HERE/'replay'
    suite=load();cases=[c for c in suite['cases'] if c['split']==args.split]
    if args.cases:
        ids=set(args.cases.split(','));cases=[c for c in cases if c['id'] in ids]
        if ids!={c['id'] for c in cases}:ap.error('unknown case or case belongs to a different split')
    if args.replay:cases=[c for c in cases if c.get('labels')]
    if not cases:ap.error('no cases selected')
    with Product() as product:
        config=product.call(op='config',model=args.model)
        config={k:v for k,v in config.items() if k!='configured'}
        config.update(mode='replay' if args.replay else 'live',replay=str(args.replay.resolve()) if args.replay else None,
                      case_ids=[c['id'] for c in cases],reps=args.reps,split=args.split)
        freeze=fingerprint(suite,config)
        vdir=args.flow/args.variant; sf=vdir/'run.json'
        if sf.exists() and json.loads(sf.read_text())['sha256']!=freeze['sha256']:
            raise SystemExit('Inputs, code, prompts, model or run selection changed. Use a new variant; old results remain unchanged.')
        rows=read_rows(vdir/'results.jsonl');done={(r['prompt_id'],r['rep']) for r in rows if r['status']=='ok'}
        if len(done)!=len(rows):raise SystemExit('Duplicate or invalid result rows; inspect the local run before resuming.')
        todo=[(c,rep) for c in cases for rep in range(args.reps) if (c['id'],rep) not in done]
        print(f'{len(cases)} cases x {args.reps} reps; {len(todo)} remaining; {config["mode"]}; split={args.split}',flush=True)
        if args.dry_run:return 0
        vdir.mkdir(parents=True,exist_ok=True);write(sf,freeze)
        snapshot_path=vdir/'source_snapshot.json'
        if not snapshot_path.exists():
            from suite import load_ctx
            ctx=load_ctx(); snapshot={}
            for key,expected_hash in freeze.get('files',{}).items():
                if key.startswith('source:'):value=ctx.docs[key.split(':',1)[1]].body
                else:
                    source=Path(key.split(':',1)[1]) if key.startswith('corpus-config:') else ROOT/key
                    value=source.read_bytes().decode("utf-8")
                if digest(value.encode())!=expected_hash:raise SystemExit('Source changed while taking the run snapshot; use a new variant.')
                snapshot[key]=value
            write(snapshot_path,snapshot)
        write(args.flow/'_state.json',{'schema':'navigator-eval/v2','goal':{'target':'all_required','direction':'higher'},
             'train_ids':[c['id'] for c in suite['cases'] if c['split']=='train'],
             'val_ids':[c['id'] for c in suite['cases'] if c['split']=='validation'],
             'test_ids':[c['id'] for c in suite['cases'] if c['split']=='test'],
             'metrics':[{'id':k,'kind':'float','label':k,'scale':1} for k in ('all_required','format_ok','rule_recall','safe','exact','fields','evidence')],
             'best':None,'note':'Replay and live use separate flow directories; no official competition score.'})
        for c,rep in todo:
            if fingerprint(suite,config)['sha256'] != freeze['sha256']:
                append(vdir/'errors.jsonl',dict(prompt_id=c['id'],rep=rep,**{'class':'version_drift'},error='inputs/code/prompts changed; start a new variant'))
                break
            stem=f'{c["id"]}_rep{rep}'; response_file=vdir/'traces'/f'{stem}.response.json'; start=time.monotonic(); response=None
            try:
                if c.get('kind')=='chain':
                    chain_calls=[];chain_trace=[];answers={}
                    for pid in c['packets']:
                        # One extraction per (packet, repetition), shared by every chain that needs the packet.
                        rf=vdir/'traces'/f'chain_{pid}_rep{rep}.response.json'
                        if rf.exists():part=json.loads(rf.read_text())
                        else:
                            part=product.call(op='extract',model=config['model'],packet_id=pid,as_of=suite['as_of'],
                                              **({'documents':[d for d in c['documents'] if d['id']+'-01'==pid]} if c.get('documents') else {}))
                            if part['status']=='ok':write(rf,part)
                        if part['status']!='ok':raise RuntimeError(f'{pid}: '+str(part.get('error',part['status'])))
                        answers[pid]=part['answer'];chain_calls+=part.get('calls',[]);chain_trace+=part['trace']
                    response=dict(answer='',trace=chain_trace,model=config['model'],calls=chain_calls,status='ok')
                    if fingerprint(suite,config)['sha256'] != freeze['sha256']:
                        raise RuntimeError('version_drift: inputs/code/prompts changed during this attempt')
                    scored=grade_chain(product,c,answers,suite['as_of'])
                    trace=chain_trace;write(vdir/'traces'/f'{stem}.json',trace)
                    write(vdir/'traces'/f'{stem}.answers.json',answers)
                elif args.replay:
                    source=args.replay/'traces'/f'{stem}.json'
                    trace=json.loads(source.read_text())
                    response=dict(answer=trace[2]['content'],trace=trace,model=None,calls=[],status='ok',replay_sha256=digest(source.read_bytes()),replay_source=str(source))
                elif response_file.exists():
                    response=json.loads(response_file.read_text())
                else:
                    response=product.call(op='extract',model=config['model'],**inputs(c,suite['as_of']))
                    # Persist the actual output before grading; a grading interruption never causes another successful model call.
                    if response['status']=='ok':write(response_file,response)
                if response['status']!='ok':
                    raise RuntimeError(response.get('error',response['status']))
                if c.get('kind')!='chain':
                    if fingerprint(suite,config)['sha256'] != freeze['sha256']:
                        raise RuntimeError('version_drift: inputs/code/prompts changed during this attempt')
                    scored=grade(product,c,response['answer'],suite['as_of'])
                    trace=response['trace'];write(vdir/'traces'/f'{stem}.json',trace)
                calls=response.get('calls',[])
                usage=None
                if calls and all(call.get('usage') is not None for call in calls):
                    keys=set().union(*(call['usage'].keys() for call in calls))
                    usage={k:sum(call['usage'][k] for call in calls) if all(isinstance(call['usage'].get(k),(int,float)) for call in calls) else None for k in keys}
                row=dict(prompt_id=c['id'],rep=rep,prompt=next((m.get('content','') for m in trace if m['role']=='user'),''),
                         status='ok',output_kind='structured' if scored['grade']['format_ok'] else 'invalid_output',
                         model=response['model'],usage=usage,cost_usd=None,grade=scored['grade'],counts=scored['counts'],issues=scored['issues'],
                         evidence_scope=scored['scope'],citation_scoring_eligible=c['citation_scoring_eligible'],
                         stop_reason='stop' if calls else None,mode=config['mode'],fingerprint=freeze['sha256'],source_trace_sha256=response.get('replay_sha256'),
                         latency_s=sum(x['latency_s'] for x in calls) if calls else None,
                         evaluation_wall_s=time.monotonic()-start,ts=dt.datetime.now(dt.timezone.utc).isoformat())
                append(vdir/'results.jsonl',row);rows.append(row)
                print(stem,scored['grade'].get('all_required','unlabeled'),flush=True)
            except (OSError,RuntimeError,ValueError,KeyError) as e:
                klass='missing_replay' if args.replay and isinstance(e,FileNotFoundError) else ('truncated' if response and response.get('status')=='truncated' else 'serving_or_grading_error')
                if response and response.get('calls') and response['calls'][-1].get('status')=='transport_error':klass='transport_error'
                if 'served_model_mismatch' in str(e):klass='served_model_mismatch'
                if 'version_drift' in str(e):klass='version_drift'
                if response and response.get('status')=='ok' and klass not in ('missing_replay','version_drift'):klass='grading_error'
                error=dict(prompt_id=c['id'],rep=rep,**{'class':klass},error=str(e),model=response.get('model') if response else None,ts=dt.datetime.now(dt.timezone.utc).isoformat())
                if response:
                    attempt=len(read_rows(vdir/'errors.jsonl'));write(vdir/'traces'/f'{stem}_error{attempt}.json',response)
                append(vdir/'errors.jsonl',error);print(stem,klass,flush=True)
        result=summary(rows,len(cases)*args.reps,read_rows(vdir/'errors.jsonl'));write(vdir/'summary.json',result)
        print(dumps(result))
        return 0 if result['completed_runs']==result['expected_runs'] else 1

if __name__=='__main__':raise SystemExit(main())
