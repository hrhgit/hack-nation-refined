"""Constructed texts and independent expected outcomes, not actual law or official scoring.
All family members stay together. No production prompts are changed using reserved final cases.
"""
import copy

def build():
    rows = []
    families = [
        ('size', 'validation'), ('owner', 'validation'), ('effective', 'validation'), ('empty', 'validation'),
        ('expiry', 'test'), ('benefit', 'test'), ('alternative', 'test'), ('pending', 'test'),
    ]
    for fi, (family, split) in enumerate(families):
        for variant in range(2):
            did = 'Z%03d' % (fi * 2 + variant + 1); pid = did + '-01'; n = 6 + variant * 3
            cite = 'Cambridge Ordinance No. 2099-%d' % (fi * 2 + variant + 1)
            base = 'A landlord shall not demand a security deposit exceeding one month of rent.'
            conditions = []; probes = []; extra = ''; life = 'enacted'; effective = '2025-01-01'; end = None
            category='security_deposits';key='one month'
            def probe(name, expected, **facts):
                return {'id':name,'facts':{'year_built':1960,'units':20,'units_at_least':None,**facts},'as_of':'2026-10-01','exact':expected,'ok':[expected], 'basis':'Explicit synthetic clause in this document.'}
            if family == 'size':
                extra = f'This ordinance applies only to residential buildings containing at least {n} dwelling units.'
                conditions = [dict(type='units',role='covered',op='at_least',n=n)]
                probes = [probe('below','excluded',units=n-1),probe('at','applies',units=n),probe('missing','unknown',units=None),probe('conflict','unknown',units=2,units_at_least=n+1)]
            elif family == 'owner':
                category='screening_restrictions';key=None
                base='A landlord shall not reject a tenant solely because rent is paid using a housing subsidy.'
                extra = f'Owner-occupied premises with no more than {n} dwelling units are exempt from this ordinance.'
                conditions = [dict(type='owner',role='exempt',who='owner-occupied',unit_limit=n)]
                probes = [probe('owner-unknown','unknown',units=n),probe('too-large-for-exemption','applies',units=n+1)]
            elif family == 'effective':
                category='algorithmic_rent_setting';key=None
                base='A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.'
                effective = '2027-0%d-01' % (variant+2); extra = f'This ordinance takes effect on {effective}.'
                probes = [probe('before','not_yet_effective'),probe('on','applies')];probes[-1]['as_of']=effective
            elif family == 'empty':
                base = ('This library bulletin lists opening hours and contains no rental housing requirements.' if not variant else
                        'Federal law only: 15 U.S.C. 1681m requires users of consumer reports to provide an adverse action notice. This page states no state or city rule.')
                life = None
            elif family == 'expiry':
                end = '2026-10-%02d' % (12+variant); extra=f'This temporary security deposit rule remains valid through {end} and expires the next day.'
                probes = [probe('last-day','applies'),probe('next-day','excluded')]
                probes[0]['as_of']=end;probes[1]['as_of']='2026-10-%02d' % (13+variant)
            elif family == 'benefit':
                category='rent_increase_limits';key=f'{n} years'
                base = f'Newly constructed residential buildings are exempt from local rent control for {n} years following completion of construction.'
                conditions = [dict(type='built_within_years',role='covered',years=n,basis='construction')]
                probes=[probe('new','applies',year_built=2025),probe('old','excluded',year_built=1990),probe('boundary','unknown',year_built=2026-n)]
            elif family == 'alternative':
                category='just_cause_eviction';key=None
                base='A landlord may terminate a residential tenancy only for a just cause listed in Section 9.'
                extra=f'This ordinance covers buildings constructed before January 1, {1980+variant}, as well as replacement units built under Section 9.'
                conditions=[dict(type='built',role='covered',op='before',date=str(1980+variant)+'-01-01',basis='construction',also='replacement units built under Section 9')]
                probes=[probe('old','applies'),probe('replacement-unknown','unknown',year_built=2020)]
            else:
                category='application_screening_fees';key='37 dollars'
                base='A landlord shall not charge an application screening fee exceeding 37 dollars.'
                life='pending_bill';effective=None;extra='This is a proposal still in committee. It has not been enacted and has no effective date.'
                probes=[probe('proposal','pending')]
            heading = f'INVENTED EVALUATION TEXT — not actual law.\nCambridge, MA\n{cite}\n'
            text = heading + base + '\n' + extra + ('\nEffective January 1, 2025.' if effective=='2025-01-01' and life else '')
            record = dict(packet_id=pid,doc_id=did,jurisdiction='Cambridge, MA',category=category,
                          lifecycle=life,title='Synthetic '+family,requirement=base,citation=cite,quoted_span=base,effective_date=effective,valid_through=end,
                          key_value=key,coverage_conditions=extra or None,exemptions=None,penalty=None,interaction=None,
                          confidence=1,conflict_flag=False,conflict_note=None,relations=[],applicability={'conditions':conditions,'coverage_quotes':[extra or base],'per_tenancy':None})
            oracle = [record] if life else []
            row = dict(id=pid,doc_id=did,group=family,split=split,origin='synthetic',citation_scoring_eligible=False,
                       answer_source='constructed from explicit invented text; not independently human-reviewed',
                       document=dict(id=did,jurisdiction='Cambridge, MA',url='https://example.test/eval/'+did,text=text),
                       expected=copy.deepcopy(oracle),probes=probes,oracle=oracle+[dict(packet_id=pid,n_rules=len(oracle),note=None)])
            rows.append(row)
    return rows
