import path from 'node:path';
import type {Data} from '../types.js';
import {clone, counter, equal, readJson, repr, setKey, sortedEntries} from '../util.js';
import {DISCLAIMER, ROOT, pack, matches, queryDate} from '../lookup/common.js';
import {LookupEngine} from '../lookup/engine.js';
export class ChangeTracker {
  tests: Data[]; rule_map: Data; cache: Data = {}; audit_cache: Data = {};
  constructor(public engine: LookupEngine, tests?: Data[], ruleMap?: Data) {this.tests = clone(tests ?? readJson(path.join(pack(), 'dev/change_tests.json'))); this.rule_map = clone(ruleMap ?? readJson(path.join(ROOT, 'changes/test_rule_map.json')));}
  mapped(id: string): string[] {if (!Object.hasOwn(this.rule_map, id)) throw new Error('变更题缺少法规对照配置: ' + id); return this.engine.rules.filter(r => matches(r, this.rule_map[id])).map(r => r.team_rule_id).sort();}
  private lookups(day: string): Data {queryDate(day); if (!this.cache[day]) {const [out, audit] = this.engine.all(day); this.cache[day] = out.lookups; this.audit_cache[day] = audit.addresses;} return this.cache[day];}
  private signature(rows: Data[], relevant: Set<string>): Data {return Object.fromEntries(rows.filter(r => relevant.has(r.team_rule_id)).map(r => [r.team_rule_id, [r.result, r.conflict_flag]]));}
  run(dateOverrides: Data = {}): [Data, Data] {
    const ids = this.tests.map(c => c.test_id); if (Object.keys(dateOverrides).some(k => !ids.includes(k))) throw new Error('日期配置含未知题号'); const output: Data = {}, audit: Data = {disclaimer: DISCLAIMER, tests: {}};
    for (const supplied of this.tests) {
      const c = clone(supplied), testId = c.test_id, replacement = dateOverrides[testId] || {}, allowed = c.type === 'as_of' ? ['as_of_before', 'as_of_after'] : ['as_of'];
      if (Object.keys(replacement).some(k => !allowed.includes(k))) throw new Error('只能覆盖该题实际使用的查询日期：' + allowed.sort().join(', ')); Object.assign(c, replacement);
      const mapping: Record<string, string[]> = Object.fromEntries([...c.rule_ids, ...c.conflict_with || []].map(id => [id, this.mapped(id)]));
      const missing = Object.entries(mapping).filter(([, v]) => !v.length).map(([id]) => id), relevant = new Set<string>(c.rule_ids.flatMap((id: string) => mapping[id])), conflictRules = new Set<string>((c.conflict_with || []).flatMap((id: string) => mapping[id])), affected: string[] = [], conflicts: string[] = [], evidence: Data = {}, notes: string[] = [];
      if (c.type === 'as_of') {
        const before = c.as_of_before, after = c.as_of_after, old = this.lookups(before), next = this.lookups(after); notes.push(`Compared the lookup results on ${before} and ${after}`);
        for (const id of Object.keys(this.engine.addresses).sort()) {const previous = this.signature(old[id], relevant), current = this.signature(next[id], relevant); if (!equal(previous, current)) {affected.push(id); evidence[id] = {before: previous, after: current};} if (relevant.size && conflictRules.size) {const pairs = [...this.audit_cache[before][id].conflict_pairs, ...this.audit_cache[after][id].conflict_pairs]; if (pairs.some(([s, city]: string[]) => relevant.has(s) && conflictRules.has(city))) conflicts.push(id);}}
      } else {
        const day = c.as_of, lookups = this.lookups(day); notes.push('Query date ' + day);
        if (['boundary', 'pending'].includes(c.type)) {
          const results = c.type === 'boundary' ? ['applies', 'unknown'] : ['pending']; for (const [id, rows] of sortedEntries<Data[]>(lookups)) {const chosen = rows.filter(r => relevant.has(r.team_rule_id) && results.includes(r.result)); if (chosen.length) {affected.push(id); evidence[id] = chosen;}}
          if (c.type === 'boundary') {const counts = counter(affected.map(id => this.engine.addresses[id].legal_city || 'city not resolved')); notes.push('Affected addresses by city: ' + (sortedEntries(counts).map(([city, n]) => `${city} ${n}`).join(', ') || 'none, because no city ban is in the rule set'));} else notes.push('The list shows the addresses the bills would cover if enacted; they are reported as pending, not as law');
        } else if (c.type === 'negative') {
          const targets: string[] = c.states || [], violations: [string, string][] = []; for (const [id, rows] of sortedEntries<Data[]>(lookups)) {if (targets.length && !targets.includes(this.engine.addresses[id].state)) continue; for (const row of rows) {const r = this.engine.by_id[row.team_rule_id], bars = (r.relations || []).some((r: Data) => r.type === 'preempts_local'); if (row.result === 'applies' && r.category === 'rent_increase_limits' && !bars) violations.push([id, row.team_rule_id]);}}
          if (violations.length) throw new Error('反例检查失败：麻州地址出现适用的涨租上限: [' + violations.map(([id, r]) => `(${repr(id)}, ${repr(r)})`).join(', ') + ']');
          if ([...relevant].some(id => !['failed', 'withdrawn'].includes(this.engine.by_id[id].lifecycle || ''))) throw new Error('反例检查失败：公投规则未记为 failed'); notes.push('The affected list is empty; every target address was checked and none has an applicable rent cap'); if (relevant.size) notes.push('The ballot measure is recorded as failed');
        } else throw new Error('不支持的变更题类型: ' + c.type);
      }
      if (missing.length) notes.push(`Rules missing from the extracted set: ${missing.join(', ')}; this answer covers only what the extracted rules support and is incomplete`); notes.push(DISCLAIMER);
      setKey(output, testId, {affected_address_ids: affected.sort(), conflict_flag_address_ids: conflicts.sort(), notes: notes.join('. ')}); setKey(audit.tests, testId, {query_dates: Object.fromEntries(['as_of', 'as_of_before', 'as_of_after'].filter(k => Object.hasOwn(c, k)).map(k => [k, c[k]])), rule_mapping: mapping, missing_rules: missing, evidence});
    }
    return [output, audit];
  }
}
