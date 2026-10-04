import path from 'node:path';
import type {Data, Rule, Address, LookupRow} from '../types.js';
import {clone, cmp, equal, pyStr, readJson, setKey, slice, sortedEntries, truth, unique, yearsBefore} from '../util.js';
import {CATEGORIES, DEFAULT_DATE, DISCLAIMER, ROOT, dateInterval, matches, queryDate} from './common.js';

export const REVIEW_NOTE = 'a state law and a city ordinance regulate the same subject and the sources do not settle which one governs here; flagged for human review';
export const FIELDS = ['team_rule_id', 'jurisdiction', 'level', 'category', 'status', 'title', 'requirement', 'key_value', 'coverage_conditions', 'exemptions', 'overrides', 'interaction', 'effective_date', 'citation', 'source_doc_id', 'source_url', 'quoted_span', 'confidence', 'conflict_flag', 'conflict_note'];
export const sentence = (s: string): string => {s = s.trim(); return s[0].toUpperCase() + s.slice(1) + (s.endsWith('.') ? '' : '.');};
export const stateOf = (r: Rule): string => r.level === 'state' ? r.jurisdiction : r.jurisdiction.split(', ').at(-1)!;
export function loadRules(file = path.join(ROOT, 'work/rules_enriched.json'), supplements?: Data[], report?: Data): Rule[] {
  const payload = readJson(file), rules: Rule[] = clone(Array.isArray(payload) ? payload : payload.rules);
  for (const s of supplements ?? readJson(path.join(ROOT, 'lookup/coverage_facts.json'))) {
    if (!s.basis || !s.source) throw new Error('覆盖条件补充必须有依据和来源');
    let hits = 0;
    for (const r of rules) if (matches(r, s.match)) {
      hits++; if (!truth(r.applicability)) r.applicability = {};
      for (const [k, v] of Object.entries(s.applicability ?? {})) {
        const old = r.applicability![k] ?? null;
        if (report && ![null, false, [], v].some(x => equal(x, old))) (report.differs ??= []).push({supplement: s.id, rule: r.team_rule_id, citation: r.citation, field: k, extracted: old, supplement_value: v});
      }
      Object.assign(r.applicability!, clone(s.applicability ?? {})); Object.assign(r, clone(s.set ?? {}));
      (r.coverage_sources ??= []).push({id: s.id, basis: s.basis, source: s.source});
    }
    if (!hits && report) (report.unused ??= []).push(s.id);
  }
  return rules;
}
const BUILDING_WORDS = /exclud|exempt|does not apply|not apply to|only (?:to|if|a)|owner[- ]occup|subsid|affordable|income[- ]restricted|funded|certificate of occupancy|covered by|under the rent ordinance|convert|condominium|mobile ?home|(?:one|two|three|single)[- ]family|produced in|built|constructed/i;
export const otherKind = (text: string): string => BUILDING_WORDS.test(text) ? 'building' : 'trigger';
export function statusOn(rule: Rule, asOf: string): string {
  const life = rule.lifecycle;
  if (life === 'failed' || life === 'withdrawn') return 'failed';
  if (life === 'pending_bill') return 'pending';
  if (life !== 'enacted') return 'unknown';
  if (!rule.effective_date) return 'in_force';
  const [first, last] = dateInterval(rule.effective_date), day = queryDate(asOf);
  return day < first ? 'not_yet_effective' : day < last ? 'unknown' : 'in_force';
}
type Pair = {yielding: string; prevailing: string; entry: Data};
type Check = {field: string; fact: any; outcome: string; explanation: string};
export class LookupEngine {
  rules: Rule[]; addresses: Record<string, Address>; precedence: Data[]; review: Data[];
  by_id: Record<string, Rule>; edges: Pair[]; review_pairs: Pair[];
  constructor(rules: Rule[], addresses: Record<string, Address>, precedence?: Data[], review?: Data[]) {
    for (const r of rules) for (const field of ['team_rule_id', 'jurisdiction', 'citation']) if (typeof r[field] !== 'string' || !r[field].trim()) throw new Error('规则缺少有效的' + field);
    this.rules = clone(rules).sort((a, b) => cmp(a.team_rule_id, b.team_rule_id)); this.addresses = clone(addresses);
    for (const [id, a] of Object.entries(this.addresses)) {
      if (typeof a.state !== 'string' || !a.state) throw new Error(id + '缺少州');
      for (const field of ['year_built', 'units', 'units_at_least']) if (a[field] != null && (!Number.isInteger(a[field]) || a[field] < 0)) throw new Error(`${id}.${field} 必须是非负整数或 null`);
    }
    this.precedence = clone(precedence ?? readJson(path.join(ROOT, 'lookup/precedence.json')));
    if (new Set(this.rules.map(r => r.team_rule_id)).size !== this.rules.length) throw new Error('规则编号重复');
    this.by_id = Object.fromEntries(this.rules.map(r => [r.team_rule_id, r]));
    for (const r of this.rules) {
      if (!CATEGORIES.has(r.category) || !['state', 'city'].includes(r.level)) throw new Error('规则类别或地区级别错误: ' + r.team_rule_id);
      if (![null, 'enacted', 'pending_bill', 'failed', 'withdrawn'].includes(r.lifecycle ?? null)) throw new Error('未知的规则通过状态: ' + r.team_rule_id);
      if (r.effective_date) dateInterval(r.effective_date); if (r.valid_through) dateInterval(r.valid_through); if (r.value_valid_through) dateInterval(r.value_valid_through);
      if ((r.level === 'city') !== r.jurisdiction.includes(', ')) throw new Error('规则地区与级别不一致: ' + r.team_rule_id);
      const a = r.applicability ?? {};
      for (const f of ['min_units', 'max_units', 'exempt_if_newer_than_years', 'covered_if_newer_than_years', 'owner_exempt_if_units_at_most']) if (a[f] != null && (!Number.isInteger(a[f]) || a[f] < 0)) throw new Error(`${r.team_rule_id}.${f} 必须是非负整数`);
      for (const f of ['built_on_or_before', 'built_before', 'built_after', 'built_on_or_after']) if (a[f]) dateInterval(a[f]);
    }
    this.edges = this.precedenceEdges(); this.review = clone(review ?? readJson(path.join(ROOT, 'lookup/review_pairs.json'))); this.review_pairs = this.reviewPairs();
  }
  static fromFiles(rulesPath = path.join(ROOT, 'work/rules_enriched.json'), addressesPath = path.join(ROOT, 'work/addresses_resolved.json')): LookupEngine {return new LookupEngine(loadRules(rulesPath), readJson(addressesPath));}
  private precedenceEdges(): Pair[] {
    const edges = new Map<string, Pair>();
    for (const e of this.precedence) {
      if (!e.basis || !e.source) throw new Error('取代关系必须有原文依据和来源');
      for (const y of this.rules) if (y.lifecycle === 'enacted' && y.category === e.category && stateOf(y) === e.state && matches(y, e.yielding))
        for (const p of this.rules) if (p.lifecycle === 'enacted' && p.category === y.category && stateOf(p) === e.state && p !== y && matches(p, e.prevailing)) edges.set(y.team_rule_id + '\0' + p.team_rule_id, {yielding: y.team_rule_id, prevailing: p.team_rule_id, entry: e});
    }
    const visit = (node: string, ancestors: Set<string>): void => {
      if (ancestors.has(node)) throw new Error('取代关系形成循环');
      for (const e of edges.values()) if (e.yielding === node) visit(e.prevailing, new Set([...ancestors, node]));
    };
    for (const e of edges.values()) visit(e.yielding, new Set()); return [...edges.values()];
  }
  private reviewPairs(): Pair[] {
    const pairs = new Map<string, Pair>(), put = (s: Rule, c: Rule, entry: Data): void => {pairs.set(s.team_rule_id + '\0' + c.team_rule_id, {yielding: s.team_rule_id, prevailing: c.team_rule_id, entry});};
    for (const s of this.rules) if (s.level === 'state' && s.lifecycle === 'enacted') {
      const q = (s.relations ?? []).filter((r: Data) => r.type === 'preempts_local').map((r: Data) => r.quote);
      if (!q.length) continue;
      for (const c of this.rules) if (c.level === 'city' && c.lifecycle === 'enacted' && c.category === s.category && stateOf(c) === stateOf(s)) put(s, c, {basis: q[0], source: s.source_url || s.citation, automatic: true});
    }
    for (const e of this.review) {
      if (!e.basis || !e.source) throw new Error('需人工复核的州/市关系必须有原文依据和来源');
      for (const s of this.rules) if (s.level === 'state' && s.lifecycle === 'enacted' && s.category === e.category && stateOf(s) === e.state && matches(s, e.state_rule))
        for (const c of this.rules) if (c.level === 'city' && c.lifecycle === 'enacted' && c.category === e.category && stateOf(c) === e.state && matches(c, e.city_rule)) put(s, c, e);
    }
    return [...pairs.values()];
  }
  static coverage(rule: Rule, address: Address, day: string): [string, Check[], [string, string][]] {
    const a = rule.applicability ?? {}, checks: Check[] = [], missing: [string, string][] = [], failures: string[] = [];
    const add = (field: string, fact: any, outcome: string, explanation: string): void => {checks.push({field, fact, outcome, explanation}); if (outcome === 'unknown') missing.push([field, explanation]); else if (outcome === 'excluded') failures.push(explanation);};
    const year = address.year_built ?? null, units = address.units ?? null, lower = address.units_at_least ?? null, conflict = units !== null && lower !== null && units < lower;
    const words: Data = {on_or_before: 'on or before', before: 'before', after: 'after', on_or_after: 'on or after'};
    const tests = (src: Data, emit: typeof add): void => {
      const basis = src.date_basis || a.date_basis || 'unspecified', exact = ['construction_date', 'certificate_of_occupancy'].includes(basis) ? address[basis] ?? null : null, actual = exact ? queryDate(exact) : null;
      const label = basis === 'certificate_of_occupancy' ? 'certificate of occupancy date' : 'construction date';
      const decide = (value: string, op: string): [string, any, string] => {
        const [start, end] = dateInterval(value), word = `the rule covers buildings with a ${label} ${words[op]} ${value}`;
        if (actual) {
          if (['on_or_before', 'after'].includes(op) && start !== end && start <= actual && actual <= end) return ['unknown', exact, 'the source gives the cutoff only to the year or month, so the boundary cannot be settled'];
          const passed = op === 'on_or_before' ? actual <= start : op === 'before' ? actual < start : op === 'after' ? actual > end : actual >= start;
          return [passed ? 'met' : 'excluded', exact, `the ${label} is ${exact}; ${word}`];
        }
        if (year === null) return ['unknown', null, `the data has no year built and no ${label}`];
        if (+start.slice(0, 4) === year) {
          if (basis === 'construction_date' && start === `${year}-01-01` && end === `${year}-12-31`) return [['on_or_before', 'on_or_after'].includes(op) ? 'met' : 'excluded', year, `year built ${year} is the cutoff year; ${word}`];
          return ['unknown', year, `year built is ${year}, the cutoff is ${value}, and the data has no exact ${label} to place the building before or after it`];
        }
        const passed = ['on_or_before', 'before'].includes(op) ? year < +start.slice(0, 4) : year > +end.slice(0, 4);
        return [passed ? 'met' : 'excluded', year, `year built is ${year}; ${word}`];
      };
      for (const [key, op] of [['built_on_or_before', 'on_or_before'], ['built_before', 'before'], ['built_after', 'after'], ['built_on_or_after', 'on_or_after']]) if (src[key]) {const [o, f, w] = decide(src[key], op); emit(key, f, o, w);}
      for (const key of ['exempt_if_newer_than_years', 'covered_if_newer_than_years']) if (src[key] != null) {
        const years = src[key], isExempt = key.startsWith('exempt'), [o, f, w] = decide(yearsBefore(day, years), isExempt ? 'on_or_before' : 'after'), built = actual ? +actual.slice(0, 4) : year;
        let why = w;
        if (o === 'met') why = isExempt ? `the building dates from ${pyStr(built)}, too old for the rule's exemption of housing first occupied in the previous ${years} years` : `the building dates from ${pyStr(built)}, inside the previous ${years} years the rule reaches`;
        else if (o === 'excluded') why = isExempt ? `the building dates from ${pyStr(built)}, inside the rule's exemption for housing first occupied in the previous ${years} years` : `the building dates from ${pyStr(built)}, older than the previous ${years} years the rule reaches`;
        emit(key, f, o, why);
      }
      for (const [field, isMin] of [['min_units', true], ['max_units', false]] as [string, boolean][]) {
        const t = src[field]; if (t == null) continue;
        if (conflict) {
          const byCount = (isMin ? units! >= t : units! <= t) ? 'met' : 'excluded', byLower = isMin ? lower! >= t ? 'met' : 'unknown' : lower! > t ? 'excluded' : 'unknown';
          emit(field, {units, units_at_least: lower}, byCount === byLower ? byCount : 'unknown', byCount !== byLower ? `the data gives ${units} units for the building but its land-use description shows at least ${lower}; the two cannot both be right, so the threshold of ${t} units is not settled by them` : `the exact count (${units}) and the land-use minimum (${lower}) agree on the threshold of ${t} units`); continue;
        }
        if (units !== null) emit(field, {units}, (isMin ? units >= t : units <= t) ? 'met' : 'excluded', `the building has ${units} units; the rule requires ${isMin ? 'at least' : 'no more than'} ${t}`);
        else if (lower !== null && lower >= t && isMin) emit(field, {units_at_least: lower}, 'met', `the land-use record shows at least ${lower} units, which meets the minimum of ${t}`);
        else if (lower !== null && lower > t && !isMin) emit(field, {units_at_least: lower}, 'excluded', `the building has at least ${lower} units, above the rule's limit of ${t}`);
        else emit(field, {units, units_at_least: lower}, 'unknown', `the data has no exact unit count, and the known minimum cannot settle the threshold of ${t} units`);
      }
    };
    tests(a, add);
    const get = (flats: Data): Check[] => {const got: Check[] = []; tests(flats, (field, fact, outcome, explanation) => {got.push({field, fact, outcome, explanation});}); return got;};
    for (const item of a.deferred ?? []) {
      const outcomes: string[] = []; let seen: any = null;
      for (const flats of item.flats_all || [item.flats]) {const got = get(flats), kinds = got.map(x => x.outcome); outcomes.push(kinds.includes('excluded') ? 'excluded' : kinds.includes('unknown') ? 'unknown' : 'met'); seen = seen || got[0]?.fact || null;}
      const n = item.note;
      if (outcomes.includes('met')) add('deferred:' + n, seen, 'met', `the building is outside the exemption (${n})`);
      else if (outcomes.every(x => x === 'excluded')) {if (item.conditional ?? true) add('deferred:' + n, seen, 'unknown', `the building may fall under an exemption that holds only if the owner filed or registered it (${n}); the data cannot show a filing`); else add('deferred:' + n, seen, 'excluded', `the building falls inside an exemption (${n})`);}
      else add('deferred:' + n, seen, 'unknown', `the data cannot place the building inside or outside an exemption (${n})`);
    }
    for (const item of a.alternatives ?? []) {
      const got = get(item.flats), seen = got[0]?.fact ?? null, kinds = got.map(x => x.outcome), label = 'alternative:' + item.also;
      if (kinds.includes('excluded')) add(label, seen, 'unknown', `the stated limit leaves this building out, but the text also covers ${item.also}, which the data cannot show`);
      else if (kinds.includes('unknown')) add(label, seen, 'unknown', got.find(x => x.outcome === 'unknown')!.explanation);
      else add(label, seen, 'met', got[0]?.explanation ?? 'the building is inside the stated limit');
    }
    if (a.owner_dependent) {
      const maximum = a.owner_exempt_if_units_at_most, knownLower = units !== null ? conflict ? null : units : lower;
      if (maximum != null && knownLower !== null && knownLower > maximum) add('owner_dependent', {units_lower: knownLower, exemption_max_units: maximum}, 'met', `the building has at least ${knownLower} units, so the owner-based exception (limited to ${maximum} units) cannot apply`);
      else add('owner_dependent', null, 'unknown', 'coverage depends on who the owner is or whether the owner lives there, and the data has no owner information');
    }
    if (a.other) {const kind = a.other_kind || (a.contract ? 'building' : otherKind(a.other)); add('other', null, kind === 'building' ? 'unknown' : 'note', (kind === 'building' ? 'the data cannot settle this condition: ' : 'condition stated in the source: ') + a.other);}
    if (truth(a.program_notes)) add('program_notes', null, 'note', `kinds of housing the data cannot show may be exempt (${slice(a.program_notes.join('; '), 0, 300)})`);
    if (a.per_tenancy) add('per_tenancy', null, 'note', 'individual tenancies can differ: ' + a.per_tenancy);
    if (rule.coverage_note) add('coverage_note', null, 'note', 'individual tenancies can differ: ' + rule.coverage_note);
    if (rule.coverage_missing) add('coverage_missing', null, 'unknown', 'coverage also depends on facts not in the data: ' + rule.coverage_missing);
    return [failures.length ? 'excluded' : missing.length ? 'unknown' : 'met', checks, missing];
  }
  private initial(rule: Rule, address: Address, asOf: string): [string | null, string, Data] {
    const day = queryDate(asOf), trace: Data = {team_rule_id: rule.team_rule_id, steps: [], missing_facts: [], source: {citation: rule.citation, source_url: rule.source_url ?? null, retrieved: rule.retrieved ?? null, quoted_span: rule.quoted_span ?? null, coverage_sources: rule.coverage_sources ?? [], coverage_quotes: rule.applicability?.coverage_quotes || [], date_source: rule.date_source ?? null, fact_corrections: rule.overrides_applied || []}};
    const step = (n: number, o: string, f: any, e: string): void => {trace.steps.push({step: n, outcome: o, facts: f, explanation: e});};
    const done = (r: string | null, e: string, n: number): [string | null, string, Data] => {Object.assign(trace, {result: r, stopped_at_step: n, explanation: e}); return [r, e, trace];};
    if (stateOf(rule) !== address.state) {step(1, 'excluded', {state: address.state}, 'the address is in a different state'); return done(null, 'the address is in a different state', 1);}
    if (rule.level === 'city') {
      const city = address.legal_city ?? null;
      if (city === null && !address.jurisdiction_known) {
        const msg = `the legal city of this address could not be determined, so it is not known whether it lies in ${rule.jurisdiction}`;
        step(1, 'unknown', {legal_city: null}, msg); trace.missing_facts = [{field: 'legal_city', explanation: msg}];
        if (['failed', 'withdrawn'].includes(rule.lifecycle ?? '')) {step(2, 'excluded', {lifecycle: rule.lifecycle}, 'the measure failed or was withdrawn'); return done(null, 'the measure failed or was withdrawn', 2);} return done('unknown', msg, 1);
      }
      if (city !== rule.jurisdiction) {step(1, 'excluded', {legal_city: city, resolved_by: address.resolved_by ?? null}, 'the address is in a different city'); return done(null, 'the address is in a different city', 1);}
    }
    step(1, 'met', {state: address.state, legal_city: address.legal_city ?? null, resolved_by: address.resolved_by ?? null}, "the address is inside the rule's jurisdiction");
    if (['failed', 'withdrawn'].includes(rule.lifecycle ?? '')) {step(2, 'excluded', {lifecycle: rule.lifecycle}, 'the measure failed or was withdrawn'); return done(null, 'the measure failed or was withdrawn', 2);}
    step(2, 'met', {lifecycle: rule.lifecycle ?? null}, 'the measure has not failed');
    if (rule.lifecycle === 'pending_bill') {step(3, 'pending', {lifecycle: 'pending_bill'}, 'this is still a proposal, not enacted law'); return done('pending', `The address is in ${rule.jurisdiction}, but this is a proposal that has not become law`, 3);}
    if (rule.lifecycle !== 'enacted') {const msg = 'the record does not say whether the measure was enacted, and the extraction-time status is not used in its place'; step(3, 'unknown', {lifecycle: rule.lifecycle ?? null}, msg); trace.missing_facts = [{field: 'lifecycle', explanation: msg}]; return done('unknown', msg, 3);}
    step(3, 'met', {lifecycle: 'enacted'}, 'the rule is enacted'); const status = statusOn(rule, asOf);
    if (status === 'not_yet_effective' || status === 'unknown') {
      const msg = status === 'unknown' ? `the effective date is known only to the year or month, and the query date ${asOf} falls inside that span` : `Enacted, but it takes effect on ${rule.effective_date}, after the query date ${asOf}`;
      step(4, status, {effective_date: rule.effective_date, as_of: asOf}, msg); if (status === 'unknown') trace.missing_facts = [{field: 'effective_date', explanation: msg}]; return done(status, msg, 4);
    }
    step(4, 'met', {effective_date: rule.effective_date ?? null, as_of: asOf}, 'no effective date later than the query date');
    if (rule.valid_through && day > dateInterval(rule.valid_through)[1]) {const msg = `the figure in this rule is published for a period ending ${rule.valid_through} and is not reported for ${asOf}`; step(4, 'excluded', {valid_through: rule.valid_through, as_of: asOf}, msg); return done(null, msg, 4);}
    const noDate = !rule.effective_date;
    step(5, 'met', {effective_date: rule.effective_date ?? null, date_source: rule.date_source ?? null}, noDate ? 'the source states no effective date; treated as in force' : 'the effective date has passed');
    const [coverage, checks, missing] = LookupEngine.coverage(rule, address, day); step(6, coverage, checks, 'checked building date, unit count, owner and other coverage conditions'); trace.missing_facts = missing.map(([field, explanation]) => ({field, explanation}));
    const kinds = coverage === 'excluded' ? ['excluded'] : coverage === 'unknown' ? ['unknown'] : ['met', 'note'], details = checks.filter(c => kinds.includes(c.outcome)).map(c => c.explanation);
    let msg = details.length ? details.join('; ') : `The address is in ${rule.jurisdiction} and the rule lists no further coverage condition`; if (noDate) msg += '; the source states no effective date';
    return done(coverage === 'excluded' ? null : coverage === 'unknown' ? 'unknown' : 'applies', msg, coverage === 'met' ? 8 : 6);
  }
  evaluate(addressId: string, asOf = DEFAULT_DATE): [LookupRow[], Data] {
    queryDate(asOf); if (!Object.hasOwn(this.addresses, addressId)) throw new Error("'" + addressId + "'"); const address = this.addresses[addressId];
    const results: Record<string, any> = {}, traces: Record<string, Data> = {};
    for (const rule of this.rules) {const [r, e, t] = this.initial(rule, address, asOf); setKey(traces, rule.team_rule_id, t); if (r) setKey(results, rule.team_rule_id, {team_rule_id: rule.team_rule_id, result: r, explanation: e, conflict_flag: false});}
    const visited = new Set<string>();
    const resolve = (rid: string): void => {
      if (visited.has(rid)) return; visited.add(rid); const candidate = Object.hasOwn(results, rid) ? results[rid] : undefined; if (!candidate || !['applies', 'unknown'].includes(candidate.result)) return;
      const edges = this.edges.filter(e => e.yielding === rid); for (const e of edges) resolve(e.prevailing);
      const applicable = edges.filter(e => Object.hasOwn(results, e.prevailing) && results[e.prevailing].result === 'applies'), uncertain = edges.filter(e => Object.hasOwn(results, e.prevailing) && results[e.prevailing].result === 'unknown');
      if (applicable.length && candidate.result === 'applies') {candidate.result = 'superseded'; candidate.explanation += `; ${applicable.map(e => this.by_id[e.prevailing].citation).join(', ')} applies to this address, so this rule yields to it. Basis: ${applicable[0].entry.basis}`;}
      else if (uncertain.length) {candidate.result = 'unknown'; candidate.explanation += '; it also depends on whether the city rule covers this address, which the data cannot settle';}
      if (applicable.length || uncertain.length) {
        traces[rid].steps.push({step: 7, outcome: candidate.result, facts: [...applicable, ...uncertain].map(e => ({rule: e.prevailing, result: results[e.prevailing].result, basis: e.entry.basis})), explanation: candidate.explanation}); traces[rid].stopped_at_step = 7;
        if (uncertain.length && !applicable.length) traces[rid].missing_facts.push({field: 'precedence_coverage', explanation: 'whether the prevailing city rule covers this address is not known'});
      }
    };
    for (const rid of Object.keys(results)) resolve(rid); const pairs: string[][] = [];
    for (const e of [...this.review_pairs].sort((a, b) => cmp([a.yielding, a.prevailing], [b.yielding, b.prevailing]))) {
      const s = e.yielding, c = e.prevailing;
      if (!Object.hasOwn(results, s) || !Object.hasOwn(results, c) || this.edges.some(x => x.yielding === s && x.prevailing === c || x.yielding === c && x.prevailing === s)) continue;
      results[s].conflict_flag = results[c].conflict_flag = true; pairs.push([s, c]);
    }
    for (const [rid, r] of Object.entries(results)) {
      const rule = this.by_id[rid];
      if (rule.value_valid_through && queryDate(asOf) > dateInterval(rule.value_valid_through)[1]) {
        r.explanation += '; ' + rule.value_expiry_note;
        traces[rid].missing_facts.push({field: 'current_value', explanation: rule.value_expiry_note});
      }
      if (r.conflict_flag) r.explanation += '; ' + REVIEW_NOTE;
      const sources = unique<string>((rule.overrides_applied ?? []).filter((c: Data) => Object.hasOwn(c.after ?? {}, 'effective_date') && c.source).map((c: Data) => c.source)).sort(); if (sources.length) r.explanation += '; effective date taken from: ' + sources.join(', ');
      const retrieved = rule.retrieved || (rule.sources ?? []).find((s: Data) => s.retrieved)?.retrieved || 'not recorded';
      r.explanation = sentence(r.explanation) + ` Source: ${rule.citation}, ${pyStr(Object.hasOwn(rule, 'source_url') ? rule.source_url : '')} (retrieved ${retrieved}). ${DISCLAIMER}`;
      const t = traces[rid]; if (t.stopped_at_step === 8) t.steps.push({step: 7, outcome: 'met', facts: [], explanation: 'no applicable rule requires this one to yield'}, {step: 8, outcome: r.result, facts: [], explanation: 'coverage conditions are met'});
      Object.assign(t, {result: r.result, explanation: r.explanation, conflict_flag: r.conflict_flag, source: {citation: rule.citation, source_url: rule.source_url ?? null, retrieved, quoted_span: rule.quoted_span ?? null, coverage_sources: rule.coverage_sources ?? [], date_source: rule.date_source ?? null, fact_corrections: rule.overrides_applied || []}});
    }
    return [sortedEntries(results).map(([, v]) => v), {rules: sortedEntries(traces).map(([, v]) => v), conflict_pairs: pairs}];
  }
  lookup(id: string, asOf = DEFAULT_DATE): LookupRow[] {return this.evaluate(id, asOf)[0];}
  all(asOf = DEFAULT_DATE): [Data, Data] {const lookups: Data = {}, addresses: Data = {}; for (const id of Object.keys(this.addresses).sort()) {const [rows, audit] = this.evaluate(id, asOf); setKey(lookups, id, rows); setKey(addresses, id, audit);} return [{as_of: asOf, lookups}, {as_of: asOf, disclaimer: DISCLAIMER, addresses}];}
  exportedRules(asOf = DEFAULT_DATE, lookupPayload?: Data): Data[] {
    const payload = lookupPayload ?? this.all(asOf)[0], flagged = new Set(Object.values(payload.lookups).flatMap((rows: any) => rows.filter((r: Data) => r.conflict_flag).map((r: Data) => r.team_rule_id)));
    return this.rules.map(rule => {
      const r: Data = Object.fromEntries(FIELDS.map(k => [k, clone(rule[k] ?? null)])); r.status = statusOn(rule, asOf); if (r.status === 'unknown') throw new Error(`规则${rule.team_rule_id}缺少准确的通过状态或生效日期，无法导出四种状态之一`);
      r.overrides = this.edges.filter(e => e.prevailing === rule.team_rule_id).map(e => e.yielding).sort();
      r.interaction = unique<string>(this.edges.filter(e => [e.yielding, e.prevailing].includes(rule.team_rule_id)).map(e => e.entry.basis)).sort().join('; ') || (rule.interaction ?? null);
      r.conflict_flag = flagged.has(rule.team_rule_id); r.conflict_note = r.conflict_flag ? sentence(REVIEW_NOTE) : null; r.retrieved = rule.retrieved ?? null;
      r.applicability = clone(rule.applicability || {}); r.coverage_sources = clone(rule.coverage_sources ?? []); r.date_source = rule.date_source ?? null; r.relations = clone(rule.relations || []); r.fact_corrections = clone(rule.overrides_applied || []);
      if (rule.valid_through) r.valid_through = rule.valid_through;
      if (rule.value_valid_through) {
        r.value_valid_through = rule.value_valid_through;
        if (queryDate(asOf) > dateInterval(rule.value_valid_through)[1]) {
          r.value_status = 'missing_current_value';
          r.requirement = (r.requirement || '') + ' ' + rule.value_expiry_note;
        }
      }
      r.disclaimer = DISCLAIMER; return r;
    });
  }
}
export const lookup = (id: string, asOf = DEFAULT_DATE): LookupRow[] => LookupEngine.fromFiles().lookup(id, asOf);
