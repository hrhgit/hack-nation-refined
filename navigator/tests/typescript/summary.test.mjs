import assert from 'node:assert/strict';
import {test} from 'node:test';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import http from 'node:http';
import {ApiConfig, ChatClient} from '../../dist/nav/api.js';
import {SummaryService, citationCatalog, summaryInput} from '../../dist/web/summary.js';
import {apiLookup, createServer} from '../../dist/web/server.js';
import {canonicalJson, summaryFingerprint} from '../../web/static/summary-shared.js';
import {receiveSummary} from '../../web/static/summary-client.js';

function evidence() {
  return {as_of: '2026-10-01', computed_ms: 1, address: {address_id: 'A0001', state: 'CA', year_built: null, units: 3}, entered_facts: {},
    results: [{team_rule_id: 'r-1', result: 'unknown', conflict_flag: true, explanation: 'Year built is missing', missing_facts: [{field: 'year_built'}],
      rule: {team_rule_id: 'r-1', citation: 'Civil Code § 123', status: 'in_force', key_value: "1 month's rent", exemptions: 'Owner-occupied homes', sources: [
        {doc_id: 'D001', origin: 'starter', url: 'https://example.org/law', quoted_span: 'A deposit shall not exceed one month of rent.'},
        {doc_id: 'X001', origin: 'extra', url: 'https://example.org/extra', quoted_span: 'An owner-occupied dwelling is exempt.'}]} }],
    left_out: [], conflict_pairs: [['r-1', 'r-2']], extraction: {done: 1, total: 2}, disclaimer: 'Not legal advice.'};
}
const paragraph = (section = 'uncertainty', refs = [{ref_id: 'C1', result: 'unknown'}]) => ({type: 'paragraph', section, sentences: [{text: '押金上限为一个月租金，但缺少建造年份，适用情况仍不确定。', refs}]});
const modelText = (...paragraphs) => [...paragraphs, {type: 'complete'}].map(o => JSON.stringify(o)).join('\n') + '\n';
function setup(t, client, extra = {}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'navigator-summary-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const options = {cacheDir: path.join(dir, 'cache'), archiveDir: path.join(dir, 'runs'), config: () => new ApiConfig('private-test-key'), client: () => client, ...extra};
  return {dir, options, service: new SummaryService(options)};
}
function simulated(text, {finish = 'stop', fail = false} = {}) {
  return {async streamComplete(prompt, input, onDelta) {
    // Split JSON lines across chunks, including Chinese characters at JS boundaries.
    for (let i = 0; i < text.length; i += 7) onDelta(text.slice(i, i + 7));
    if (fail) throw new Error('connection lost');
    return {text, finish_reason: finish, usage: {completion_tokens: 10}};
  }};
}
async function collect(service, data = evidence(), language = 'zh') {
  const events = []; let detach;
  await new Promise((resolve, reject) => {
    summaryFingerprint(data).then(fp => service.subscribe(data, language, fp, event => {
      events.push(event); if (event.type === 'complete' || event.type === 'error') resolve();
    })).then(d => {detach = d;}, reject);
  });
  detach?.(); return events;
}
async function localServer(t, handler) {
  const server = typeof handler === 'function' ? http.createServer(handler) : handler;
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => {server.close(resolve); server.closeAllConnections();}));
  return 'http://127.0.0.1:' + server.address().port;
}
function sse(text, reason = 'stop') {
  const events = [];
  for (let i = 0; i < text.length; i += 11) events.push('data: ' + JSON.stringify({choices: [{index: 0, delta: {content: text.slice(i, i + 11)}, finish_reason: null}]}) + '\r\n\r\n');
  events.push('data: ' + JSON.stringify({choices: [{index: 0, delta: {}, finish_reason: reason}]}) + '\n\n');
  events.push('data: ' + JSON.stringify({choices: [], usage: {completion_tokens: 12}}) + '\n\n');
  events.push('data: [DONE]\n\n'); return Buffer.from(events.join(''));
}

test('fingerprints match the delivered JSON, ignore only timing, and include all query evidence', async () => {
  const data = evidence(), original = await summaryFingerprint(data);
  assert.equal(await summaryFingerprint({...data, computed_ms: 999}), original);
  assert.equal(await summaryFingerprint(JSON.parse(JSON.stringify(data))), original);
  assert.equal(canonicalJson({b: 1, a: '中'}), canonicalJson({a: '中', b: 1}));
  const changes = [d => d.as_of = '2027-01-01', d => d.address.address_id = 'A0002', d => d.address.units = 4,
    d => d.address.year_built = 1980, d => d.entered_facts.units = 3, d => d.results[0].result = 'applies',
    d => d.results[0].rule.sources[0].quoted_span += ' Exceptions apply.', d => d.results[0].rule.exemptions = 'New exception',
    d => d.results[0].missing_facts = [], d => d.conflict_pairs = [], d => d.extraction.done = 2];
  for (const change of changes) {const modified = structuredClone(data); change(modified); assert.notEqual(await summaryFingerprint(modified), original);}
});

test('paragraphs are streamed before completion; citations are rebuilt from actual sources', async t => {
  let finish, first;
  const firstReady = new Promise(r => {first = r;});
  const release = new Promise(r => {finish = r;});
  const text = modelText(paragraph('uncertainty', [{ref_id: 'C2', result: 'unknown'}]));
  const {service, dir} = setup(t, {async streamComplete(prompt, input, onDelta, options) {
    assert.match(prompt, /Simplified Chinese/); assert.match(prompt, /missing fact stays unknown/);
    assert.deepEqual(options, {thinking: {type: 'disabled'}});
    const payload = JSON.parse(input); assert.equal(payload.unresolved_or_inactive_rules[0].result, 'unknown'); assert.ok(payload.unresolved_or_inactive_rules[0].conflict_flag); assert.equal(payload.computed_ms, undefined);
    const cut = text.indexOf('\n') + 1; onDelta(text.slice(0, cut)); first(); await release; onDelta(text.slice(cut));
    return {text, finish_reason: 'stop', usage: null};
  }});
  const events = [], data = evidence(), fp = await summaryFingerprint(data);
  let complete; const completed = new Promise(r => {complete = r;});
  const detach = await service.subscribe(data, 'zh', fp, e => {events.push(e); if (e.type === 'complete') complete();});
  await firstReady;
  assert.deepEqual(events.map(e => e.type), ['start', 'paragraph']);
  const ref = events[1].paragraph.sentences[0].refs[0]; assert.equal(ref.origin, 'extra'); assert.equal(ref.result, 'unknown'); assert.equal(ref.conflict_flag, true);
  assert.equal(ref.url, 'https://example.org/extra'); assert.match(ref.source_href, /doc_id=X001/);
  finish(); await completed; detach();
  assert.equal(fs.readdirSync(path.join(dir, 'cache')).length, 1);
  assert.equal(events.at(-1).cached, false);
  const archive = fs.readFileSync(path.join(dir, 'runs', fs.readdirSync(path.join(dir, 'runs'))[0]), 'utf8');
  assert.doesNotMatch(archive, /private-test-key/);
});

test('completed answers survive restart, share calls, and invalidate for language/model/version', async t => {
  let calls = 0;
  const client = {async streamComplete(...args) {calls++; return simulated(modelText(paragraph())).streamComplete(...args);}};
  const {service, options} = setup(t, client);
  const results = await Promise.all([collect(service), collect(service)]);
  assert.equal(calls, 1); assert.ok(results.every(events => events.at(-1).type === 'complete'));
  assert.equal((await collect(new SummaryService(options)))[0].cached, true); assert.equal(calls, 1);
  await collect(service, evidence(), 'es'); await collect(service, evidence(), 'en');
  await collect(new SummaryService({...options, version: 'future-version'}));
  await collect(new SummaryService({...options, config: () => new ApiConfig('private-test-key', 'different-model')}));
  assert.equal(calls, 5);
  const same = evidence(); same.computed_ms = 999; assert.equal((await collect(service, same))[0].cached, true); assert.equal(calls, 5);
  for (const change of [d => d.as_of = '2027-01-01', d => d.address.address_id = 'A0002', d => d.address.units = 4,
    d => d.results[0].rule.sources[0].quoted_span += ' A full new sentence.', d => d.extraction.done = 2]) {
    const changed = evidence(); change(changed); const prior = calls;
    assert.equal((await collect(service, changed))[0].cached, false); assert.equal(calls, prior + 1);
    assert.equal((await collect(service, changed))[0].cached, true); assert.equal(calls, prior + 1);
  }
});

test('disconnecting all subscribers still completes the shared job and cache', async t => {
  let release, entered;
  const gate = new Promise(r => {release = r;}); const running = new Promise(r => {entered = r;});
  let finished; const ended = new Promise(r => {finished = r;});
  const {service} = setup(t, {async streamComplete(...args) {entered(); await gate; const result = await simulated(modelText(paragraph())).streamComplete(...args); finished(); return result;}});
  const data = evidence(), received = [];
  const detach = await service.subscribe(data, 'zh', await summaryFingerprint(data), e => received.push(e)); await running; detach(); release(); await ended;
  await new Promise(r => setImmediate(r));
  assert.deepEqual(received.map(e => e.type), ['start']);
  assert.equal((await collect(service))[0].cached, true);
});

test('unknown references, malformed paragraphs, incomplete receipts and interrupted output never populate cache', async t => {
  const cases = [modelText(paragraph('uncertainty', [{ref_id: 'foreign-ref', result: 'unknown'}])),
    modelText(paragraph('uncertainty', [{ref_id: 'C99', result: 'unknown'}])),
    modelText(paragraph('uncertainty', [{ref_id: 'C1', result: 'applies'}])),
    modelText(paragraph('overview', [])), '{"type":"paragraph",',
    JSON.stringify(paragraph()) + '\n',
    '{"type":"complete"}\n',
    modelText(paragraph()) + JSON.stringify(paragraph()) + '\n',
    modelText(paragraph('uncertainty'), paragraph('overview'))];
  for (const text of cases) {
    const {service, dir} = setup(t, simulated(text)); const events = await collect(service);
    assert.equal(events.at(-1).type, 'error'); assert.ok(!fs.existsSync(path.join(dir, 'cache')));
  }
  for (const options of [{finish: 'length'}, {fail: true}]) {
    const {service, dir} = setup(t, simulated(modelText(paragraph()), options)); const events = await collect(service);
    assert.equal(events[1].type, 'paragraph'); assert.equal(events.at(-1).type, 'error'); assert.ok(!fs.existsSync(path.join(dir, 'cache')));
  }
});

test('failed generation can be retried manually with a fresh call, without automatic retry', async t => {
  let calls = 0;
  const {service} = setup(t, {async streamComplete(...args) {calls++; return simulated(modelText(paragraph()), {fail: calls === 1}).streamComplete(...args);}});
  assert.equal((await collect(service)).at(-1).type, 'error'); assert.equal(calls, 1);
  assert.equal((await collect(service)).at(-1).type, 'complete'); assert.equal(calls, 2);
});

test('each sentence keeps its own sources and an uncited sentence rejects the whole paragraph', async t => {
  const p = paragraph();
  p.sentences.push({text: '业主自住的房屋可能有例外。', refs: [{ref_id: 'C2', result: 'unknown'}]});
  const good = setup(t, simulated(modelText(p)));
  const result = (await collect(good.service))[1].paragraph;
  assert.deepEqual(result.sentences.map(s => s.refs.map(r => r.doc_id)), [['D001'], ['X001']]);
  p.sentences[1].refs = [];
  const bad = setup(t, simulated(modelText(p))); const events = await collect(bad.service);
  assert.deepEqual(events.map(e => e.type), ['start', 'error']);
  const multiple = paragraph(); multiple.sentences[0].text = '第一句。第二句。';
  const split = setup(t, simulated(modelText(multiple)));
  const splitResult = (await collect(split.service))[1].paragraph;
  assert.deepEqual(splitResult.sentences.map(s => s.text), ['第一句。', '第二句。']);
  assert.ok(splitResult.sentences.every(s => s.refs[0].doc_id === 'D001'));
  const legal = paragraph(); legal.sentences[0].text = 'P.L. 2026, c. 43 takes effect in 2027. It is not in force yet.';
  const legalSplit = setup(t, simulated(modelText(legal)));
  const legalResult = (await collect(legalSplit.service, evidence(), 'en'))[1].paragraph;
  assert.deepEqual(legalResult.sentences.map(s => s.text), ['P.L. 2026, c. 43 takes effect in 2027.', 'It is not in force yet.']);
  assert.equal((await collect(new SummaryService(legalSplit.options), evidence(), 'en'))[1].paragraph.sentences[0].text, legalResult.sentences[0].text);
});

test('empty lookup uses no model or configuration; stale evidence is rejected before calling', async t => {
  let calls = 0;
  const {service} = setup(t, null, {config() {calls++; throw new Error('no config');}});
  const empty = evidence(); empty.results = [];
  const events = await collect(service, empty); assert.equal(events.at(-1).empty, true); assert.equal(events[0].partial, true); assert.equal(calls, 0);
  await assert.rejects(service.subscribe(evidence(), 'zh', await summaryFingerprint(empty), () => {}), e => e.code === 'stale_evidence' && e.status === 409);
  assert.equal(calls, 0);
});

test('missing key is explicit; existing cache can be read without a key', async t => {
  const {service, options} = setup(t, simulated(modelText(paragraph())));
  const emptyKey = new SummaryService({...options, config: () => new ApiConfig('')});
  const data = evidence();
  await assert.rejects(emptyKey.subscribe(data, 'zh', await summaryFingerprint(data), () => {}), e => e.code === 'missing_key');
  await collect(service); assert.equal((await collect(emptyKey))[0].cached, true);
});

test('ChatClient parses fragmented SSE and UTF-8 and waits for finish=stop plus DONE', async t => {
  const text = modelText(paragraph()), bytes = sse(text); let request;
  const url = await localServer(t, async (req, res) => {
    let raw = ''; for await (const part of req) raw += part; request = JSON.parse(raw);
    res.writeHead(200, {'Content-Type': 'text/event-stream'});
    for (let i = 0; i < bytes.length; i += 13) {res.write(bytes.subarray(i, i + 13)); await new Promise(r => setImmediate(r));}
    res.end();
  });
  let received = '';
  const result = await new ChatClient(new ApiConfig('private-test-key', 'model', url)).streamComplete('instructions', 'evidence', d => {received += d;}, {thinking: {type: 'disabled'}});
  assert.equal(received, text); assert.equal(result.text, text); assert.equal(result.usage.completion_tokens, 12);
  assert.equal(request.stream, true); assert.ok(!('max_tokens' in request));
  assert.deepEqual(request.thinking, {type: 'disabled'});
  for (const variant of [sse(text, 'length'), bytes.subarray(0, bytes.length - 'data: [DONE]\n\n'.length), Buffer.from('data: invalid JSON\n\n')]) {
    const broken = await localServer(t, (req, res) => {res.writeHead(200, {'Content-Type': 'text/event-stream'}); res.end(variant);});
    await assert.rejects(new ChatClient(new ApiConfig('private-test-key', 'model', broken)).streamComplete('p', 'i', () => {}));
  }
  const validationError = new Error('invalid citation');
  await assert.rejects(new ChatClient(new ApiConfig('private-test-key', 'model', url)).streamComplete('p', 'i', () => {throw validationError;}), e => e === validationError);
  const severed = await localServer(t, (req, res) => {
    res.writeHead(200, {'Content-Type': 'text/event-stream'}); res.write(bytes.subarray(0, 30));
    setImmediate(() => res.destroy());
  });
  await assert.rejects(new ChatClient(new ApiConfig('private-test-key', 'model', severed)).streamComplete('p', 'i', () => {}));
});

test('HTTP summary leaves lookup intact, streams before model ends, returns cache and handles mismatch', async t => {
  const data = apiLookup({address_id: ['A0001']}); const row = data.results.find(r => r.result === 'applies' && r.rule.sources.some(s => s.doc_id && s.quoted_span));
  assert.ok(row);
  const entry = citationCatalog(data).find(r => r.rule_id === row.team_rule_id);
  const p = paragraph('overview', [{ref_id: entry.ref_id, result: entry.result}]);
  const {service} = setup(t, simulated(modelText(p)));
  const url = await localServer(t, createServer({summaryService: service}));
  const payload = {query: {address_id: 'A0001'}, language: 'en', fingerprint: await summaryFingerprint(data)};
  const post = body => fetch(url + '/api/summary', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
  const response = await post(payload); assert.equal(response.status, 200);
  const events = (await response.text()).trim().split('\n').map(line => JSON.parse(line));
  assert.deepEqual(events.map(e => e.type), ['start', 'paragraph', 'complete']);
  assert.equal((await (await post(payload)).text()).split('\n').map(line => line && JSON.parse(line))[0].cached, true);
  const stale = await post({...payload, query: {address_id: 'A0002'}}); assert.equal(stale.status, 409); assert.equal((await stale.json()).code, 'stale_evidence');
  const invalid = await post({...payload, language: 'fr'}); assert.equal(invalid.status, 400);
  const external = await fetch(url + '/api/summary', {method: 'POST', headers: {'Content-Type': 'application/json', Origin: 'https://other.example'}, body: JSON.stringify(payload)});
  assert.equal(external.status, 403);
  const original = await (await fetch(url + '/api/lookup?address_id=A0001')).json();
  assert.equal(await summaryFingerprint(original), payload.fingerprint);
  // Model failure is on the separate summary connection, never the lookup.
  const bad = setup(t, simulated('not JSON\n'));
  const brokenUrl = await localServer(t, createServer({summaryService: bad.service}));
  const broken = await fetch(brokenUrl + '/api/summary', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
  assert.equal(JSON.parse((await broken.text()).trim().split('\n').at(-1)).type, 'error');
  assert.equal((await fetch(brokenUrl + '/api/lookup?address_id=A0001')).status, 200);
});

test('browser receiver handles split records, aborts old connections and refuses an incomplete answer', async t => {
  const fp = await summaryFingerprint(evidence());
  const events = [{type: 'start', fingerprint: fp, cached: false}, {type: 'paragraph', paragraph: paragraph()}, {type: 'complete', empty: false}];
  const bytes = Buffer.from(events.map(e => JSON.stringify(e)).join('\n') + '\n');
  const url = await localServer(t, async (req, res) => {
    res.writeHead(200, {'Content-Type': 'application/x-ndjson'});
    for (let i = 0; i < bytes.length; i += 5) {res.write(bytes.subarray(i, i + 5)); await new Promise(r => setImmediate(r));}
    res.end();
  });
  const controller = new AbortController(), got = [];
  await receiveSummary({query: {}, language: 'zh', fingerprint: fp, signal: controller.signal, onEvent: e => got.push(e)}, (p, options) => fetch(url + p, options));
  assert.equal(got[1].paragraph.sentences[0].text, paragraph().sentences[0].text); assert.equal(got.at(-1).type, 'complete');
  const aborted = new AbortController(), old = [];
  await assert.rejects(receiveSummary({query: {}, language: 'zh', fingerprint: fp, signal: aborted.signal, onEvent(e) {old.push(e); aborted.abort();}}, (p, options) => fetch(url + p, options)), {name: 'AbortError'});
  assert.deepEqual(old.map(e => e.type), ['start']);
  const incomplete = new Response(JSON.stringify(events[0]) + '\n', {headers: {'Content-Type': 'application/x-ndjson'}});
  await assert.rejects(receiveSummary({query: {}, language: 'zh', fingerprint: fp, signal: new AbortController().signal, onEvent() {}}, async () => incomplete), e => e.code === 'incomplete');
  const wrong = new Response(JSON.stringify({...events[0], fingerprint: 'wrong'}) + '\n', {headers: {'Content-Type': 'application/x-ndjson'}});
  await assert.rejects(receiveSummary({query: {}, language: 'zh', fingerprint: fp, signal: new AbortController().signal, onEvent() {}}, async () => wrong), e => e.code === 'invalid_stream');
});

test('compact model input preserves full sources, numbers, exceptions, conflicts and unknowns without modifying lookup', () => {
  const data = evidence(); data.results[0].steps = [{step: 3, explanation: 'Year built is missing'}];
  const before = structuredClone(data), input = summaryInput(data);
  assert.deepEqual(data, before); assert.equal(input.unresolved_or_inactive_rules[0].steps, undefined);
  for (const field of ['sources', 'key_value', 'exemptions']) assert.deepEqual(input.unresolved_or_inactive_rules[0].rule[field], data.results[0].rule[field]);
  assert.deepEqual(input.unresolved_or_inactive_rules[0].missing_facts, data.results[0].missing_facts);
  assert.equal(input.unresolved_or_inactive_rules[0].result, 'unknown'); assert.equal(input.unresolved_or_inactive_rules[0].conflict_flag, true);
  assert.deepEqual(input.extraction, data.extraction); assert.deepEqual(input.excluded_measures, data.left_out);
});
