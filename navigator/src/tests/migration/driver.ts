// Test-only JSON adapter. Production entry points never import this module.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import readline from 'node:readline';
import type {Data, Rule} from '../../types.js';
import {clone, readJson, sha256, stable, writeText, walk} from '../../util.js';
import * as conditions from '../../nav/conditions.js';
import * as facts from '../../nav/facts.js';
import {extractJsonObjects} from '../../nav/parse.js';
import {check} from '../../nav/schema.js';
import {cleanText, splitBlocks, selectBlocks} from '../../nav/textutil.js';
import {DocIndex} from '../../nav/spans.js';
import {chapterOf} from '../../nav/chapters.js';
import {KNOWN_JURISDICTIONS, STATE_NAMES, ROOT, Paths, defaultPaths, loadSchema} from '../../nav/config.js';
import {ApiConfig, ApiError, ChatClient, answer, select, runApi} from '../../nav/api.js';
import {checkFinal, checkRecord, loadCards, renderCore, toolSpecs, runAgentApi} from '../../nav/agent.js';
import {loadCorpus} from '../../nav/corpus.js';
import {buildDocPackets, renderPacket, renderPrompt, prepare} from '../../nav/packets.js';
import {Validator, pendingPackets, runIngest} from '../../nav/ingest.js';
import {dateInterval, queryDate} from '../../lookup/common.js';
import {integer, unitLowerBound, parseBatch, loadAddresses, CensusResolver} from '../../lookup/addresses.js';
import {LookupEngine, loadRules} from '../../lookup/engine.js';
import {render as renderReview} from '../../lookup/review.js';
import {requestsReport} from '../../lookup/cli.js';
import {ChangeTracker} from '../../changes/engine.js';
import {ROUTES} from '../../web/server.js';
const digest = (v: any): string => sha256(JSON.stringify(stable(v)));
const ingestionView = (p: Paths): Data => {const r = runIngest(p, undefined, false); return {rules: r.rules, counts: r.counts, states: r.states, pending: pendingPackets(r), rejected: r.rejected, problems: r.problems, parse_problems: r.parse_problems};};
export async function execute(c: Data): Promise<any> {
  const a = c.args || {}, op = c.op;
  if (op === 'parse') return extractJsonObjects(a.text);
  if (op === 'clean') return cleanText(a.text);
  if (op === 'blocks') {const b = splitBlocks(a.text); return {blocks: b.map(x => ({idx: x.idx, text: x.text, scores: x.scores})), keep: selectBlocks(b, a.budget)};}
  if (op === 'span') return new DocIndex(a.body).locate(a.span);
  if (op === 'schema') return check(a.value, a.schema);
  if (op === 'facts') {if (a.name === 'normalize_jurisdiction') return facts.normalizeJurisdiction(a.value, KNOWN_JURISDICTIONS, STATE_NAMES); const name = a.name.replace(/_([a-z])/g, (_: string, x: string) => x.toUpperCase()); const v = (facts as any)[name](a.value); return v instanceof Set ? [...v].sort() : v;}
  if (op === 'date_interval') return dateInterval(a.value);
  if (op === 'query_date') return queryDate(a.value);
  if (op === 'chapter') return chapterOf(a.value);
  if (op === 'api_endpoint') return new ApiConfig('test-key', undefined, a.value).endpoint;
  if (op === 'api_answer') return answer(a.value);
  if (op === 'api_select') return select(a.pending, a.index, a.only);
  if (op === 'chat_complete') return new ChatClient(new ApiConfig('test-secret', undefined, a.base_url)).complete('test prompt', 'test packet');
  if (op === 'check_final') {checkFinal(a.text, 'D100-01'); return true;}
  if (op === 'cards') return {cards: loadCards(), core: renderCore('2026-10-01'), tools: toolSpecs(), prompt: renderPrompt('2026-10-01')};
  if (op === 'conditions') {const warnings: string[] = [], locate = Object.hasOwn(a, 'body') ? (q: string): string | null => new DocIndex(a.body).locate(q)?.text ?? null : null; return {value: conditions.parse(a.value, warnings, a.dates ? new Set(a.dates) : null, a.nums ? new Set(a.nums) : null, locate), warnings};}
  if (op === 'relations') {const warnings: string[] = [], idx = new DocIndex(a.body); return {value: conditions.parseRelations(a.value, warnings, q => idx.locate(q)?.text ?? null), warnings};}
  if (op === 'integer') return integer(a.value, 'units');
  if (op === 'unit_lower_bound') return unitLowerBound(a.value);
  if (op === 'parse_batch') return parseBatch(a.text, new Set(a.ids));
  if (op === 'engine') {const eng = new LookupEngine(a.rules, a.addresses, a.precedence || [], a.review || []), out = eng.all(a.as_of || '2026-10-01'); return a.export ? {all: out, exported: eng.exportedRules(a.as_of || '2026-10-01', out[0])} : out;}
  if (op === 'changes') return new ChangeTracker(new LookupEngine(a.rules, a.addresses, a.precedence || [], a.review || []), a.tests, a.rule_map).run(a.date_overrides);
  if (op === 'real_all') {const eng = LookupEngine.fromFiles(); return {addresses: Object.keys(eng.addresses).length, rules: eng.rules.length, sha256: digest(eng.all(a.as_of))};}
  if (op === 'real_changes') return new ChangeTracker(LookupEngine.fromFiles()).run();
  if (op === 'real_rules') return LookupEngine.fromFiles().exportedRules();
  if (op === 'real_review') return renderReview(LookupEngine.fromFiles());
  if (op === 'real_requests') {const report: Data = {}, eng = new LookupEngine(loadRules(undefined, undefined, report), readJson(path.join(ROOT, 'work/addresses_resolved.json'))); return requestsReport(eng, eng.all()[1], new ChangeTracker(eng).run()[1], report);}
  if (op === 'real_census') return new CensusResolver(undefined, true).resolve(loadAddresses());
  if (op === 'census') return new CensusResolver(a.cache_dir, a.offline || false, a.refresh || false, undefined, a.base_url, a.mode || 'single').resolve(a.addresses, a.aliases || {});
  if (op === 'real_packets') {const values: Data = {}; for (const [id, doc] of Object.entries(loadCorpus(defaultPaths()))) {const [packets, stats] = buildDocPackets(doc); values[id] = {stats, packets: packets.map(p => renderPacket(p, doc, '2026-10-01'))};} return {documents: Object.keys(values).length, sha256: digest(values)};}
  if (op === 'real_ingest') return ingestionView(defaultPaths());
  if (op === 'web') {const value = ROUTES['/api/' + a.route](a.query || {}); delete value.computed_ms; return value;}
  if (['pipeline', 'api_run', 'agent_run', 'tool_check'].includes(op)) {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'navigator-parity-')), p = new Paths(path.join(tmp, 'pack'), path.join(tmp, 'work'), path.join(tmp, 'outputs'), path.join(tmp, 'extra'));
    try {
      writeText(p.manifest, a.fixture.manifest); for (const [id, text] of Object.entries<string>(a.fixture.docs)) writeText(path.join(p.corpus_dir, 'text', id + '.txt'), text);
      writeText(p.schema_file, fs.readFileSync(path.join(ROOT, 'tests/fixtures/rule_record.schema.json'))); const index = prepare(p, '2026-10-01');
      if (op === 'tool_check') return checkRecord(new Validator(loadCorpus(p), index, loadSchema(p), '2026-10-01'), a.text);
      let n = 0; for (const [name, text] of Object.entries<string>(a.answers || {})) {const file = path.join(p.inbox_dir, name); writeText(file, text); fs.utimesSync(file, ++n, n);}
      if (Object.hasOwn(a, 'overrides')) writeText(path.join(p.work_dir, 'overrides.json'), JSON.stringify(a.overrides));
      if (op === 'pipeline') return ingestionView(p);
      const replies: Data[] = clone(a.replies || []), calls: Data[] = [], messages: string[] = [], post = (msgs: Data[], tools: Data[] | null = null): Data => {calls.push(clone({messages: msgs, tools})); const next = replies.shift(); if (!next) throw new Error('Test reply queue exhausted'); if (next.error) throw new ApiError(next.error); return next;}, opts = {only: a.only || ['D100-01'], once: a.once || false, dry_run: a.dry_run || false, emit: (m: string): void => {messages.push(m);}}, config = new ApiConfig('test-key'), run: Data = {};
      try {run.code = op === 'api_run' ? await runApi(p, config, {...opts, client: {complete: (prompt, packet) => post([{role: 'system', content: prompt}, {role: 'user', content: packet}])}}) : await runAgentApi(p, config, {...opts, post, workers: a.workers || 1});} catch (e) {if (!(e instanceof ApiError)) throw e; run.error = e.message.replaceAll(tmp, '<TEMP>').replace(/(?:API|AGENT)_D\d+-\d+_[\w-]+\.json/g, '<ATTEMPT>.json');}
      const res = runIngest(p, undefined, false); run.calls = calls; run.answer_count = walk(p.inbox_dir).filter(f => f.endsWith('.jsonl')).length; run.archive_count = walk(path.join(p.work_dir, 'api')).filter(f => f.endsWith('.json')).length; run.state = Object.fromEntries(Object.entries(res.states).map(([k, v]) => [k, Object.fromEntries(Object.entries(v).filter(([kk]) => kk !== 'file'))])); run.rules = res.rules.map(r => Object.fromEntries(Object.entries(r).filter(([k]) => !k.startsWith('_')))); return run;
    } finally {fs.rmSync(tmp, {recursive: true, force: true});}
  }
  throw new Error('Unknown migration operation: ' + op);
}
for await (const line of readline.createInterface({input: process.stdin, crlfDelay: Infinity})) {
  try {process.stdout.write(JSON.stringify({value: await execute(JSON.parse(line))}) + '\n');} catch (error) {process.stdout.write(JSON.stringify({error: (error as Error).message}) + '\n');}
}
