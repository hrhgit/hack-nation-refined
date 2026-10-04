"""Change-test chain cases: the documents behind each change test, run through the whole shipped pipeline.

A normal case grades one answer for one packet. A chain case grades what the later stages do with several answers: the model
extracts the packets, the shipped ingest (with the project's reviewed overrides) merges them, the lookup engine judges the
sample addresses, and the change tracker answers one change test. Two kinds of case:

* real chains: T1 to T5 from the participant pack, built from the packets that feed each test. The expected outcome is what the
  pack's own `dev/change_tests.json` (`expected_behavior`) says, turned into exact address sets with the 500 resolved
  addresses. They are development items: the real texts have all been seen.
* constructed chains: invented texts for the same situations (a relative effective date, a state ban on conflicting local
  ordinances, two city boundaries, a pending bill, a measure struck by a court). Two variants per family; a family stays in one split.

All expectations live here, in the scoring side. The model only ever receives the packet text.
"""
import copy
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

REAL = [  # test id -> packets that feed it
    ('T1', ['D022-01', 'X005-01']),
    ('T2', ['D034-01', 'D035-01', 'D037-01', 'X102-01']),
    ('T3', ['D069-01', 'D034-01', 'D035-01', 'D037-01', 'X102-01']),
    ('T4', ['D045-01', 'D046-01', 'D047-01']),
    ('T5', ['X101-01']),
]


def digest(value):
    if not isinstance(value, bytes):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(value).hexdigest()


# ------------------------------------------------------------------ real chains

def real_cases(resolved, dev_tests, packet_hash):
    """`resolved`: work/addresses_resolved.json; `dev_tests`: the pack's change_tests.json."""
    by_test = {t['test_id']: t for t in dev_tests}
    ids = lambda pred: sorted(a for a, v in resolved.items() if pred(v))
    ca, nj, ma = ids(lambda v: v['state'] == 'CA'), ids(lambda v: v['state'] == 'NJ'), ids(lambda v: v['state'] == 'MA')
    hob, jc = ids(lambda v: v['legal_city'] == 'Hoboken, NJ'), ids(lambda v: v['legal_city'] == 'Jersey City, NJ')
    everyone = sorted(resolved)
    expected = {
        'T1': [{'kind': 'no_missing_rules'}, {'kind': 'affected', 'ids': ca}, {'kind': 'dated', 'ids': ca, 'before': 'not_yet_effective', 'after': 'applies'}],
        'T2': [{'kind': 'no_missing_rules'}, {'kind': 'affected', 'ids': sorted(hob + jc)},
               {'kind': 'boundary', 'by_address': {a: ['HOB-ALG-01'] if a in hob else ['JC-ALG-01'] if a in jc else [] for a in everyone}}],
        'T3': [{'kind': 'no_missing_rules'}, {'kind': 'affected', 'ids': nj}, {'kind': 'dated', 'ids': nj, 'before': 'not_yet_effective', 'after': 'applies'},
               {'kind': 'conflicts', 'ids': sorted(hob + jc)},
               {'kind': 'rule_field', 'jurisdiction': 'NJ', 'citation_regex': r'56:9-20|c\.\s?43', 'field': 'effective_date', 'equals': '2027-07-01'},
               {'kind': 'rule_field', 'jurisdiction': 'NJ', 'citation_regex': r'56:9-20|c\.\s?43', 'field': 'relations', 'contains': 'preempts_local'}],
        'T4': [{'kind': 'no_missing_rules'}, {'kind': 'affected', 'ids': ma}, {'kind': 'pending'}],
        'T5': [{'kind': 'no_error'}, {'kind': 'no_missing_rules'}, {'kind': 'affected', 'ids': []},
               {'kind': 'rule_field', 'jurisdiction': 'MA', 'citation_regex': r'25-21', 'field': 'lifecycle', 'equals': 'failed'}],
    }
    rows = []
    for tid, packets in REAL:
        test = by_test[tid]
        rows.append(dict(id='CHAIN-' + tid, kind='chain', group='chain:' + tid, split='train', origin='real_chain', citation_scoring_eligible=False,
                         answer_source="the pack's dev/change_tests.json expected_behavior, made exact with the resolved sample addresses; not official scoring",
                         packets=packets, test=test, expected_behavior=test['expected_behavior'], checks=expected[tid],
                         input_sha256=digest({p: packet_hash(p) for p in packets}), source_sha256=digest(sorted(packets) + [tid]),
                         exposure='Real material, already seen in this project; development only.'))
    return rows


# ------------------------------------------------------------------ constructed chains

HEAD = 'INVENTED EVALUATION TEXT — not actual law.\n'
SENT = 'A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.'
TOWNS = {  # synthetic sample addresses; every address carries the facts the engine needs
    'M1': ('MA', 'Boston, MA'), 'M2': ('MA', 'Boston, MA'), 'M3': ('MA', 'Cambridge, MA'), 'M4': ('MA', 'Cambridge, MA'),
    'H1': ('NJ', 'Hoboken, NJ'), 'H2': ('NJ', 'Hoboken, NJ'), 'J1': ('NJ', 'Jersey City, NJ'), 'J2': ('NJ', 'Jersey City, NJ'),
    'N1': ('NJ', 'Newark, NJ'), 'L1': ('CA', 'Los Angeles, CA')}


def addresses(*names):
    return {n: dict(state=TOWNS[n][0], legal_city=TOWNS[n][1], resolved_by='geocoder', year_built=1960, units=10, units_at_least=None) for n in names}


def record(did, jur, category, cite, quote, requirement=None, life='enacted', effective=None, relations=None, key=None):
    return dict(packet_id=did + '-01', doc_id=did, jurisdiction=jur, category=category, lifecycle=life, title='Synthetic ' + cite,
                requirement=requirement or quote, citation=cite, quoted_span=quote, effective_date=effective, valid_through=None, key_value=key,
                coverage_conditions=None, exemptions=None, penalty=None, interaction=None, confidence=1, conflict_flag=False, conflict_note=None,
                relations=relations or [], applicability={'conditions': [], 'coverage_quotes': [], 'per_tenancy': None})


def doc(did, jur, body):
    return dict(id=did, jurisdiction=jur, url='https://example.test/eval/' + did, text=HEAD + jur + '\n' + body)


def oracle(rec):
    return [rec, dict(packet_id=rec['packet_id'], n_rules=1, note=None)] if rec else []


def families():
    """(family, split, builder(variant, first_doc_number) -> dict(docs, records, test, rule_map, addresses, checks))."""
    def relative(v, n):
        cite = 'Invented Act 2099-R%d' % v
        clause, approved, eff, before, after = [
            ('This act shall take effect on the first day of the twelfth month next following its enactment.', 'August 12, 2026', '2027-08-01', '2026-10-01', '2027-08-02'),
            ('This act takes effect ninety (90) days after its approval.', 'September 10, 2026', '2026-12-09', '2026-10-01', '2026-12-10')][v]
        d = doc('Y%03d' % n, 'MA', 'An Act Relating to Rent-Setting Software (%s)\nSection 1. %s\nSection 2. %s\nApproved %s.\n' % (cite, SENT, clause, approved))
        rec = record(d['id'], 'MA', 'algorithmic_rent_setting', cite, SENT, effective=eff)
        ids = ['M1', 'M2', 'M3', 'M4']
        return dict(docs=[d], records=[rec], test=dict(test_id='C-REL%d' % v, title='relative effective date', type='as_of', rule_ids=['CH-A'], as_of_before=before, as_of_after=after, states=['MA']),
                    rule_map={'CH-A': dict(jurisdiction='MA', category='algorithmic_rent_setting', citation_regex='2099-R%d' % v)}, addresses=addresses(*ids, 'N1'),
                    checks=[{'kind': 'no_missing_rules'}, {'kind': 'affected', 'ids': ids}, {'kind': 'dated', 'ids': ids, 'before': 'not_yet_effective', 'after': 'applies'},
                            {'kind': 'rule_field', 'jurisdiction': 'MA', 'citation_regex': '2099-R%d' % v, 'field': 'effective_date', 'equals': eff}])

    def preempt(v, n):
        city = ['Cambridge, MA', 'Boston, MA'][v]; hit = ['M3', 'M4'] if v == 0 else ['M1', 'M2']
        eff, before, after = [('January 1, 2028', '2027-12-31', '2028-01-02'), ('July 1, 2029', '2029-06-30', '2029-07-02')][v]
        iso = {'January 1, 2028': '2028-01-01', 'July 1, 2029': '2029-07-01'}[eff]
        ban = 'A municipality may not enact or enforce an ordinance that conflicts with this act.'
        sa, ca = 'Invented Act 2099-P%d' % v, '%s Invented Ordinance 2099-Q%d' % (city.split(',')[0], v)
        d1 = doc('Y%03d' % n, 'MA', 'An Act Relating to Rent-Setting Software (%s)\nSection 1. %s\nSection 2. %s\nSection 3. This act takes effect on %s.\n' % (sa, SENT, ban, eff))
        d2 = doc('Y%03d' % (n + 1), city, 'Ordinance %s\nSection 1. %s\nSection 2. This ordinance takes effect on January 1, 2025.\n' % (ca, SENT))
        r1 = record(d1['id'], 'MA', 'algorithmic_rent_setting', sa, SENT, effective=iso, relations=[{'type': 'preempts_local', 'quote': ban}])
        r2 = record(d2['id'], city, 'algorithmic_rent_setting', ca, SENT, effective='2025-01-01')
        ids = ['M1', 'M2', 'M3', 'M4']
        return dict(docs=[d1, d2], records=[r1, r2], test=dict(test_id='C-PRE%d' % v, title='state ban on conflicting local ordinances', type='as_of', rule_ids=['CH-A'], conflict_with=['CH-B'],
                                                         as_of_before=before, as_of_after=after, states=['MA']),
                    rule_map={'CH-A': dict(jurisdiction='MA', category='algorithmic_rent_setting', citation_regex='2099-P%d' % v),
                              'CH-B': dict(jurisdiction=city, category='algorithmic_rent_setting', citation_regex='2099-Q%d' % v)}, addresses=addresses(*ids, 'N1'),
                    checks=[{'kind': 'no_missing_rules'}, {'kind': 'affected', 'ids': ids}, {'kind': 'dated', 'ids': ids, 'before': 'not_yet_effective', 'after': 'applies'},
                            {'kind': 'conflicts', 'ids': hit}, {'kind': 'rule_field', 'jurisdiction': 'MA', 'citation_regex': '2099-P%d' % v, 'field': 'relations', 'contains': 'preempts_local'}])

    def boundary(v, n):
        (ja, a_ids, pa), (jb, b_ids, pb), outside = [(('Hoboken, NJ', ['H1', 'H2'], 'H'), ('Jersey City, NJ', ['J1', 'J2'], 'J'), 'N1'),
                                                    (('Cambridge, MA', ['M3', 'M4'], 'H'), ('Boston, MA', ['M1', 'M2'], 'J'), 'L1')][v]
        ca, cb = '%s Invented Ordinance 2099-%s%d' % (ja.split(',')[0], pa, v), '%s Invented Ordinance 2099-%s%d' % (jb.split(',')[0], pb, v)
        d1 = doc('Y%03d' % n, ja, 'Ordinance %s\nSection 1. %s\nSection 2. This ordinance takes effect on March 1, 2025.\n' % (ca, SENT))
        d2 = doc('Y%03d' % (n + 1), jb, 'Ordinance %s\nSection 1. %s\nSection 2. This ordinance takes effect on June 1, 2025.\n' % (cb, SENT))
        r1 = record(d1['id'], ja, 'algorithmic_rent_setting', ca, SENT, effective='2025-03-01')
        r2 = record(d2['id'], jb, 'algorithmic_rent_setting', cb, SENT, effective='2025-06-01')
        names = a_ids + b_ids + [outside]
        by = {x: ['CH-A'] for x in a_ids}; by.update({x: ['CH-B'] for x in b_ids}); by[outside] = []
        return dict(docs=[d1, d2], records=[r1, r2], test=dict(test_id='C-BND%d' % v, title='two city boundaries', type='boundary', rule_ids=['CH-A', 'CH-B'], as_of='2026-10-01'),
                    rule_map={'CH-A': dict(jurisdiction=ja, category='algorithmic_rent_setting', citation_regex='2099-%s%d' % (pa, v)),
                              'CH-B': dict(jurisdiction=jb, category='algorithmic_rent_setting', citation_regex='2099-%s%d' % (pb, v))}, addresses=addresses(*names),
                    checks=[{'kind': 'no_missing_rules'}, {'kind': 'affected', 'ids': sorted(a_ids + b_ids)}, {'kind': 'boundary', 'by_address': by}])

    def pending(v, n):
        cite = 'Invented Bill H.99%d' % v
        status = ['This bill is pending in committee. It has not been enacted and has no effective date.',
                  'This bill was referred to the Joint Committee on Housing and has not passed either chamber. It has no effective date.'][v]
        d = doc('Y%03d' % n, 'MA', 'A Bill Relating to Rent-Setting Software (%s)\n%s\n%s\n' % (cite, SENT, status))
        rec = record(d['id'], 'MA', 'algorithmic_rent_setting', cite, SENT, life='pending_bill')
        ids = ['M1', 'M2', 'M3', 'M4']
        return dict(docs=[d], records=[rec], test=dict(test_id='C-PND%d' % v, title='pending bill', type='pending', rule_ids=['CH-A'], as_of='2026-10-01', states=['MA']),
                    rule_map={'CH-A': dict(jurisdiction='MA', category='algorithmic_rent_setting', citation_regex='H\\.99%d' % v)}, addresses=addresses(*ids, 'N1'),
                    checks=[{'kind': 'no_missing_rules'}, {'kind': 'affected', 'ids': ids}, {'kind': 'pending'}])

    def failed(v, n):
        cite = 'Invented Initiative Petition 99-%d' % v
        quote = 'An Initiative Petition to Limit Residential Rent Increases (%s).' % cite
        status = ['On June 23, 2026 the Supreme Judicial Court ruled that the question may not be placed on the 2026 ballot. The measure will not appear and cannot take effect.',
                  'The sponsors did not collect enough signatures, the question was never placed on the 2026 ballot, and the measure was abandoned. It cannot take effect.'][v]
        d = doc('Y%03d' % n, 'MA', '%s\n%s\n' % (quote, status))
        rec = record(d['id'], 'MA', 'rent_increase_limits', cite, quote, life='failed')
        return dict(docs=[d], records=[rec], test=dict(test_id='C-FLD%d' % v, title='failed ballot question', type='negative', rule_ids=['CH-A'], as_of='2026-10-01', states=['MA']),
                    rule_map={'CH-A': dict(jurisdiction='MA', category='rent_increase_limits', citation_regex='99-%d' % v)}, addresses=addresses('M1', 'M2', 'M3', 'M4', 'N1'),
                    checks=[{'kind': 'no_error'}, {'kind': 'no_missing_rules'}, {'kind': 'affected', 'ids': []},
                            {'kind': 'rule_field', 'jurisdiction': 'MA', 'citation_regex': '99-%d' % v, 'field': 'lifecycle', 'equals': 'failed'}])

    return [('chainrelative', 'validation', relative), ('chainpreempt', 'validation', preempt), ('chainboundary', 'validation', boundary),
            ('chainpending', 'test', pending), ('chainfailed', 'test', failed)]


def constructed_cases(first_doc_number=101):
    rows, n = [], first_doc_number
    for family, split, build in families():
        for v in range(2):
            c = build(v, n); n += len(c['docs'])
            packets = [d['id'] + '-01' for d in c['docs']]
            rows.append(dict(id='CHAIN-%s-%d' % (family[5:].upper(), v), kind='chain', group=family, split=split, origin='synthetic_chain', citation_scoring_eligible=False,
                             answer_source='constructed from explicit invented text; not independently human-reviewed',
                             packets=packets, documents=c['docs'], addresses=c['addresses'], test=c['test'], rule_map=c['rule_map'], checks=c['checks'],
                             oracle={r['packet_id']: oracle(r) for r in c['records']},
                             input_sha256=digest(c['docs']), source_sha256=digest([d['text'] for d in c['docs']])))
    return rows


def oracle_answers(case):
    return {pid: '\n'.join(map(json.dumps, rows)) for pid, rows in case['oracle'].items()}


# ------------------------------------------------------------------ grading

def evaluate(case, out):
    """[(name, passed, detail)] for one chain result."""
    tid = case['test']['test_id']
    results = []
    if out.get('error'):
        return [(c['kind'], False, 'change tracker stopped: ' + out['error'][:160]) for c in case['checks']]
    change, audit = out['changes'][tid], out['audit']['tests'][tid]
    mapping, evidence = audit['rule_mapping'], audit['evidence']
    inverse = {rid: key for key, rids in mapping.items() for rid in rids}
    rules = out['rules']
    for c in case['checks']:
        kind, ok, detail = c['kind'], False, ''
        if kind == 'no_error':
            ok = True
        elif kind == 'no_missing_rules':
            ok = not audit['missing_rules']; detail = 'missing %s' % audit['missing_rules']
        elif kind == 'affected':
            got = sorted(change['affected_address_ids']); ok = got == sorted(c['ids']); detail = 'want %d got %d; missing %s extra %s' % (len(c['ids']), len(got), sorted(set(c['ids']) - set(got))[:4], sorted(set(got) - set(c['ids']))[:4])
        elif kind == 'conflicts':
            got = sorted(change['conflict_flag_address_ids']); ok = got == sorted(c['ids']); detail = 'want %d got %d; missing %s extra %s' % (len(c['ids']), len(got), sorted(set(c['ids']) - set(got))[:4], sorted(set(got) - set(c['ids']))[:4])
        elif kind == 'dated':
            bad = []
            for aid in c['ids']:
                ev = evidence.get(aid) or {}
                for side in ('before', 'after'):
                    seen = {v[0] for v in (ev.get(side) or {}).values()}
                    if seen != {c[side]}: bad.append((aid, side, sorted(seen)))
            ok = not bad; detail = 'wrong: %s' % bad[:3]
        elif kind == 'boundary':
            bad = [(aid, sorted(want), sorted({inverse.get(r['team_rule_id'], r['team_rule_id']) for r in evidence.get(aid) or []}))
                   for aid, want in c['by_address'].items()
                   if {inverse.get(r['team_rule_id'], r['team_rule_id']) for r in evidence.get(aid) or []} != set(want)]
            ok = not bad; detail = 'wrong: %s' % bad[:3]
        elif kind == 'pending':
            seen = {r['result'] for rows in evidence.values() for r in rows}; ok = seen == {'pending'}; detail = 'results %s' % sorted(seen)
        elif kind == 'rule_field':
            rx = re.compile(c['citation_regex'], re.I)
            hit = [r for r in rules if r['jurisdiction'] == c['jurisdiction'] and rx.search(r['citation'])]
            got = hit[0].get(c['field']) if hit else None
            ok = bool(hit) and (got == c['equals'] if 'equals' in c else c['contains'] in (got or []))
            detail = 'rule %s: %s = %s' % (hit[0]['citation'] if hit else 'missing', c['field'], got)
        else:
            raise ValueError('unknown chain check ' + kind)
        results.append((kind, ok, detail))
    return results


def grade_chain(product, case, answers, as_of):
    synthetic = case['origin'] == 'synthetic_chain'
    documents = {d['id'] + '-01': d for d in case.get('documents', [])}
    views = {}
    for pid in case['packets']:
        views[pid] = product.call(op='inspect', answer=answers.get(pid, ''), packet_id=pid, as_of=as_of, **({'documents': [documents[pid]]} if synthetic else {}))
    clean = [bool(v['clean']) for v in views.values()]
    args = dict(op='chain', as_of=as_of, answers={pid: answers.get(pid, '') for pid in case['packets']}, tests=[case['test']])
    if synthetic: args.update(documents=case['documents'], addresses=case['addresses'], rule_map=case['rule_map'])
    out = product.call(**args)
    checks = evaluate(case, out)
    passed = sum(ok for _, ok, _ in checks)
    counts = dict(chain_checks_total=len(checks), chain_checks_passed=passed, packets_total=len(clean), packets_clean=sum(clean),
                  rejected_records=out['rejected'], tracker_stopped=int(bool(out.get('error'))),
                  packets_done=sum(s['state'] == 'done' for pid, s in out['states'].items() if pid in case['packets']))
    grade = {'format_ok': float(all(clean)), 'chain_checks': passed / len(checks) if checks else 1.0}
    grade['all_required'] = float(all(clean) and passed == len(checks) and not out['rejected'])
    issues = [{'check': name, 'detail': detail} for name, ok, detail in checks if not ok]
    issues += [{'packet': pid, 'rejected': v['rejected'], 'problems': v['problems']} for pid, v in views.items() if not v['clean']]
    return {'grade': grade, 'counts': counts, 'issues': issues, 'rejected': [r for v in views.values() for r in v['rejected']],
            'scope': 'change-test chain: ingest, lookup and change tracker on the extracted packets'}
