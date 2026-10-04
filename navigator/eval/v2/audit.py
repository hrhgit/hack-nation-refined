#!/usr/bin/env python3
"""Exhaustive structural audit; near-duplicates are review candidates, not deleted automatically."""
import collections
import itertools
import re
from suite import HERE,load,load_ctx,dumps


def audit(suite):
    cases=suite['cases'];ctx=load_ctx();ids=[c['id'] for c in cases];errors=[];groups={};hashes={}
    lengths=[];categories=collections.Counter();bodies={}
    for c in cases:
        if c.get('kind')=='chain':
            # chain cases reuse packets or documents that are checked elsewhere; only grouping and splits are audited here
            for d,k in [(groups,c['group']),(hashes,c['source_sha256'])]:
                if d.setdefault(k,c['split'])!=c['split']:errors.append(c['id']+': group/duplicate crosses split')
            if c['origin']=='real_chain' and c['split']!='train':errors.append(c['id']+': exposed material outside development')
            for d in c.get('documents',[]):
                bodies[d['id']]=d['text'];lengths.append(len(d['text']))
            continue
        if c['origin']=='synthetic':body=c['document']['text'];labels=c['expected']
        else:
            body=ctx.docs[c['doc_id']].body;labels=c['labels']
            if c['split']!='train':errors.append(c['id']+': exposed material outside development')
        bodies[c['doc_id']]=body;lengths.append(len(body))
        for label in labels:categories[label['category']]+=1
        for d,k in [(groups,c['group']),(hashes,c['source_sha256'])]:
            if d.setdefault(k,c['split'])!=c['split']:errors.append(c['id']+': group/duplicate crosses split')
    if len(ids)!=len(set(ids)):errors.append('duplicate case IDs')
    sets={did:set(tuple(words[i:i+5]) for i in range(max(0,len(words)-4))) for did,body in bodies.items() for words in [re.findall(r'\w+',body.lower())]}
    near=[]
    for a,b in itertools.combinations(sorted(sets),2):
        x,y=sets[a],sets[b]
        if not x or not y or min(len(x),len(y))/max(len(x),len(y))<.8:continue
        score=len(x&y)/len(x|y)
        if score>=.8:near.append({'a':a,'b':b,'five_word_jaccard':round(score,4)})
    return {'cases':len(cases),'documents':len(bodies),'groups':len(groups),'splits':dict(collections.Counter(c['split'] for c in cases)),
            'origins':dict(collections.Counter(c['origin'] for c in cases)),'label_categories':dict(categories),
            'document_characters':{'min':min(lengths),'max':max(lengths)},'near_duplicate_candidates':near,
            'unlabeled_development_packets':[c['id'] for c in cases if c['split']=='train' and c.get('kind')!='chain' and not c['labels']],
            'chain_cases':{'real':sum(c['origin']=='real_chain' for c in cases),'constructed':sum(c['origin']=='synthetic_chain' for c in cases)},
            'errors':errors,'warning':'Near duplicates are correlated examples. Corpus labels inherited, not independently re-verified. Synthetic final set is small and not representative traffic.'}

if __name__=='__main__':
    result=audit(load());(HERE/'audit.json').write_text(dumps(result));print(dumps(result));raise SystemExit(bool(result['errors']))
