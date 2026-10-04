import assert from 'node:assert/strict';
import {test} from 'node:test';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {ROOT, Paths} from '../../dist/nav/config.js';
import {prepare, makeBatches} from '../../dist/nav/packets.js';
import {runIngest, pendingPackets} from '../../dist/nav/ingest.js';
import {ApiConfig, runApi} from '../../dist/nav/api.js';
import {runAgentApi} from '../../dist/nav/agent.js';
import {CensusResolver} from '../../dist/lookup/addresses.js';
import {LookupEngine} from '../../dist/lookup/engine.js';
import {ChangeTracker} from '../../dist/changes/engine.js';
import {hashFile, readJson, writeText, walk} from '../../dist/util.js';

const SPAN = 'A landlord shall not demand or receive a security deposit exceeding one month’s rent.';
function fixture() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'navigator-native-')), p = new Paths(path.join(tmp, 'pack'), path.join(tmp, 'work'), path.join(tmp, 'outputs'), path.join(tmp, 'extra'));
  writeText(p.schema_file, fs.readFileSync(path.join(ROOT, 'tests/fixtures/rule_record.schema.json')));
  writeText(p.manifest, 'doc_id,jurisdictions,url,source_type,capture,retrieved_at,sha256,text_file,status\nD100,"Cambridge, MA",https://example.org/law,official,yes,2026-10-03 12:00 UTC,,text/D100.txt,ok\nD101,MA,https://example.org/bill,official,yes,2026-10-03 12:00 UTC,,text/D101.txt,ok\n');
  writeText(path.join(p.corpus_dir, 'text/D100.txt'), `SOURCE: https://example.org/law\nRETRIEVED: 2026-10-03 12:00 UTC\n\nChapter 8.99 Security deposits\n${SPAN}\nThis Chapter shall take effect on January 1, 2027.\n`);
  writeText(path.join(p.corpus_dir, 'text/D101.txt'), 'SOURCE: https://example.org/bill\nRETRIEVED: 2026-10-03 12:00 UTC\n\nH.9999 An Act relative to rent stabilization.\nA municipality may adopt rent control under this act.\nStatus: pending in committee.\n');
  const good = {packet_id: 'D100-01', doc_id: 'D100', jurisdiction: 'Cambridge, MA', category: 'security_deposits', lifecycle: 'enacted', title: 'Deposit cap', requirement: "Deposits are capped at one month's rent.", key_value: "1 month's rent", coverage_conditions: 'All rentals', applicability: {}, exemptions: null, penalty: null, effective_date: '2027-01-01', citation: 'Cambridge Mun. Code §8.99.010', quoted_span: SPAN, interaction: null, confidence: .9, conflict_flag: false, conflict_note: null};
  const answer = r => JSON.stringify(r) + '\n' + JSON.stringify({packet_id: r.packet_id, n_rules: 1, note: null});
  const clean = () => fs.rmSync(tmp, {recursive: true, force: true}); return {tmp, p, good, answer, clean};
}
function cli(file, args, env = {}) {return spawnSync(process.execPath, [path.join(ROOT, 'dist', file), ...args], {cwd: ROOT, encoding: 'utf8', env: {...process.env, PATH: '/no-python-or-shell-tools', ...env}});}
function navArgs(f, command, ...args) {return [command, '--data-dir', f.p.data_dir, '--work-dir', f.p.work_dir, '--out-dir', f.p.out_dir, '--extra-dir', f.p.extra_dir, ...args];}
async function localServer(t, handler) {const server = http.createServer(handler); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve)); t.after(() => new Promise(resolve => {server.close(resolve); server.closeAllConnections();})); return 'http://127.0.0.1:' + server.address().port;}
test('native CLI prepares, bundles, imports, preserves IDs and reports without Python', t => {
  const f = fixture(); t.after(f.clean); let r = cli('nav/cli.js', navArgs(f, 'prepare')); assert.equal(r.status, 0, r.stderr); assert.equal(Object.keys(readJson(f.p.index_file).packets).length, 2);
  r = cli('nav/cli.js', navArgs(f, 'bundle')); assert.equal(r.status, 0, r.stderr); const batch = fs.readFileSync(walk(f.p.paste_dir)[0], 'utf8'); assert.match(batch, /npm run nav -- ingest/); assert.doesNotMatch(batch, /python3? run\.py/);
  writeText(path.join(f.p.inbox_dir, 'answer.txt'), f.answer(f.good)); r = cli('nav/cli.js', navArgs(f, 'ingest')); assert.equal(r.status, 0, r.stderr); const records = readJson(path.join(f.p.out_dir, 'rules.json')).rules; assert.equal(records.length, 1); assert.equal(records[0].status, 'not_yet_effective'); assert.equal(records[0].quoted_span, SPAN); const id = records[0].team_rule_id;
  r = cli('nav/cli.js', navArgs(f, 'ingest', '--rules-format', 'list')); assert.equal(r.status, 0, r.stderr); assert.equal(readJson(path.join(f.p.out_dir, 'rules.json'))[0].team_rule_id, id); const audit = readJson(path.join(f.p.work_dir, 'audit.json')); assert.equal(audit.outputs['rules.json'], hashFile(path.join(f.p.out_dir, 'rules.json')));
  r = cli('nav/cli.js', navArgs(f, 'status', '--all')); assert.equal(r.status, 0, r.stderr); assert.match(r.stdout, /D100-01\s+done/); assert.match(r.stdout, /D101-01\s+pending/); assert.match(fs.readFileSync(path.join(f.p.work_dir, 'report.md'), 'utf8'), /Rules to check by hand/);
});
test('partial prepare and add-doc keep previous answers and packets', t => {
  const f = fixture(); t.after(f.clean); prepare(f.p, '2026-10-01'); writeText(path.join(f.p.inbox_dir, 'answer.txt'), f.answer(f.good)); const packet = hashFile(path.join(f.p.packets_dir, 'D100-01.md'));
  const text = path.join(f.tmp, 'new-law.txt'); writeText(text, 'Chapter 1 Security deposits\nNo landlord shall receive a security deposit greater than two months rent.'); let r = cli('nav/cli.js', navArgs(f, 'add-doc', '--file', text, '--jurisdiction', 'Boston, MA', '--url', 'https://example.org/new-law', '--retrieved', '2026-10-04 12:00 UTC')); assert.equal(r.status, 0, r.stderr);
  r = cli('nav/cli.js', navArgs(f, 'prepare', '--only', 'X001')); assert.equal(r.status, 0, r.stderr); assert.equal(hashFile(path.join(f.p.packets_dir, 'D100-01.md')), packet); assert.ok(fs.existsSync(path.join(f.p.packets_dir, 'X001-01.md'))); assert.equal(runIngest(f.p, undefined, false).states['D100-01'].state, 'done');
});
test('CLI dry-run does not create IDs, answers or archives', t => {
  const f = fixture(); t.after(f.clean); prepare(f.p, '2026-10-01'); const env = path.join(f.tmp, 'empty.env'); writeText(env, ''); const before = Object.fromEntries(walk(f.tmp).map(p => [p, hashFile(p)])); const r = cli('nav/cli.js', navArgs(f, 'api', '--agent', '--dry-run', '--env-file', env), {NAV_API_KEY: '', DEEPSEEK_API_KEY: ''}); assert.equal(r.status, 0, r.stderr); assert.match(r.stdout, /未调用 API/); assert.deepEqual(Object.fromEntries(walk(f.tmp).map(p => [p, hashFile(p)])), before);
});
test('CLI rejects wrong arguments before changing input files', t => {
  const f = fixture(); t.after(f.clean); prepare(f.p, '2026-10-01'); const before = hashFile(f.p.index_file); const r = cli('nav/cli.js', navArgs(f, 'ingest', '--rules-format', 'bad')); assert.equal(r.status, 1); assert.match(r.stderr, /rules-format/); assert.equal(hashFile(f.p.index_file), before); assert.ok(!fs.existsSync(path.join(f.p.out_dir, 'rules.json')));
});
test('single-shot API repairs from real local HTTP and archives complete responses', async t => {
  const f = fixture(); t.after(f.clean); prepare(f.p, '2026-10-01'); const calls = [], replies = [{...f.good, quoted_span: 'An invented quotation that is not present in this source.'}, f.good];
  const base = await localServer(t, (req, res) => {let body = ''; req.on('data', chunk => {body += chunk;}); req.on('end', () => {calls.push({payload: JSON.parse(body), key: req.headers.authorization}); const text = f.answer(replies.shift()); res.end(JSON.stringify({choices: [{message: {content: text}, finish_reason: 'stop'}], usage: {completion_tokens: 12}}));});});
  assert.equal(await runApi(f.p, new ApiConfig('invented-test-key', undefined, base), {only: ['D100'], emit: () => {}}), 0); assert.equal(calls.length, 2); assert.match(calls[1].payload.messages[1].content, /CORRECTIONS NEEDED/); assert.equal(calls[0].key, 'Bearer invented-test-key'); assert.deepEqual(Object.keys(calls[0].payload).sort(), ['messages', 'model', 'stream']);
  const archives = walk(path.join(f.p.work_dir, 'api')).filter(p => p.endsWith('.json')); assert.equal(archives.length, 2); for (const p of archives) {const raw = fs.readFileSync(p, 'utf8'); assert.doesNotMatch(raw, /invented-test-key/); assert.ok(readJson(p).response.usage); assert.equal(readJson(p).prompt_sha256.length, 64);} assert.equal(runIngest(f.p, undefined, false).states['D100-01'].state, 'done');
});
test('every selected packet is checked before the first model call', async t => {
  const f = fixture(); t.after(f.clean); prepare(f.p, '2026-10-01'); fs.appendFileSync(path.join(f.p.packets_dir, 'D101-01.md'), 'tampered'); let calls = 0; await assert.rejects(runApi(f.p, new ApiConfig('test'), {client: {complete() {calls++;}}, emit: () => {}}), /D101-01 与目录记录不一致/); assert.equal(calls, 0); assert.equal(walk(f.p.inbox_dir).length, 0);
});
test('completed packets resume without any model request', async t => {
  const f = fixture(); t.after(f.clean); prepare(f.p, '2026-10-01'); writeText(path.join(f.p.inbox_dir, 'answer.txt'), f.answer(f.good)); let calls = 0; assert.equal(await runApi(f.p, new ApiConfig('test'), {only: ['D100'], client: {complete() {calls++;}}, emit: () => {}}), 0); assert.equal(calls, 0); assert.equal(walk(f.p.inbox_dir).length, 1);
});
test('agent tool calls return card text and self-checks through real local HTTP', async t => {
  const f = fixture(); t.after(f.clean); prepare(f.p, '2026-10-01'); const calls = []; let step = 0;
  const base = await localServer(t, (req, res) => {let body = ''; req.on('data', chunk => {body += chunk;}); req.on('end', () => {calls.push(JSON.parse(body)); const call = step++ === 0 ? {id: 'card', type: 'function', function: {name: 'read_card', arguments: JSON.stringify({name: 'citations'})}} : {id: 'check', type: 'function', function: {name: 'check_record', arguments: JSON.stringify({record_json: JSON.stringify(f.good)})}}; const message = step <= 2 ? {role: 'assistant', content: null, tool_calls: [call]} : {role: 'assistant', content: f.answer(f.good)}; res.end(JSON.stringify({choices: [{message, finish_reason: step <= 2 ? 'tool_calls' : 'stop'}], usage: {total_tokens: 20}}));});});
  assert.equal(await runAgentApi(f.p, new ApiConfig('test', undefined, base), {only: ['D100'], emit: () => {}}), 0); assert.equal(calls.length, 3); assert.match(calls[1].messages.at(-1).content, /Card: citations/); assert.match(calls[2].messages.at(-1).content, /^ACCEPTED\./); const log = readJson(walk(path.join(f.p.work_dir, 'api')).find(p => p.endsWith('.json'))); assert.deepEqual([log.steps, log.cards_read, log.checks], [3, ['citations'], 1]); assert.equal(log.usage.length, 3); assert.equal(log.messages.length, 5);
});
test('concurrent agent packets preserve both answers and IDs', async t => {
  const f = fixture(); t.after(f.clean); prepare(f.p, '2026-10-01'); const second = {...f.good, packet_id: 'D101-01', doc_id: 'D101', jurisdiction: 'MA', category: 'rent_increase_limits', lifecycle: 'pending_bill', title: 'Rent control bill', requirement: 'A municipality may adopt rent control.', key_value: null, effective_date: null, citation: 'H.9999', quoted_span: 'A municipality may adopt rent control under this act.'};
  const post = async msgs => {const r = msgs[1].content.includes('<<<PACKET D100-01>>>') ? f.good : second; await new Promise(resolve => setImmediate(resolve)); return {choices: [{message: {role: 'assistant', content: f.answer(r)}, finish_reason: 'stop'}]};}; assert.equal(await runAgentApi(f.p, null, {post, workers: 2, emit: () => {}}), 0); const res = runIngest(f.p, undefined, false); assert.equal(res.counts.packets_done, 2); assert.equal(res.rules.length, 2); assert.equal(new Set(res.rules.map(r => r.team_rule_id)).size, 2); assert.deepEqual(pendingPackets(res), {});
});
test('Census batch processes coordinates, ties, mismatches and an offline replay', async t => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'navigator-census-')); t.after(() => fs.rmSync(tmp, {recursive: true, force: true})); const calls = [], row = id => ({address_id: id, street_address: id + ' Example St', postal_city: 'Boston', state: 'MA', zip: '02110'}), addresses = {A: row('A'), B: row('B'), C: row('C')};
  const base = await localServer(t, (req, res) => {let body = ''; req.on('data', c => {body += c;}); req.on('end', () => {calls.push({url: req.url, body, type: req.headers['content-type']}); if (req.method === 'POST') res.end('A,addr,Match,Exact,"matched","-71.1,42.3"\nB,addr,Tie\nC,addr,Match,Exact,"matched","-70.1,42.4"\n'); else {const wrong = req.url.includes('x=-70.1'); res.end(JSON.stringify({result: {geographies: {'Incorporated Places': wrong ? [{STATE: '06', BASENAME: 'Los Angeles', NAME: 'Los Angeles city', GEOID: '066'}] : [{STATE: '25', BASENAME: 'Boston', NAME: 'Boston city', GEOID: '2507000'}]}}}));}});});
  const resolver = new CensusResolver(tmp, false, false, 2, base, 'batch'), result = await resolver.resolve(addresses, {MA: {boston: 'Boston, MA'}}); assert.equal(calls.length, 3); assert.match(calls[0].type, /multipart\/form-data; boundary=navigator-/); assert.match(calls[0].body, /A,A Example St,Boston,MA,02110/); assert.match(calls[1].url, /layers=Incorporated\+Places/); assert.equal(result.A.resolved_by, 'geocoder'); assert.equal(result.B.resolved_by, 'postal_city_fallback'); assert.equal(result.C.resolved_by, 'postal_city_fallback'); assert.equal(result.C.legal_city, 'Boston, MA'); assert.deepEqual(await new CensusResolver(tmp, true, false, 2, base, 'batch').resolve(addresses, {MA: {boston: 'Boston, MA'}}), result); assert.equal(calls.length, 3);
});
test('all submission files are reproducible and match direct computation', t => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'navigator-build-')); t.after(() => fs.rmSync(tmp, {recursive: true, force: true})); const outDir = path.join(tmp, 'outputs'), workDir = path.join(tmp, 'work'), args = ['build', '--offline', '--output-dir', outDir, '--work-dir', workDir]; let r = cli('lookup/cli.js', args); assert.equal(r.status, 0, r.stderr); const eng = LookupEngine.fromFiles(), [lookups, audit] = eng.all(), [changes, changeAudit] = new ChangeTracker(eng).run(); assert.deepEqual(readJson(path.join(outDir, 'lookups.json')), lookups); assert.deepEqual(readJson(path.join(outDir, 'rules.json')), {rules: eng.exportedRules(undefined, lookups)}); assert.deepEqual(readJson(path.join(outDir, 'changes.json')), changes); assert.deepEqual(readJson(path.join(workDir, 'lookup_audit.json')), audit); assert.deepEqual(readJson(path.join(workDir, 'changes_audit.json')), changeAudit);
  const manifest = readJson(path.join(workDir, 'stage23_audit.json')); for (const [name, hash] of Object.entries(manifest.outputs)) assert.equal(hashFile(path.join(outDir, name)), hash); const before = Object.fromEntries(walk(tmp).map(p => [p, hashFile(p)])); r = cli('lookup/cli.js', args); assert.equal(r.status, 0, r.stderr); assert.deepEqual(Object.fromEntries(walk(tmp).map(p => [p, hashFile(p)])), before);
});
test('stale resolved address facts stop a build before replacing outputs', t => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'navigator-stale-')); t.after(() => fs.rmSync(tmp, {recursive: true, force: true})); const resolved = readJson(path.join(ROOT, 'work/addresses_resolved.json')); resolved.A0001.units = 999; const file = path.join(tmp, 'addresses.json'); writeText(file, JSON.stringify(resolved)); const outDir = path.join(tmp, 'outputs'), marker = path.join(outDir, 'rules.json'); writeText(marker, 'preserve-existing-output'); const r = cli('lookup/cli.js', ['build', '--resolved', file, '--output-dir', outDir, '--work-dir', path.join(tmp, 'work')]); assert.equal(r.status, 1); assert.match(r.stderr, /请重新 resolve/); assert.equal(fs.readFileSync(marker, 'utf8'), 'preserve-existing-output'); assert.equal(walk(outDir).length, 1);
});
