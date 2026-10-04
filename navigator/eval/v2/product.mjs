// Thin adapter to the shipped TypeScript modules. No answer key is imported here.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import readline from 'node:readline';
import {ROOT, Paths, defaultPaths, loadSchema} from '../../dist/nav/config.js';
import {Doc, loadCorpus} from '../../dist/nav/corpus.js';
import {loadIndex, Packet, renderPacket} from '../../dist/nav/packets.js';
import {Validator, runIngest, writeOutputs} from '../../dist/nav/ingest.js';
import {extractJsonObjects} from '../../dist/nav/parse.js';
import {converse, renderCore, loadCards} from '../../dist/nav/agent.js';
import {loadApiConfig, ChatClient} from '../../dist/nav/api.js';
import {LookupEngine, loadRules} from '../../dist/lookup/engine.js';
import {ChangeTracker} from '../../dist/changes/engine.js';
import {writeJson, writeText, csvRow, readJson} from '../../dist/util.js';

function context(input) {
  const p = defaultPaths(), docs = input.documents ? {} : loadCorpus(p);
  const index = input.documents ? {as_of: input.as_of, packets: {}} : loadIndex(p);
  for (const d of input.documents || []) {
    const doc = new Doc(d.id, d.jurisdiction, d.url, 'synthetic', 'yes', '2026-10-04', 'ok', null);
    doc.body = d.text; doc.origin = 'synthetic'; docs[d.id] = doc;
    index.packets[d.id + '-01'] = {doc_id: d.id, part: 1, parts: 1};
  }
  return {docs, index, validator: new Validator(docs, index, loadSchema(p), input.as_of)};
}
function inspect(input, ctx) {
  const [objects, problems] = extractJsonObjects(input.answer), accepted = [], rejected = [];
  for (const raw of objects.filter(x => x.category !== undefined)) {
    if (raw.packet_id !== input.packet_id) {rejected.push({error: 'foreign packet'}); continue;}
    const [rule, errors] = ctx.validator.check(raw);
    if (rule) accepted.push(rule); else rejected.push({errors});
  }
  const receipts = objects.filter(x => x.n_rules !== undefined), n = objects.filter(x => x.category !== undefined).length;
  const clean = !problems.length && !rejected.length && receipts.length === 1 && receipts[0].packet_id === input.packet_id && receipts[0].n_rules === n;
  return {accepted, rejected, problems, clean};
}
// The change-test chain: model answers for a set of packets -> the shipped ingest (with overrides) -> lookup engine -> change tracker.
// Real packets use the project's corpus, index, overrides and 500 resolved addresses; constructed documents get a throw-away pack.
function chain(input) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'navigator-chain-'));
  try {
    const real = defaultPaths(); let p, addresses;
    if (input.documents) {
      p = new Paths(path.join(tmp, 'pack'), path.join(tmp, 'work'), path.join(tmp, 'outputs'), path.join(tmp, 'extra'));
      const columns = ['doc_id','jurisdictions','url','source_type','capture','retrieved_at','sha256','text_file','status'];
      writeText(p.manifest, csvRow(columns) + '\n' + input.documents.map(d => csvRow([d.id,d.jurisdiction,d.url,'synthetic','yes','2026-10-04','','text/' + d.id + '.txt','ok'])).join('\n'));
      for (const d of input.documents) writeText(path.join(p.corpus_dir, 'text', d.id + '.txt'), d.text);
      writeJson(p.schema_file, loadSchema(real));
      writeJson(p.index_file, {as_of: input.as_of, docs: Object.fromEntries(input.documents.map(d => [d.id,{packets:[d.id+'-01']}])), packets: Object.fromEntries(input.documents.map(d => [d.id+'-01',{doc_id:d.id,part:1,parts:1}]))});
      addresses = input.addresses;
    } else {
      p = new Paths(real.data_dir, path.join(tmp, 'work'), path.join(tmp, 'outputs'), real.extra_dir);
      fs.mkdirSync(p.work_dir, {recursive: true});
      fs.copyFileSync(real.index_file, p.index_file);
      if (fs.existsSync(path.join(real.work_dir, 'overrides.json'))) fs.copyFileSync(path.join(real.work_dir, 'overrides.json'), path.join(p.work_dir, 'overrides.json'));
      addresses = readJson(path.join(real.work_dir, 'addresses_resolved.json'));
    }
    for (const [pid, text] of Object.entries(input.answers)) writeText(path.join(p.inbox_dir, pid + '.jsonl'), text);
    const result = runIngest(p, input.as_of, false); writeOutputs(p, result);
    const engine = new LookupEngine(loadRules(path.join(p.work_dir, 'rules_enriched.json'), undefined, {}), addresses);
    const rules = engine.rules.map(r => ({team_rule_id: r.team_rule_id, jurisdiction: r.jurisdiction, category: r.category, citation: r.citation, lifecycle: r.lifecycle,
      effective_date: r.effective_date ?? null, valid_through: r.valid_through ?? null, relations: (r.relations || []).map(x => x.type)}));
    const base = {rules, states: result.states, rejected: result.rejected.length};
    try {
      const [changes, audit] = new ChangeTracker(engine, input.tests, input.rule_map).run();
      return {...base, changes, audit};
    } catch (e) {return {...base, error: String(e.message)};}
  } finally {fs.rmSync(tmp, {recursive: true, force: true});}
}
export async function execute(input) {
  if (input.op === 'chain') return chain(input);
  if (input.op === 'config') {const c = loadApiConfig(undefined, input.model, undefined, false); return {model: c.model, endpoint: c.endpoint, configured: !!c.key && c.key !== 'your-deepseek-api-key'};}
  if (input.op === 'engine') return new LookupEngine(input.rules, input.addresses, input.precedence || [], input.review || []).all(input.as_of);
  if (input.op === 'pipeline') {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'navigator-eval-'));
    try {
      const p = new Paths(path.join(tmp, 'pack'), path.join(tmp, 'work'), path.join(tmp, 'outputs'), path.join(tmp, 'extra'));
      const columns = ['doc_id','jurisdictions','url','source_type','capture','retrieved_at','sha256','text_file','status'];
      writeText(p.manifest, csvRow(columns) + '\n' + input.documents.map(d => csvRow([d.id,d.jurisdiction,d.url,'synthetic','yes','2026-10-04','','text/' + d.id + '.txt','ok'])).join('\n'));
      for (const d of input.documents) writeText(path.join(p.corpus_dir, 'text', d.id + '.txt'), d.text);
      writeJson(p.schema_file, loadSchema(defaultPaths()));
      writeJson(p.index_file, {as_of: input.as_of, docs: Object.fromEntries(input.documents.map(d => [d.id,{packets:[d.id+'-01']} ])), packets: Object.fromEntries(input.documents.map(d => [d.id+'-01',{doc_id:d.id,part:1,parts:1}]))});
      writeText(path.join(p.inbox_dir, 'answers.jsonl'), input.answer);
      const result = runIngest(p, input.as_of, false);
      const engine = new LookupEngine(result.rules, input.addresses, input.precedence || [], []);
      return {rules: result.rules, rejected: result.rejected, states: result.states, lookup: engine.all(input.as_of)};
    } finally {fs.rmSync(tmp, {recursive:true, force:true});}
  }
  const ctx = context(input);
  if (input.op === 'inspect') return inspect(input, ctx);
  if (input.op !== 'extract') throw new Error('Unknown eval operation');
  const config = loadApiConfig(undefined, input.model), client = new ChatClient(config), calls = [];
  const system = renderCore(input.as_of), cards = loadCards();
  let user;
  if (input.documents) {
    const doc = ctx.docs[input.packet_id.split('-')[0]];
    user = renderPacket(new Packet(input.packet_id, doc.doc_id, 1, 1, doc.body, {}, 'Synthetic evaluation document', [], []), doc, input.as_of);
  } else user = fs.readFileSync(path.join(defaultPaths().packets_dir, input.packet_id + '.md'), 'utf8');
  // API exposes only read_card and check_record; neither can read local labels/files.
  const post = async (messages, specs) => {
    const start = performance.now(); let body;
    try {body = await client.post(messages, specs);} catch (e) {calls.push({status:'transport_error', latency_s:(performance.now()-start)/1000}); throw e;}
    calls.push({model:body.model ?? null, usage:body.usage ?? null, latency_s:(performance.now()-start)/1000, response:body});
    if (body.model !== config.model) throw new Error('served_model_mismatch: ' + String(body.model));
    return body;
  };
  try {
    const [answer, log] = await converse(post, system, user, cards, ctx.validator);
    return {answer, model:config.model, calls, trace:[{role:'system',content:system},{role:'user',content:user},...log.messages], status:'ok'};
  } catch (e) {
    return {status: calls.at(-1)?.response?.choices?.[0]?.finish_reason === 'length' ? 'truncated' : 'error', error:String(e.message), model:config.model, calls,
      trace:[{role:'system',content:system},{role:'user',content:user},...calls.map(c=>({role:'assistant',content:JSON.stringify(c.response ?? c)}))]};
  }
}
for await (const line of readline.createInterface({input:process.stdin, crlfDelay:Infinity})) {
  try {process.stdout.write(JSON.stringify({value:await execute(JSON.parse(line))})+'\n');}
  catch(e) {process.stdout.write(JSON.stringify({error:String(e.message)})+'\n');}
}
