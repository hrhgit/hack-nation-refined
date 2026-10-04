import assert from 'node:assert/strict';
import {test} from 'node:test';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {setImmediate as nextTurn} from 'node:timers/promises';
import {LawImports} from '../../dist/web/law-imports.js';
import {createServer} from '../../dist/web/server.js';
import {ApiConfig} from '../../dist/nav/api.js';
import {findDataDir} from '../../dist/nav/config.js';
import {readJson} from '../../dist/util.js';
import {ChangeTracker} from '../../dist/changes/engine.js';

const SPAN = 'A landlord shall not demand a security deposit exceeding 2 months of rent.';
const BODY = `Cambridge Municipal Code Chapter 8.99.010 — synthetic test fixture, not actual law.\nSecurity deposits\n${SPAN}\nThis rule applies to all residential rentals.\nEnacted; effective January 1, 2027.`;
const INPUT = {text: BODY};
const oldRule = () => ({team_rule_id: 'r-1000', jurisdiction: 'Cambridge, MA', level: 'city', category: 'security_deposits', lifecycle: 'enacted', effective_date: '2020-01-01', title: 'Old test deposit law', citation: 'Cambridge Municipal Code § 8.99.010', requirement: 'Maximum deposit is 1 month of rent.', key_value: '1 month of rent', applicability: {}, coverage_conditions: 'All residential rentals', quoted_span: 'Maximum deposit is 1 month of rent.', source_doc_id: 'D100', source_url: 'https://example.org/old', retrieved: '2026-10-01'});
function fixture(t, extras = {}) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'navigator-import-tests-')); t.after(() => fs.rmSync(tmp, {recursive: true, force: true}));
  let base = [], addresses = {C: {state: 'MA', legal_city: 'Cambridge, MA', street_address: 'Synthetic Cambridge fixture', units: 5}, B: {state: 'MA', legal_city: 'Boston, MA', street_address: 'Synthetic Boston fixture'}, N: {state: 'NJ', legal_city: 'Newark, NJ'}};
  let calls = 0, checks = 0, receipt = '';
  const post = (messages) => {
    calls++;
    const packet = messages[1].content, pid = /packet_id: (\S+)/.exec(packet)[1], did = /doc_id: (\S+)/.exec(packet)[1];
    const rules = (extras.records || [typeof extras.record === 'function' ? extras.record(packet) : extras.record || {}]).map(record => ({packet_id: pid, doc_id: did, jurisdiction: 'Cambridge, MA', category: 'security_deposits', lifecycle: 'enacted', effective_date: '2027-01-01', valid_through: null, title: 'Synthetic test deposit law', citation: 'Cambridge Municipal Code § 8.99.010', requirement: 'Maximum deposit is 2 months of rent.', key_value: '2 months of rent', coverage_conditions: 'All residential rentals', applicability: {conditions: [], coverage_quotes: [], per_tenancy: null}, quoted_span: SPAN, exemptions: null, penalty: null, interaction: null, relations: [], confidence: .8, conflict_flag: false, conflict_note: null, ...record}));
    if (messages.at(-1).role !== 'tool') {
      checks += rules.length;
      return {choices: [{finish_reason: 'tool_calls', message: {role: 'assistant', tool_calls: rules.map((rule, i) => ({id: 'check' + i, type: 'function', function: {name: 'check_record', arguments: JSON.stringify({record_json: JSON.stringify(rule)})}}))}}]};
    }
    for (const message of messages.filter(m => m.role === 'tool')) assert.match(message.content, /^ACCEPTED/);
    receipt = rules.map(rule => JSON.stringify(rule)).join('\n') + '\n' + JSON.stringify({packet_id: pid, n_rules: rules.length, note: null});
    return {choices: [{finish_reason: 'stop', message: {role: 'assistant', content: receipt}}], usage: {total_tokens: 100}};
  };
  const options = {dir: path.join(tmp, 'imports'), dataDir: findDataDir(), baseRules: () => structuredClone(base), addresses: () => structuredClone(addresses), precedence: () => [], review: () => [], config: () => new ApiConfig('synthetic-key'), agentOptions: {post}, ...extras};
  const store = new LawImports(options);
  return {tmp, store, options, setBase: value => {base = value;}, setAddresses: value => {addresses = value;}, counters: () => ({calls, checks}), raw: () => receipt};
}
async function complete(store, id) {while (store.detail(id).job.status === 'running') await nextTurn(); return store.detail(id);}

test('正文必填；单个或多个网址、空正文和错误信息都在模型调用前拒绝', async t => {
  const f = fixture(t);
  for (const text of ['', '  ', 'https://example.org/law', 'https://example.org/one\nhttps://example.org/two', 'SOURCE: https://example.org/law\nRETRIEVED: 2026-10-04\n']) assert.throws(() => f.store.submit({...INPUT, text}), /正文/);
  assert.throws(() => f.store.submit({...INPUT, source_url: 'file:///private/source'}), /来源网址/);
  assert.throws(() => f.store.submit({...INPUT, source_url: 'https://example.org/law'}), /来源网址/);
  assert.throws(() => f.store.submit({text: 10}), /格式/);
  assert.throws(() => f.store.submit({text: 'binary\0text'}), /可读/);
  assert.equal(f.counters().calls, 0); assert.equal(fs.existsSync(f.options.dir), false);
});

test('只交正文即可解析；地区、名称、状态和日期来自模型，不由表单预填', {timeout: 15000}, async t => {
  const f = fixture(t), job = f.store.submit({...INPUT, title: 'wrong title', jurisdiction: 'CA', mode: 'update', target_rule_id: 'missing', version_from: '2026-02-31', as_of: '2099-01-01'}), detail = await complete(f.store, job.id);
  assert.equal(detail.job.status, 'ready', detail.job.error); assert.ok(f.counters().checks > 0);
  assert.equal(detail.input.mode, 'auto'); assert.equal(detail.job.title, 'Synthetic test deposit law'); assert.equal(detail.job.jurisdiction, 'Cambridge, MA');
  assert.deepEqual(detail.job.recognized, {added: 1, updated: 0}); assert.equal(detail.preview.as_of, '2026-10-01');
  assert.equal(detail.job.progress.done, detail.job.progress.total);
  assert.equal(f.store.rules('2027-01-02').length, 0);
  assert.deepEqual(detail.preview.affected.map(a => a.address_id), ['C']);
  assert.equal(detail.preview.affected[0].changes[0].before, null);
  assert.equal(detail.preview.affected[0].changes[0].after.result, 'not_yet_effective');
  assert.deepEqual(detail.preview.rule_scopes[0].affected_address_ids, ['C']); assert.equal(detail.preview.rule_scopes[0].as_of, '2027-01-01');
  assert.equal(detail.preview.rules[0].after.effective_date, '2027-01-01'); assert.equal(detail.preview.rules[0].after.status, 'not_yet_effective');
  assert.ok(detail.preview.cities.some(c => c.city === 'Boston, MA' && c.affected === 0));
  assert.equal(detail.preview.rules[0].after.quoted_span, SPAN);
  assert.equal(detail.preview.rules[0].after.source_url, '');
  f.store.apply(job.id); f.store.apply(job.id);
  assert.equal(readJson(path.join(f.options.dir, 'active.json')).imports.length, 1);
  const restarted = new LawImports(f.options); assert.equal(restarted.detail(job.id).job.status, 'applied');
  assert.equal(restarted.engine('2026-10-01').lookup('C', '2026-10-01')[0].result, 'not_yet_effective');
  assert.equal(restarted.engine('2027-01-02').lookup('B', '2027-01-02').length, 0);
  assert.match(restarted.source(job.doc_id), new RegExp(SPAN.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.equal(restarted.documents()[job.doc_id].origin, 'import');
});

test('新版金额变化即使前后均适用也计入影响；保留旧日期、旧编号和未提供的其他类别', {timeout: 15000}, async t => {
  const f = fixture(t, {record: {effective_date: '2026-01-01'}}), old = oldRule(), other = {...old, team_rule_id: 'r-1001', category: 'application_screening_fees'}; f.setBase([old, other]);
  const job = f.store.submit({text: BODY.replace('2027', '2026')}), detail = await complete(f.store, job.id);
  assert.equal(detail.job.status, 'ready', detail.job.error);
  assert.deepEqual(detail.job.recognized, {added: 0, updated: 1});
  const change = detail.preview.affected[0].changes[0]; assert.equal(change.before.result, 'applies'); assert.equal(change.after.result, 'applies');
  assert.equal(change.after.rule.team_rule_id, old.team_rule_id); assert.ok(detail.preview.rules[0].changed_fields.includes('key_value'));
  assert.equal(detail.preview.preserved_rules.length, 1); f.store.apply(job.id);
  assert.equal(f.store.rules('2025-12-31')[0].key_value, '1 month of rent');
  assert.equal(f.store.rules('2027-01-02').find(r => r.team_rule_id === old.team_rule_id).key_value, '2 months of rent');
  assert.deepEqual(f.store.rules('2027-01-02').find(r => r.team_rule_id === other.team_rule_id), other);
  assert.equal(old.key_value, '1 month of rent'); assert.equal(f.store.source(job.doc_id).includes(BODY.replace('2027', '2026')), true);
  const cases = [{test_id: 'DATE', type: 'as_of', rule_ids: ['LAW'], as_of_before: '2025-12-31', as_of_after: '2026-01-02'}];
  const tracker = new ChangeTracker(f.store.engine('2027-01-02'), cases, {LAW: {jurisdiction: 'Cambridge, MA', category: 'security_deposits'}}, day => f.store.engine(day));
  const [, audit] = tracker.run(); assert.equal(audit.tests.DATE.query_dates.as_of_before, '2025-12-31');
  assert.match(tracker.audit_cache['2025-12-31'].C.rules[0].source.source_url, /old/);
  assert.equal(tracker.audit_cache['2026-01-02'].C.rules[0].source.source_url, '');
});

test('资料改变需刷新影响结果；重复正文自动对应已有法规而不新增重复规则', {timeout: 15000}, async t => {
  const f = fixture(t), job = f.store.submit(INPUT); await complete(f.store, job.id);
  f.setAddresses({C: {state: 'MA', legal_city: 'Cambridge, MA', units: 8}});
  assert.throws(() => f.store.apply(job.id), error => error.status === 409 && /刷新影响/.test(error.message));
  assert.equal(fs.existsSync(path.join(f.options.dir, 'active.json')), false);
  f.store.preview(job.id); f.store.apply(job.id);
  const duplicate = f.store.submit(INPUT), detail = await complete(f.store, duplicate.id);
  assert.equal(detail.job.status, 'ready', detail.job.error); assert.deepEqual(detail.job.recognized, {added: 0, updated: 1});
  f.store.apply(duplicate.id); assert.equal(f.store.rules().length, 1);
});

test('模型未完成的回答不生效；继续任务复用已保存的正文与进度', {timeout: 15000}, async t => {
  let broken = true;
  const f = fixture(t); const goodPost = f.options.agentOptions.post;
  f.options.agentOptions.post = (messages, tools) => broken ? {choices: [{finish_reason: 'length', message: {role: 'assistant', content: 'unfinished'}}]} : goodPost(messages, tools);
  const job = f.store.submit(INPUT); let detail = await complete(f.store, job.id);
  assert.equal(detail.job.status, 'failed'); assert.equal(f.store.rules().length, 0); assert.throws(() => f.store.apply(job.id), /完成/);
  const source = f.store.detail(job.id).input.text; broken = false; f.store.retry(job.id); detail = await complete(f.store, job.id);
  assert.equal(detail.job.status, 'ready', detail.job.error); assert.equal(detail.input.text, source);
});

test('长正文全部分段，不因原有八万字符预算删掉段落', {timeout: 15000}, async t => {
  const f = fixture(t), text = Array.from({length: 1200}, (_, i) => `Section ${i + 1}\n${SPAN}`).join('\n\n');
  const job = f.store.submit({...INPUT, text}); const detail = await complete(f.store, job.id);
  assert.equal(detail.job.status, 'ready', detail.job.error);
  const index = readJson(path.join(f.options.dir, job.id, 'work/index.json'));
  assert.ok(index.docs[job.doc_id].raw_chars > 80000); assert.deepEqual(index.docs[job.doc_id].dropped_blocks, []);
  assert.ok(Object.keys(index.packets).length > 1); assert.equal(detail.job.progress.done, Object.keys(index.packets).length);
});

test('本地 HTTP 提交拒绝网址、跨站请求与表单；异步任务可查询和应用', {timeout: 15000}, async t => {
  const f = fixture(t), server = createServer({imports: f.store}); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => {server.close(resolve); server.closeAllConnections();}));
  const base = 'http://127.0.0.1:' + server.address().port;
  const post = (body, headers = {}) => fetch(base + '/api/imports', {method: 'POST', headers: {'Content-Type': 'application/json', ...headers}, body: JSON.stringify(body)});
  assert.equal((await post({...INPUT, text: 'https://example.org/law'})).status, 400);
  assert.equal((await post(INPUT, {Origin: 'https://another.example'})).status, 403);
  assert.equal((await post(INPUT, {'Sec-Fetch-Site': 'cross-site'})).status, 403);
  assert.equal((await post(INPUT, {'Content-Type': 'application/x-www-form-urlencoded'})).status, 415);
  const response = await post(INPUT); assert.equal(response.status, 202); const job = await response.json();
  const detail = await complete(f.store, job.id); assert.equal(detail.job.status, 'ready', detail.job.error);
  const get = await fetch(base + '/api/imports/' + job.id); assert.equal((await get.json()).preview.rules.length, 1);
  const applied = await fetch(base + '/api/imports/' + job.id + '/apply', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}'}); assert.equal(applied.status, 200); assert.equal((await applied.json()).job.status, 'applied');
  assert.equal((await fetch(base + '/api/imports/../../private')).status, 404);
  assert.equal(f.counters().checks, 1);
});

const ALG_QUOTE = 'A landlord shall not use an algorithmic rent-setting service.';
const ALG = {category: 'algorithmic_rent_setting', requirement: ALG_QUOTE, key_value: null, quoted_span: ALG_QUOTE};
const CASE_ADDRESSES = {CA: {state: 'CA', legal_city: 'Los Angeles, CA'}, H: {state: 'NJ', legal_city: 'Hoboken, NJ'}, J: {state: 'NJ', legal_city: 'Jersey City, NJ'}, N: {state: 'NJ', legal_city: 'Newark, NJ'}, B: {state: 'MA', legal_city: 'Boston, MA'}, C: {state: 'MA', legal_city: 'Cambridge, MA'}};
const caseDetail = async (f, text, expected) => {
  f.setAddresses(CASE_ADDRESSES); const job = f.store.submit({text}), detail = await complete(f.store, job.id);
  assert.equal(detail.job.status, 'ready', detail.job.error); assert.equal(detail.preview.change_cases.length, 1);
  const result = detail.preview.change_cases[0]; assert.equal(result.test.test_id, expected); return {job, detail, result};
};

test('官方 T1：从正文提取生效日期，跨日期的影响只包含加州地址', async t => {
  const f = fixture(t, {record: {...ALG, jurisdiction: 'CA', citation: 'AB 325 / SB 763', title: 'California algorithmic rent-setting law', effective_date: '2026-01-01'}});
  const {result} = await caseDetail(f, `California AB 325 / SB 763\n${ALG_QUOTE}\nAll residential rentals. Enacted; effective January 1, 2026.`, 'T1');
  assert.deepEqual(result.affected_address_ids, ['CA']); assert.deepEqual(result.missing_rules, []);
  assert.deepEqual(result.query_dates, {as_of_before: '2025-12-31', as_of_after: '2026-01-02'});
  assert.equal(result.transitions[0].before, 'not_yet_effective'); assert.equal(result.transitions[0].after, 'applies');
});

test('官方 T2：一份正文含两座城市的法规，自动分开提取且不覆盖 Newark', async t => {
  const records = ['Hoboken, NJ', 'Jersey City, NJ'].map(jurisdiction => ({...ALG, jurisdiction, title: jurisdiction + ' algorithmic ban', citation: jurisdiction + ' Ordinance § 1', effective_date: '2025-01-01'}));
  const f = fixture(t, {records});
  const {detail, result} = await caseDetail(f, `Hoboken, New Jersey Ordinance § 1\n${ALG_QUOTE}\nAll residential rentals. Enacted; effective January 1, 2025.\n\nJersey City, New Jersey Ordinance § 1\n${ALG_QUOTE}\nAll residential rentals. Enacted; effective January 1, 2025.`, 'T2');
  assert.equal(detail.preview.rules.length, 2); assert.deepEqual(result.missing_rules, []); assert.deepEqual(result.affected_address_ids, ['H', 'J']);
  assert.deepEqual(detail.preview.rule_scopes.map(s => s.affected_address_ids), [['H'], ['J']]);
});

test('官方 T3：NJ FAIR Act 尚未生效，未来覆盖 NJ，并复核与两个城市法规的关系', async t => {
  const preemption = 'This law preempts local algorithmic rent-setting ordinances.';
  const f = fixture(t, {record: {...ALG, jurisdiction: 'NJ', title: 'NJ FAIR Act', citation: 'NJ FAIR Act § 1', effective_date: '2027-07-01', relations: [{type: 'preempts_local', quote: preemption}]}});
  f.setBase(['Hoboken, NJ', 'Jersey City, NJ'].map((jurisdiction, i) => ({...oldRule(), ...ALG, team_rule_id: 'local-' + i, jurisdiction, level: 'city', effective_date: '2025-01-01', citation: jurisdiction + ' Ordinance § 1'})));
  const {job, detail, result} = await caseDetail(f, `New Jersey FAIR Act\n${ALG_QUOTE}\n${preemption}\nAll residential rentals. Enacted on July 20, 2026; effective July 1, 2027.`, 'T3');
  assert.deepEqual(result.affected_address_ids, ['H', 'J', 'N']); assert.deepEqual(result.conflict_flag_address_ids, ['H', 'J']); assert.deepEqual(result.missing_rules, []);
  assert.equal(result.transitions[0].before, 'not_yet_effective'); assert.equal(result.transitions[0].after, 'applies');
  assert.equal(detail.preview.rules[0].after.status, 'not_yet_effective'); assert.equal(detail.preview.rule_scopes[0].as_of, '2027-07-01');
  f.store.apply(job.id); assert.equal(f.store.engine('2026-10-01').lookup('N', '2026-10-01')[0].result, 'not_yet_effective');
  assert.equal(f.store.engine('2027-07-02').lookup('N', '2027-07-02')[0].result, 'applies');
});

test('官方 T4：两项麻州提案只给出如果通过的范围，查询不能当作现行法律', async t => {
  const records = ['S.2983', 'H.5222'].map(citation => ({...ALG, jurisdiction: 'MA', title: 'Massachusetts bill ' + citation, citation, lifecycle: 'pending_bill', effective_date: null}));
  const f = fixture(t, {records});
  const {job, detail, result} = await caseDetail(f, `Massachusetts pending bills S.2983 and H.5222\n${ALG_QUOTE}\nAll residential rentals. Both bills are pending and have not been enacted.`, 'T4');
  assert.deepEqual(result.affected_address_ids, ['B', 'C']); assert.deepEqual(result.missing_rules, []);
  assert.ok(detail.preview.rules.every(r => r.after.status === 'pending')); f.store.apply(job.id);
  assert.ok(f.store.engine().lookup('C', '2026-10-01').every(r => r.result === 'pending'));
});

test('官方 T5：公投提案失败后受影响列表为空，Boston 和 Cambridge 不出现涨租上限', async t => {
  const quote = 'The rent-control ballot question IP 25-21 was struck on June 23, 2026.';
  const f = fixture(t, {record: {jurisdiction: 'MA', title: 'Massachusetts rent-control ballot question', citation: 'IP 25-21', category: 'rent_increase_limits', lifecycle: 'failed', effective_date: null, key_value: null, requirement: 'The ballot measure failed and establishes no rent cap.', quoted_span: quote}});
  const {job, detail, result} = await caseDetail(f, `Massachusetts rent-control ballot question\n${quote}`, 'T5');
  assert.deepEqual(result.affected_address_ids, []); assert.deepEqual(result.missing_rules, []); assert.deepEqual(detail.preview.rule_scopes[0].affected_address_ids, []);
  assert.equal(detail.preview.rules[0].after.status, 'failed'); f.store.apply(job.id);
  for (const id of ['B', 'C']) assert.equal(f.store.engine().lookup(id, '2026-10-01').some(r => r.result === 'applies'), false);
});
