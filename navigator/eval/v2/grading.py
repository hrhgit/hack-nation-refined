"""Score final structured results, with denominators and no silver/model answer key."""
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from nav.facts import numbers_in

CITY={'CA':'Los Angeles, CA','NJ':'Newark, NJ','MA':'Boston, MA'}


def inputs(case, as_of):
    return dict(packet_id=case['id'],as_of=as_of,**({'documents':[case['document']]} if case['origin']=='synthetic' else {}))


def grade(product, case, answer, as_of):
    view=product.call(op='inspect',answer=answer,**inputs(case,as_of)); rules=view['accepted']
    counts=dict(expected_rules=0,found_rules=0,missing_rules=0,extra_rules=0,wrong_exclusions=0,false_applies=0,unnecessary_unknown=0,
                safe_passed=0,safe_total=0,exact_passed=0,exact_total=0,fields_passed=0,fields_total=0,evidence_passed=0,evidence_total=len(rules))
    issues=[]
    for r in rules:
        # A valid substring alone doesn't prove semantic entailment. This only checks source alignment and supported fields.
        bad=[w for w in r.get('warnings',[]) if re.search(r'not found|not printed|does not appear|differs from|ignored|dropped|differs from document',w)]
        supported=not bad and bool(r.get('quoted_span'))
        counts['evidence_passed']+=supported
        if not supported: issues.append({'citation':r['citation'],'warnings':r.get('warnings')})
    synthetic=case['origin']=='synthetic'
    labels=case['expected'] if synthetic else case['labels']
    matched=set()
    for l in labels:
        counts['expected_rules']+=1
        rx=r'(?<![0-9])'+re.escape(re.search(r'2099-\d+',l['citation']).group())+r'(?![0-9])' if synthetic else l['cite_re']
        hits=[(i,r) for i,r in enumerate(rules) if r['jurisdiction']==l['jurisdiction'] and r['category']==l['category'] and re.search(rx,r['citation']+' '+r['title'],re.I)]
        r=hits[0][1] if hits else None
        if hits: counts['found_rules']+=1;matched.add(hits[0][0])
        else: counts['missing_rules']+=1;issues.append({'label':l.get('id',l.get('citation')),'error':'missing_rule'})
        fields=('lifecycle','effective_date','valid_through','key_value') if synthetic else ('lifecycle','effective_date','valid_through','relations')
        for key in fields:
            if key not in l:continue
            want=l[key]; got=r.get(key) if r else None
            if key=='relations':
                types={t['type'] for t in (got or [])};ok=r is not None and set(want['require'])<=types and not(set(want['forbid']) & types)
            elif key=='key_value':ok=r is not None and numbers_in(want or '')<=numbers_in(got or '')
            else:ok=r is not None and got==want
            counts['fields_total']+=1;counts['fields_passed']+=ok
            if not ok:issues.append({'field':key,'expected':want,'actual':got})
        probes=case['probes'] if synthetic else l['probes']
        for p in probes:
            if r is None: got='missing'
            else:
                state=r['jurisdiction'] if r['level']=='state' else r['jurisdiction'].split(', ')[-1]
                city=r['jurisdiction'] if r['level']=='city' else CITY[state]
                addresses={'P':dict(state=state,legal_city=city,resolved_by='geocoder',**p['facts'])}
                result=product.call(op='engine',rules=[dict(r,team_rule_id='probe')],addresses=addresses,as_of=p['as_of'])
                out=result[0]['lookups']['P'];got=out[0]['result'] if out else 'excluded'
            counts['safe_total']+=1; counts['safe_passed']+=got in p['ok']
            if got in ('excluded','missing') and 'excluded' not in p['ok']:counts['wrong_exclusions']+=1
            if p['exact'] is not None:
                counts['exact_total']+=1; counts['exact_passed']+=got==p['exact']
                counts['false_applies']+=got=='applies' and p['exact']!='applies'
                counts['unnecessary_unknown']+=got=='unknown' and p['exact']!='unknown'
            if got not in p['ok'] or p['exact'] is not None and got!=p['exact']:
                issues.append({'probe':p.get('id',p.get('why')),'expected':p['exact'],'acceptable':list(p['ok']),'actual':got})
    if synthetic:counts['extra_rules']=len(rules)-len(matched)
    g={'format_ok':float(view['clean'])}
    for name,passed,total in [('rule_recall','found_rules','expected_rules'),('safe','safe_passed','safe_total'),('exact','exact_passed','exact_total'),('fields','fields_passed','fields_total'),('evidence','evidence_passed','evidence_total')]:
        if counts[total]:g[name]=counts[passed]/counts[total]
    if synthetic:
        g['no_extra_rules']=float(counts['extra_rules']==0)
        g['all_required']=float(view['clean'] and not counts['missing_rules'] and not counts['extra_rules'] and all(v==1 for v in g.values()))
    elif labels:g['all_required']=float(view['clean'] and not counts['missing_rules'] and all(v==1 for v in g.values()))
    return {'grade':g,'counts':counts,'issues':issues,'rejected':view['rejected'],'scope':'complete synthetic key' if synthetic else 'selected real rules only; extras not scored'}
