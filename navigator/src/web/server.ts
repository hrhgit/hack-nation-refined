import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import type {Data, Query} from '../types.js';
import {cmp, counter, csvRecords, escapeRegex, isObject, length, pyStr, readJson, slice, sortedEntries, unique} from '../util.js';
import {ChangeTracker} from '../changes/engine.js';
import {DEFAULT_DATE, DISCLAIMER, ROOT, pack, queryDate} from '../lookup/common.js';
import {LookupEngine, loadRules, stateOf, statusOn} from '../lookup/engine.js';
export const STATIC = path.join(ROOT, 'web/static');
const CATEGORY_ORDER = ['rent_increase_limits', 'just_cause_eviction', 'security_deposits', 'application_screening_fees', 'screening_restrictions', 'algorithmic_rent_setting'];
const RULE_FIELDS = ['team_rule_id', 'jurisdiction', 'level', 'category', 'title', 'requirement', 'key_value', 'coverage_conditions', 'exemptions', 'penalty', 'interaction', 'effective_date', 'valid_through', 'citation', 'source_doc_id', 'source_url', 'quoted_span', 'confidence', 'conflict_flag', 'conflict_note', 'retrieved', 'lifecycle', 'packet_id', 'date_source'];
const ADDRESS_FIELDS = ['address_id', 'street_address', 'postal_city', 'legal_city', 'state', 'zip', 'year_built', 'units', 'units_at_least', 'resolved_by'];
export class NotFound extends Error {}
const work = (f: string): string => path.join(ROOT, 'work', f);
const engine = (): LookupEngine => new LookupEngine(loadRules(), readJson(work('addresses_resolved.json')));
const documents = (): Data => readJson(work('index.json')).docs;
const extractionProgress = (): Data => {const c = readJson(work('audit.json')).counts; return {done: c.packets_done, total: c.packets_total};};
const fields = (row: Data, keys: string[]): Data => Object.fromEntries(keys.map(k => [k, row[k] ?? null]));
const first = (q: Query, k: string, d = ''): string => q[k]?.[0] ?? d;
export function ruleView(rule: Data, asOf: string, eng: LookupEngine, docs: Data): Data {
  const view = fields(rule, RULE_FIELDS); view.status = statusOn(rule as any, asOf); const sources = rule.sources?.length ? rule.sources : [{doc_id: rule.source_doc_id ?? null, url: rule.source_url ?? null, retrieved: rule.retrieved ?? null, quoted_span: rule.quoted_span ?? null}];
  view.sources = sources.map((s: Data) => ({...fields(s, ['doc_id', 'url', 'retrieved', 'quoted_span']), origin: docs[s.doc_id]?.origin ?? null})); view.fact_corrections = rule.overrides_applied || []; view.coverage_sources = rule.coverage_sources ?? [];
  const edges = [...eng.edges].sort((a, b) => cmp([a.yielding, a.prevailing], [b.yielding, b.prevailing])); view.yields_to = edges.filter(e => e.yielding === rule.team_rule_id).map(e => ({team_rule_id: e.prevailing, citation: eng.by_id[e.prevailing].citation, basis: e.entry.basis})); view.prevails_over = edges.filter(e => e.prevailing === rule.team_rule_id).map(e => ({team_rule_id: e.yielding, citation: eng.by_id[e.yielding].citation, basis: e.entry.basis})); return view;
}
export function apiMeta(_q: Query): Data {return {disclaimer: DISCLAIMER, default_date: DEFAULT_DATE, categories: CATEGORY_ORDER, addresses: sortedEntries<Data>(readJson(work('addresses_resolved.json'))).map(([, a]) => fields(a, ADDRESS_FIELDS))};}
export function apiLookup(q: Query): Data {
  const id = first(q, 'address_id'), asOf = first(q, 'as_of', DEFAULT_DATE); queryDate(asOf); const rules = loadRules(), addresses = readJson(work('addresses_resolved.json')); if (!Object.hasOwn(addresses, id)) throw new NotFound('Unknown address id: ' + id); const address = {...addresses[id]}, entered: Data = {};
  for (const f of ['year_built', 'units']) {const value = first(q, f); if (value) {if (!/^\d{1,4}$/.test(value)) throw new Error(f + ' must be a whole number'); entered[f] = address[f] = +value;}}
  const started = performance.now(), eng = new LookupEngine(rules, {[id]: address}), [results, audit] = eng.evaluate(id, asOf), elapsed = Math.round((performance.now() - started) * 10) / 10, docs = documents(), traces: Data = Object.fromEntries(audit.rules.map((t: Data) => [t.team_rule_id, t]));
  const rows = results.map(row => ({...row, rule: ruleView(eng.by_id[row.team_rule_id], asOf, eng, docs), steps: traces[row.team_rule_id].steps, missing_facts: traces[row.team_rule_id].missing_facts || []})), leftOut = sortedEntries<Data>(traces).filter(([, t]) => !t.result && t.stopped_at_step !== 1).map(([rid, t]) => ({rule: ruleView(eng.by_id[rid], asOf, eng, docs), steps: t.steps, stopped_at_step: t.stopped_at_step}));
  return {as_of: asOf, computed_ms: elapsed, address, entered_facts: entered, results: rows, left_out: leftOut, conflict_pairs: audit.conflict_pairs, extraction: extractionProgress(), disclaimer: DISCLAIMER};
}
export function apiRules(q: Query): Data {const asOf = first(q, 'as_of', DEFAULT_DATE); queryDate(asOf); const eng = engine(), docs = documents(); return {as_of: asOf, disclaimer: DISCLAIMER, extraction: extractionProgress(), rules: eng.rules.map(r => ruleView(r, asOf, eng, docs))};}
export function apiChanges(_q: Query): Data {
  const eng = engine(), tracker = new ChangeTracker(eng), [output, audit] = tracker.run(), cities = counter(Object.values(eng.addresses).map(a => a.legal_city || 'city not resolved'));
  const tests = tracker.tests.map(c => {
    const id = c.test_id, detail = audit.tests[id], transitions = new Map<string, {rid: string; before: string | null; after: string | null; count: number}>();
    const add = (rid: string, before: string | null, after: string | null): void => {const k = JSON.stringify([rid, before, after]); if (!transitions.has(k)) transitions.set(k, {rid, before, after, count: 0}); transitions.get(k)!.count++;};
    for (const evidence of Object.values<any>(detail.evidence)) {if (isObject(evidence)) {for (const rid of unique<string>([...Object.keys(evidence.before), ...Object.keys(evidence.after)]).sort()) add(rid, evidence.before[rid]?.[0] ?? null, evidence.after[rid]?.[0] ?? null);} else for (const r of evidence) add(r.team_rule_id, null, r.result);}
    const byCity = counter(output[id].affected_address_ids.map((aid: string) => eng.addresses[aid].legal_city || 'city not resolved')), flagged = counter(output[id].conflict_flag_address_ids.map((aid: string) => eng.addresses[aid].legal_city || 'city not resolved')); let states = new Set<string>(c.states || []);
    if (!states.size) states = new Set<string>([...Object.values<string[]>(detail.rule_mapping).flat().map(r => stateOf(eng.by_id[r])), ...output[id].affected_address_ids.map((aid: string) => eng.addresses[aid].state)]);
    const scope = sortedEntries(cities).filter(([city]) => states.has(city.split(', ').at(-1)!)).map(([city, total]) => ({city, total, affected: byCity[city] || 0, flagged: flagged[city] || 0}));
    return {test: c, output: output[id], query_dates: detail.query_dates, missing_rules: detail.missing_rules, rule_mapping: Object.fromEntries(Object.entries<string[]>(detail.rule_mapping).map(([external, ids]) => [external, ids.map(rid => ({team_rule_id: rid, citation: eng.by_id[rid].citation, title: eng.by_id[rid].title ?? null}))])), transitions: [...transitions.values()].sort((a, b) => cmp([a.rid, pyStr(a.before), pyStr(a.after)], [b.rid, pyStr(b.before), pyStr(b.after)])).map(t => ({team_rule_id: t.rid, citation: eng.by_id[t.rid].citation, before: t.before, after: t.after, addresses: t.count})), cities: scope};
  });
  return {tests, addresses_by_city: Object.fromEntries(sortedEntries(cities)), extraction: extractionProgress(), disclaimer: DISCLAIMER};
}
export function apiPipeline(_q: Query): Data {
  const eng = engine(), docs = documents(), audit = readJson(work('audit.json')), manifest = csvRecords(fs.readFileSync(path.join(pack(), 'corpus/corpus_manifest.csv'), 'utf8')), perDoc: Record<string, number> = {};
  for (const r of eng.rules) for (const id of unique<string>((r.sources?.length ? r.sources : [{doc_id: r.source_doc_id}]).map((s: Data) => s.doc_id))) perDoc[id] = (perDoc[id] || 0) + 1;
  const [lookups] = eng.all(DEFAULT_DATE); return {as_of: DEFAULT_DATE, disclaimer: DISCLAIMER, extraction: {...audit.counts, ran_at: audit.ran_at, pipeline_version: audit.pipeline_version}, corpus: {manifest_documents: manifest.length, manifest_with_text: manifest.filter(r => r.text_file).length, indexed_documents: Object.keys(docs).length, indexed_with_text: Object.values<Data>(docs).filter(d => !d.no_text).length, added_documents: Object.values<Data>(docs).filter(d => d.origin !== 'starter').length}, rules: {total: eng.rules.length, by_status: counter(eng.rules.map(r => statusOn(r, DEFAULT_DATE))), precedence_links: eng.edges.length}, addresses: {total: Object.keys(eng.addresses).length, resolved_by: counter(Object.values(eng.addresses).map(a => a.resolved_by ?? null))}, lookups: counter(Object.values<Data[]>(lookups.lookups).flat().map(r => r.result)), documents: sortedEntries<Data>(docs).map(([id, d]) => ({doc_id: id, jurisdictions: d.jurisdictions ?? null, url: d.url ?? null, source_type: d.source_type ?? null, origin: d.origin ?? null, no_text: Boolean(d.no_text), packets: (d.packets || []).length, rules: perDoc[id] || 0}))};
}
export function apiSource(q: Query): Data {
  const id = first(q, 'doc_id'), quote = first(q, 'quote'); if (!/^[A-Z]\d{3}$/.test(id)) throw new Error('doc_id must look like D024'); const doc = documents()[id]; if (!doc) throw new NotFound('Unknown document: ' + id); const file = path.join(doc.origin === 'starter' ? path.join(pack(), 'corpus') : path.join(ROOT, 'corpus_extra'), 'text', id + '.txt'); if (!fs.existsSync(file)) throw new NotFound('No saved text for ' + id);
  const text = fs.readFileSync(file, 'utf8').replace(/\r\n?/g, '\n'), header = Object.fromEntries(text.split('\n').slice(0, 2).filter(l => l.includes(': ')).map(l => {const i = l.indexOf(': '); return [l.slice(0, i), l.slice(i + 2)];})), payload: Data = {doc_id: id, origin: doc.origin ?? null, url: header.SOURCE || doc.url || null, retrieved: header.RETRIEVED ?? null, jurisdictions: doc.jurisdictions ?? null, characters: length(text), found: false}, tokens = quote.split(/\s+/).filter(Boolean);
  if (tokens.length) {const m = new RegExp(tokens.map(escapeRegex).join('\\s+')).exec(text); if (m) {const start = length(text.slice(0, m.index)), end = start + length(m[0]); Object.assign(payload, {found: true, offset: start, before: slice(text, Math.max(0, start - 1500), start), match: m[0], after: slice(text, end, end + 1500)});}} return payload;
}
export const ROUTES: Record<string, (q: Query) => Data> = {'/api/meta': apiMeta, '/api/lookup': apiLookup, '/api/rules': apiRules, '/api/changes': apiChanges, '/api/pipeline': apiPipeline, '/api/source': apiSource};
export function createServer(): http.Server {
  return http.createServer((req, res) => {
    const send = (status: number, data: string | Buffer, type: string): void => {const body = Buffer.isBuffer(data) ? data : Buffer.from(data); res.writeHead(status, {'Content-Type': type, 'Content-Length': body.length, 'Cache-Control': 'no-store'}); res.end(body);};
    if (req.method !== 'GET') {send(501, "Unsupported method ('" + req.method + "')", 'text/html; charset=utf-8'); return;}
    try {
      // Preserve the unnormalized path for the same static traversal checks.
      const rawPath = (req.url || '/').split('?')[0], query = new URLSearchParams((req.url || '').split('?').slice(1).join('?')), q: Query = Object.create(null); for (const [k, v] of query) if (v) (q[k] ??= []).push(v);
      if (Object.hasOwn(ROUTES, rawPath)) {try {send(200, JSON.stringify(ROUTES[rawPath](q)), 'application/json; charset=utf-8');} catch (e) {const error = e as Error; const status = e instanceof NotFound ? 404 : 'code' in error ? 500 : 400; send(status, JSON.stringify({error: error.message, disclaimer: DISCLAIMER}), 'application/json; charset=utf-8');} return;}
      const name = rawPath === '/' ? 'index.html' : rawPath.replace(/^\/+/, ''), target = path.resolve(STATIC, name), root = fs.realpathSync(STATIC);
      if (!fs.existsSync(target) || !fs.statSync(target).isFile() || !fs.realpathSync(target).startsWith(root + path.sep)) {send(404, 'Not found', 'text/plain; charset=utf-8'); return;}
      const types: Record<string, string> = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png'}; send(200, fs.readFileSync(target), (types[path.extname(target)] || 'application/octet-stream') + '; charset=utf-8');
    } catch {send(500, JSON.stringify({error: '无法读取服务数据。', disclaimer: DISCLAIMER}), 'application/json; charset=utf-8');}
  });
}
export async function main(argv = process.argv.slice(2)): Promise<void> {
  let host = '127.0.0.1', port = 8000; for (let i = 0; i < argv.length; i++) {if (argv[i] === '--host') host = argv[++i]; else if (argv[i] === '--port') port = Number(argv[++i]); else if (['--help', '-h'].includes(argv[i])) {console.log('地址查询网页：npm start -- --host 127.0.0.1 --port 8000'); return;} else throw new Error('未知参数：' + argv[i]);}
  if (!Number.isInteger(port) || port < 0 || port > 65535 || !host) throw new Error('端口必须在 0 到 65535 之间，地址不能为空'); const server = createServer(); await new Promise<void>((resolve, reject) => {server.once('error', reject); server.listen(port, host, resolve);}); const address = server.address(); console.log(`网页已启动：http://${host}:${typeof address === 'object' ? address!.port : port}  （按 Ctrl+C 停止）${DISCLAIMER}`);
  const stop = (): void => {server.close(); server.closeAllConnections();}; process.once('SIGINT', stop); process.once('SIGTERM', stop);
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main().catch(e => {console.error(e.message); process.exitCode = 1;});
