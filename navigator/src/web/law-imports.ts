import fs from 'node:fs';
import path from 'node:path';
import {randomUUID} from 'node:crypto';
import {setImmediate as nextTurn} from 'node:timers/promises';
import type {Address, Data, Rule} from '../types.js';
import {clone, isObject, readJson, sha256, writeJson, writeText} from '../util.js';
import {DEFAULT_AS_OF, Paths, ROOT, findDataDir} from '../nav/config.js';
import {addExtraDoc, splitHeader} from '../nav/corpus.js';
import {citationKey} from '../nav/facts.js';
import {prepare, DEFAULT_MAX_CHARS} from '../nav/packets.js';
import {loadApiConfig} from '../nav/api.js';
import {runAgentApi, type AgentOptions} from '../nav/agent.js';
import {loadRules, LookupEngine, statusOn} from '../lookup/engine.js';
import {DISCLAIMER, matches, queryDate} from '../lookup/common.js';
import {ChangeTracker} from '../changes/engine.js';

export class ImportError extends Error {
  constructor(message: string, public status = 400) {super(message);}
}
type Input = {title: string; text: string; jurisdiction: string; source_url: string; retrieved: string; mode: 'auto' | 'add' | 'update'; target_rule_id: string; version_from: string; as_of: string};
type Operation = {before: Rule | null; after: Rule; version_from?: string; history_date_unknown?: boolean};
type Options = {
  dir?: string; dataDir?: string; baseRules?: () => Rule[]; addresses?: () => Record<string, Address>;
  precedence?: () => Data[]; review?: () => Data[];
  config?: typeof loadApiConfig; run?: typeof runAgentApi; agentOptions?: AgentOptions;
  tests?: Data[]; ruleMap?: Data;
};
const ruleKey = (r: Rule): string => JSON.stringify([r.jurisdiction, r.category, citationKey(r.citation)]);
const lawKey = (r: Rule): string => JSON.stringify([r.jurisdiction, citationKey(r.citation)]);
const now = (): string => new Date().toISOString();
const FACT_FIELDS = ['lifecycle', 'requirement', 'key_value', 'coverage_conditions', 'applicability', 'exemptions', 'penalty', 'effective_date', 'valid_through', 'interaction', 'relations'];
const viewFields = (r: Rule): Data => Object.fromEntries(['team_rule_id', 'jurisdiction', 'category', 'title', 'citation', ...FACT_FIELDS, 'source_doc_id', 'source_url', 'retrieved', 'quoted_span', 'warnings', 'confidence', 'conflict_flag', 'conflict_note'].map(k => [k, r[k] ?? null]));
// Compare ordered JSON objects as facts, independently of key insertion order.
const canonical = (v: any): any => Array.isArray(v) ? v.map(canonical) : isObject(v) ? Object.fromEntries(Object.keys(v).sort().map(k => [k, canonical(v[k])])) : v;
const fingerprint = (v: any): string => sha256(JSON.stringify(canonical(v)));

export class LawImports {
  readonly dir: string;
  private running = new Map<string, Promise<void>>();
  constructor(private options: Options = {}) {this.dir = options.dir ?? path.join(ROOT, 'work/law_imports');}
  private file(id: string, name: string): string {
    if (!/^[0-9a-f-]{36}$/.test(id)) throw new ImportError('提交记录不存在。', 404);
    return path.join(this.dir, id, name);
  }
  private read(id: string): Data {
    const file = this.file(id, 'job.json'); if (!fs.existsSync(file)) throw new ImportError('提交记录不存在。', 404);
    const job = readJson(file);
    if (this.active().includes(id)) job.status = 'applied';
    else if (job.status === 'running' && !this.running.has(id)) {
      job.status = 'failed'; job.stage = 'interrupted'; job.error = '提取因服务重启而中断，已保存进度，可以继续。'; this.save(job);
    }
    return job;
  }
  private save(job: Data): void {job.updated_at = now(); this.atomic(this.file(job.id, 'job.json'), job);}
  private atomic(file: string, value: Data): void {
    const tmp = file + '.' + randomUUID() + '.tmp'; writeJson(tmp, value, false); fs.renameSync(tmp, file);
  }
  private active(): string[] {const f = path.join(this.dir, 'active.json'); return fs.existsSync(f) ? readJson(f).imports : [];}
  private base(): Rule[] {return this.options.baseRules?.() ?? loadRules();}
  private addresses(): Record<string, Address> {return this.options.addresses?.() ?? readJson(path.join(ROOT, 'work/addresses_resolved.json'));}
  private precedence(): Data[] {return this.options.precedence?.() ?? readJson(path.join(ROOT, 'lookup/precedence.json'));}
  private review(): Data[] {return this.options.review?.() ?? readJson(path.join(ROOT, 'lookup/review_pairs.json'));}
  private context(): string {return fingerprint([this.base(), this.addresses(), this.precedence(), this.review(), this.active()]);}
  private applyOperations(rules: Rule[], input: Input, ops: Operation[], day: string): Rule[] {
    if (input.mode === 'update' && day < input.version_from) return rules;
    const byId = new Map(rules.map(r => [r.team_rule_id, r]));
    for (const op of ops) {
      if (input.mode === 'auto' && op.before && op.version_from && day < op.version_from) {
        if (op.history_date_unknown) byId.set(op.after.team_rule_id, {...clone(op.before), lifecycle: null, import_history_unknown: true});
        continue;
      }
      byId.set(op.after.team_rule_id, clone(op.after));
    }
    return [...byId.values()];
  }
  rules(day = DEFAULT_AS_OF, draft?: {input: Input; operations: Operation[]}): Rule[] {
    queryDate(day); let rules = this.base();
    // A later-dated revision always governs after its switch date, even if an
    // older revision was imported later. New laws stay visible before enactment.
    const applied = this.active().map(id => ({input: readJson(this.file(id, 'input.json')) as Input, operations: readJson(this.file(id, 'operations.json')).operations as Operation[]}));
    if (draft) applied.push(draft);
    applied.sort((a, b) => (a.input.mode === 'update' ? a.input.version_from : '').localeCompare(b.input.mode === 'update' ? b.input.version_from : ''));
    // Order individual auto-matched rules by dates read from their text. Legacy
    // manually dated imports remain readable, but new submissions are text-only.
    const auto: {input: Input; operations: Operation[]}[] = [];
    for (const item of applied) {
      if (item.input.mode === 'auto') for (const op of item.operations) auto.push({input: item.input, operations: [op]});
      else rules = this.applyOperations(rules, item.input, item.operations, day);
    }
    auto.sort((a, b) => (a.operations[0].version_from || '').localeCompare(b.operations[0].version_from || ''));
    for (const item of auto) rules = this.applyOperations(rules, item.input, item.operations, day);
    return rules;
  }
  engine(day = DEFAULT_AS_OF, draft?: {input: Input; operations: Operation[]}): LookupEngine {
    return new LookupEngine(this.rules(day, draft), this.addresses(), this.precedence(), this.review());
  }
  documents(): Data {
    const docs: Data = {};
    for (const id of this.active()) {
      const job = this.read(id), index = readJson(this.file(id, 'work/index.json'));
      docs[job.doc_id] = {...index.docs[job.doc_id], origin: 'import', title: job.title, jurisdictions: job.jurisdiction, import_id: id};
    }
    return docs;
  }
  source(docId: string): string | null {
    for (const id of this.active()) {const job = this.read(id); if (job.doc_id === docId) return fs.readFileSync(this.file(id, 'corpus/text/' + docId + '.txt'), 'utf8');}
    return null;
  }
  list(): Data {
    let configured = false; try {configured = Boolean((this.options.config ?? loadApiConfig)().key);} catch { /* reported without exposing credentials */ }
    const jobs = fs.existsSync(this.dir) ? fs.readdirSync(this.dir).filter(id => /^[0-9a-f-]{36}$/.test(id)).map(id => this.read(id)).sort((a, b) => b.created_at.localeCompare(a.created_at)) : [];
    return {jobs, configured, disclaimer: DISCLAIMER};
  }
  detail(id: string): Data {
    const job = this.read(id), input = readJson(this.file(id, 'input.json')), f = this.file(id, 'preview.json');
    return {job, input, preview: fs.existsSync(f) ? readJson(f) : null, disclaimer: DISCLAIMER};
  }
  private validate(raw: unknown): Input {
    if (!isObject(raw)) throw new ImportError('请提交法规正文。');
    const str = (k: string): string => {if (raw[k] != null && typeof raw[k] !== 'string') throw new ImportError('提交信息格式错误：' + k); return (raw[k] ?? '').trim();};
    const text = str('text').replace(/\r\n?/g, '\n');
    const [metadata, body] = splitHeader(text);
    if (!body.trim() || body.trim().split(/\s+/).every(word => /^https?:\/\/\S+$/i.test(word))) throw new ImportError('必须提交法规正文，不能只提交网址。');
    if (text.includes('\0')) throw new ImportError('正文必须是可读的文本，请使用 UTF-8 文本文件。');
    if (raw.source_url) throw new ImportError('此入口只接收法规正文，不接收单独提交的来源网址。');
    const source_url = metadata.SOURCE || '';
    if (source_url) {let u: URL; try {u = new URL(source_url);} catch {throw new ImportError('来源网址格式不正确。');} if (!['http:', 'https:'].includes(u.protocol) || u.username || u.password) throw new ImportError('来源网址必须是公开的 http 或 https 地址。');}
    return {title: '提交的法规正文', text, jurisdiction: '', source_url, retrieved: metadata.RETRIEVED || now(), mode: 'auto', target_rule_id: '', version_from: '', as_of: DEFAULT_AS_OF};
  }
  submit(raw: unknown): Data {
    const input = this.validate(raw);
    // Fail before accepting a task when the server lacks model configuration.
    (this.options.config ?? loadApiConfig)();
    const id = randomUUID(), used = this.list().jobs.map((j: Data) => Number(j.doc_id.slice(1))), doc_id = 'U' + String(Math.max(0, ...used) + 1).padStart(4, '0');
    const job: Data = {id, doc_id, title: input.title, jurisdiction: input.jurisdiction, mode: input.mode, status: 'running', stage: 'preparing', created_at: now(), events: [], progress: {done: 0, total: 0}};
    writeJson(this.file(id, 'input.json'), input, false); this.save(job); this.launch(job); return job;
  }
  retry(id: string): Data {
    const job = this.read(id); if (job.status !== 'failed') throw new ImportError('只有未完成的提取任务可以继续。', 409);
    (this.options.config ?? loadApiConfig)(); job.status = 'running'; job.stage = 'preparing'; delete job.error; this.save(job); this.launch(job); return job;
  }
  private launch(job: Data): void {
    const promise = this.extract(job); this.running.set(job.id, promise); void promise.finally(() => this.running.delete(job.id));
  }
  private async extract(job: Data): Promise<void> {
    // Yield before reading the job so running is registered and the POST can
    // return immediately while model calls continue independently of the page.
    await nextTurn();
    const id = job.id, input = readJson(this.file(id, 'input.json')) as Input;
    const paths = new Paths(path.join(this.dir, id, 'pack'), path.join(this.dir, id, 'work'), path.join(this.dir, id, 'outputs'), path.join(this.dir, id, 'corpus'));
    const event = (stage: string, message: string): void => {job.stage = stage; job.events.push({at: now(), message}); this.save(job);};
    try {
      const dataDir = this.options.dataDir ?? findDataDir();
      writeText(paths.schema_file, fs.readFileSync(path.join(dataDir, 'schema/rule_record.schema.json'), 'utf8'));
      if (!fs.existsSync(paths.index_file)) {
        addExtraDoc(paths, splitHeader(input.text)[1], input.jurisdiction, input.source_url, job.doc_id, 'user-supplied text', input.retrieved);
        // Split a long document into complete packets, without omitting its
        // lower-ranked sections or imposing an overall text budget.
        const index = prepare(paths, input.as_of, DEFAULT_MAX_CHARS, Infinity, [job.doc_id]); job.progress.total = Object.keys(index.packets).length;
      }
      event('extracting', '正文已保存，智能体正在读取并提取规则。');
      const code = await (this.options.run ?? runAgentApi)(paths, (this.options.config ?? loadApiConfig)(), {...this.options.agentOptions, only: [job.doc_id], emit: () => {
        const file = path.join(paths.work_dir, 'audit.json');
        if (fs.existsSync(file)) {const counts = readJson(file).counts; job.progress = {done: counts.packets_done, total: counts.packets_total}; this.save(job);}
      }});
      if (code !== 0) throw new ImportError('提取没有全部完成，请检查本地模型配置后继续。已完成的部分已保存。');
      event('checking', '全部正文已处理，正在检查规则和原文引用。');
      const extracted: Rule[] = readJson(path.join(paths.work_dir, 'rules_enriched.json'));
      if (!extracted.length) throw new ImportError('正文中没有提取到本项目所支持的住房规则。');
      const existing = this.rules('9999-12-31');
      const operations: Operation[] = extracted.map((r, i) => {
        const previous = existing.find(old => ruleKey(old) === ruleKey(r));
        const after = {...r, team_rule_id: previous?.team_rule_id ?? `u-${id}-${i + 1}`, import_id: id};
        const dated = r.lifecycle === 'enacted' && /^\d{4}-\d{2}-\d{2}$/.test(r.effective_date || '');
        return {before: previous ?? null, after, version_from: previous ? dated ? r.effective_date! : input.as_of : '', history_date_unknown: Boolean(previous && !dated && fingerprint(FACT_FIELDS.map(k => previous[k] ?? null)) !== fingerprint(FACT_FIELDS.map(k => r[k] ?? null)))};
      });
      job.title = [...new Set(extracted.map(r => r.title || r.citation))].join(' / ');
      job.jurisdiction = [...new Set(extracted.map(r => r.jurisdiction))].join(' / ');
      job.recognized = {added: operations.filter(o => !o.before).length, updated: operations.filter(o => o.before).length};
      writeJson(this.file(id, 'operations.json'), {operations}, false);
      event('comparing', '引用检查已完成，正在比较规则和全部样本地址的结论。'); await nextTurn();
      this.preview(id); job.status = 'ready'; event('ready', '解析结果和地址影响已生成。');
    } catch (error) {
      job.status = 'failed'; job.error = (error as Error).message; event('failed', '本次提取未完成，现有规则未被修改。');
    }
  }
  preview(id: string): Data {
    const job = this.read(id), input = readJson(this.file(id, 'input.json')) as Input, f = this.file(id, 'operations.json');
    if (!fs.existsSync(f) || job.status === 'applied') throw new ImportError('当前提交不能重新比较。', 409);
    const operations = readJson(f).operations as Operation[], all = this.rules('9999-12-31');
    for (const op of operations) {
      const current = all.find(r => r.team_rule_id === op.after.team_rule_id);
      if (op.before && (!current || ruleKey(current) !== ruleKey(op.before))) throw new ImportError('对应旧法规已改变，请重新提交。', 409);
      if (!op.before && all.some(r => ruleKey(r) === ruleKey(op.after))) throw new ImportError('同一法规已被其他提交加入，请重新提交正文以匹配已有记录。', 409);
    }
    const before = this.engine(input.as_of), after = this.engine(input.as_of, {input, operations}), affected: Data[] = [], cities: Data = {};
    const rowView = (row: Data, eng: LookupEngine): Data => ({...row, rule: viewFields(eng.by_id[row.team_rule_id])});
    const signature = (row: Data | undefined, eng: LookupEngine): string => row ? fingerprint([row.result, row.conflict_flag, Object.fromEntries(FACT_FIELDS.map(k => [k, eng.by_id[row.team_rule_id][k] ?? null]))]) : '';
    for (const address of Object.keys(before.addresses).sort()) {
      const oldRows = new Map(before.lookup(address, input.as_of).map(r => [r.team_rule_id, r])), newRows = new Map(after.lookup(address, input.as_of).map(r => [r.team_rule_id, r]));
      const changes = [...new Set([...oldRows.keys(), ...newRows.keys()])].filter(rid => signature(oldRows.get(rid), before) !== signature(newRows.get(rid), after)).map(rid => ({team_rule_id: rid, before: oldRows.has(rid) ? rowView(oldRows.get(rid)!, before) : null, after: newRows.has(rid) ? rowView(newRows.get(rid)!, after) : null}));
      const a = before.addresses[address], city = a.legal_city || a.state, flagged = changes.some(c => c.after?.conflict_flag || c.before?.conflict_flag || c.after?.result === 'unknown');
      cities[city] ??= {city, total: 0, affected: 0, flagged: 0}; cities[city].total++;
      if (changes.length) {affected.push({address_id: address, street_address: a.street_address, city, flagged, changes}); cities[city].affected++; if (flagged) cities[city].flagged++;}
    }
    const preview = {
      as_of: input.as_of, version_from: input.version_from, context: this.context(), affected, cities: Object.values(cities),
      rules: operations.map(op => {const current = all.find(r => r.team_rule_id === op.after.team_rule_id); const b = op.before ? current! : null; return {before: b ? viewFields(b) : null, after: {...viewFields(op.after), status: statusOn(op.after, input.as_of)}, changed_fields: [...FACT_FIELDS, 'quoted_span', 'source_url'].filter(k => fingerprint(b?.[k] ?? null) !== fingerprint(op.after[k] ?? null))};}),
      warnings: [...operations.flatMap(op => op.after.warnings || []), ...operations.filter(op => op.history_date_unknown).map(op => `${op.after.citation}：正文没有给出准确的变更日期，更早日期的历史状态保留为不确定。`)], preserved_rules: all.filter(r => operations.some(op => op.before && lawKey(r) === lawKey(op.after)) && !operations.some(o => o.after.team_rule_id === r.team_rule_id)).map(viewFields),
      change_cases: this.changeCases(input, operations),
      rule_scopes: this.ruleScopes(input, operations),
      disclaimer: DISCLAIMER,
    };
    this.atomic(this.file(id, 'preview.json'), preview); return preview;
  }
  private changeCases(input: Input, operations: Operation[]): Data[] {
    const tests: Data[] = this.options.tests ?? readJson(path.join(this.options.dataDir ?? findDataDir(), 'dev/change_tests.json'));
    const ruleMap = this.options.ruleMap ?? readJson(path.join(ROOT, 'changes/test_rule_map.json'));
    const related = tests.filter(c => c.rule_ids.some((rid: string) => ruleMap[rid] && operations.some(op => matches(op.after, ruleMap[rid]))));
    const draft = {input, operations}, dated = new Map<string, LookupEngine>();
    const engineAt = (day: string): LookupEngine => {if (!dated.has(day)) dated.set(day, this.engine(day, draft)); return dated.get(day)!;};
    const tracker = new ChangeTracker(engineAt(input.as_of), related, ruleMap, engineAt), [output, audit] = tracker.run();
    return related.map(c => {
      const info = audit.tests[c.test_id], transitions = new Map<string, Data>();
      for (const evidence of Object.values<any>(info.evidence)) {
        if (!isObject(evidence) || !evidence.before || !evidence.after) continue;
        for (const rid of new Set([...Object.keys(evidence.before), ...Object.keys(evidence.after)])) {
          const old = evidence.before[rid]?.[0] ?? null, next = evidence.after[rid]?.[0] ?? null, key = JSON.stringify([rid, old, next]);
          if (!transitions.has(key)) transitions.set(key, {team_rule_id: rid, before: old, after: next, addresses: 0}); transitions.get(key)!.addresses++;
        }
      }
      return {test: c, ...output[c.test_id], query_dates: info.query_dates, missing_rules: info.missing_rules, transitions: [...transitions.values()]};
    });
  }
  private ruleScopes(input: Input, operations: Operation[]): Data[] {
    const dated = new Map<string, LookupEngine>(), draft = {input, operations};
    return operations.map(op => {
      const rule = op.after, failed = ['failed', 'withdrawn'].includes(rule.lifecycle || '');
      const day = rule.lifecycle === 'enacted' && /^\d{4}-\d{2}-\d{2}$/.test(rule.effective_date || '') && rule.effective_date! > input.as_of ? rule.effective_date! : input.as_of;
      if (!dated.has(day)) dated.set(day, this.engine(day, draft)); const eng = dated.get(day)!;
      const addresses = failed ? [] : Object.keys(eng.addresses).sort().filter(id => eng.lookup(id, day).some(r => r.team_rule_id === rule.team_rule_id && ['applies', 'unknown', 'pending', 'superseded'].includes(r.result)));
      return {team_rule_id: rule.team_rule_id, as_of: day, lifecycle: rule.lifecycle, status: statusOn(rule, input.as_of), affected_address_ids: addresses};
    });
  }
  apply(id: string): Data {
    const job = this.read(id); if (job.status === 'applied') return this.detail(id);
    if (job.status !== 'ready') throw new ImportError('请等提取和比较完成后再应用。', 409);
    const preview = readJson(this.file(id, 'preview.json'));
    if (preview.context !== this.context()) throw new ImportError('规则或地址资料已改变，请点击“刷新影响结果”后再使用解析结果。', 409);
    // Commit the manifest last; readers see either the old set or all new rules.
    this.atomic(path.join(this.dir, 'active.json'), {imports: [...this.active(), id]}); job.status = 'applied'; job.applied_at = now(); this.save(job); return this.detail(id);
  }
}
