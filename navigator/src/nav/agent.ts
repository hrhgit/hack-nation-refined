import fs from 'node:fs';
import path from 'node:path';
import type {Data, Rule} from '../types.js';
import {isObject, jsonProblem, pool, pyStr, repr, sha256, slice, writeJson, writeText} from '../util.js';
import {LookupEngine} from '../lookup/engine.js';
import {ApiConfig, ApiError, ChatClient, RunOptions, attemptName, readPackets, select, validateFinal} from './api.js';
import {KNOWN_JURISDICTIONS, ROOT, Paths, loadSchema} from './config.js';
import {loadCorpus} from './corpus.js';
import {Validator, pendingPackets, runIngest, writeOutputs} from './ingest.js';
import {loadIndex, renderPacketInput} from './packets.js';
export const AGENT_DIR = process.env.NAV_AGENT_DIR || path.join(ROOT, 'prompts/agent'), AS_OF = '2026-10-01';
const PROBES: [number | null, number | null, number | null][] = [[2022, 20, null], [2005, 20, null], [1990, 20, null], [1970, 20, null], [null, 20, null], [1950, 2, null], [1950, 5, null], [1950, null, null]];
const WORDS: Data = {applies: 'applies', unknown: 'unknown (a fact is missing)', excluded: 'NOT in the results (the building is left out)', not_yet_effective: 'not yet effective', pending: 'pending (a proposal)', superseded: 'superseded'};
const CITY_FOR_STATE: Data = {CA: 'Los Angeles, CA', NJ: 'Newark, NJ', MA: 'Boston, MA'};
export type Post = (messages: Data[], specs: Data[]) => Promise<Data> | Data;
export const cardNames = (): string[] => fs.readdirSync(path.join(AGENT_DIR, 'cards')).filter(f => f.endsWith('.md')).map(f => f.slice(0, -3)).sort();
export const loadCards = (): Record<string, string> => Object.fromEntries(cardNames().map(n => [n, fs.readFileSync(path.join(AGENT_DIR, 'cards', n + '.md'), 'utf8')]));
export const renderCore = (asOf: string): string => fs.readFileSync(path.join(AGENT_DIR, 'core.md'), 'utf8').replaceAll('{{AS_OF}}', asOf).replaceAll('{{JURISDICTIONS}}', KNOWN_JURISDICTIONS.map(j => `"${j}"`).join(', '));
export function toolSpecs(tools = ['cards', 'check']): Data[] {
  const specs: Data[] = []; if (tools.includes('cards')) specs.push({type: 'function', function: {name: 'read_card', description: 'Read one short reference card with the detailed rules for one kind of field.', parameters: {type: 'object', properties: {name: {type: 'string', enum: cardNames()}}, required: ['name']}}});
  if (tools.includes('check')) specs.push({type: 'function', function: {name: 'check_record', description: "Run the pipeline's checks on one finished record and show how a program will read its conditions.", parameters: {type: 'object', properties: {record_json: {type: 'string', description: 'one record as a JSON object, as text'}}, required: ['record_json']}}}); return specs;
}
export function outcome(rule: Data, facts: Data, asOf: string): string {const state = rule.level === 'state' ? rule.jurisdiction : rule.jurisdiction.split(', ').at(-1), city = rule.level === 'city' ? rule.jurisdiction : CITY_FOR_STATE[state] || state, address = {state, legal_city: city, resolved_by: 'geocoder', ...facts}; const rows = new LookupEngine([{...rule, team_rule_id: 'probe'} as Rule], {P: address}, [], []).lookup('P', asOf); return rows[0]?.result || 'excluded';}
export function describeConditions(a: Data): string {
  const keys = ['built_on_or_before', 'built_before', 'built_after', 'built_on_or_after', 'min_units', 'max_units', 'exempt_if_newer_than_years', 'covered_if_newer_than_years', 'owner_exempt_if_units_at_most', 'date_basis'], parts = keys.filter(k => a[k] != null).map(k => k + '=' + pyStr(a[k]));
  for (const item of a.alternatives || []) parts.push(`covered if ${Object.entries(item.flats).filter(([k]) => k !== 'date_basis').map(([k, v]) => `${k}=${pyStr(v)}`).join(', ')}; a building outside that limit stays an open question because the text also covers: ${item.also}`);
  if (a.owner_dependent) parts.push('owner_dependent' + (a.owner_exempt_if_units_at_most != null ? '' : ' (no size limit: every building comes out unknown)')); if (a.other) parts.push('unresolved: ' + a.other); if (a.program_notes?.length) parts.push('note only (kinds of housing the data cannot show): ' + slice(a.program_notes.join('; '), 0, 160)); for (const d of a.deferred || []) parts.push('exemption only if the owner filed (open inside its reach): ' + d.note); if (a.per_tenancy) parts.push('note: ' + slice(a.per_tenancy, 0, 100)); return parts.join('; ') || 'none (the rule covers every building)';
}
export function checkRecord(validator: Validator, recordJson: string): string {
  let raw: unknown; try {raw = JSON.parse(recordJson);} catch (error) {return `NOT VALID JSON: ${jsonProblem(recordJson, error as Error)}. Send one record as a JSON object.`;} if (!isObject(raw)) return 'Send one record as a JSON object.';
  const [rule, errors, warns] = validator.check(raw); if (!rule) return 'REJECTED. Fix and check again:\n- ' + errors.join('\n- '); const lines = ['ACCEPTED.' + (warns.length ? ' Warnings:\n- ' + warns.join('\n- ') : '')];
  lines.push(`How a program reads it: citation ${repr(rule.citation)}; lifecycle ${rule.lifecycle}; effective_date ${pyStr(rule.effective_date)}; valid_through ${pyStr(rule.valid_through)}.`, 'Conditions it will test: ' + describeConditions(rule.applicability)); if (rule.relations.length) lines.push('Relations kept: ' + rule.relations.map((r: Data) => r.type).join(', '));
  if (rule.lifecycle === 'enacted') {lines.push(`What the conditions do to made-up buildings on ${AS_OF} (year built, units):`); for (const [year, units, lower] of PROBES) {const got = outcome(rule, {year_built: year, units, units_at_least: lower}, AS_OF); lines.push(`  built ${year || 'unknown year'}, ${units ?? 'unknown'} units -> ${WORDS[got] || got}`);}} return lines.join('\n');
}
export function makePost(config: ApiConfig): Post {const client = new ChatClient(config); return (messages, specs) => client.post(messages, specs);}
export async function converse(post: Post, system: string, user: string, cards: Record<string, string>, validator: Validator, tools = ['cards', 'check']): Promise<[string, Data]> {
  const specs = toolSpecs(tools), messages: Data[] = [{role: 'system', content: system}, {role: 'user', content: user}], log: Data = {steps: 0, cards_read: [], checks: 0, usage: []};
  while (true) {
    const body = await post(messages, specs); log.steps++; log.usage.push(body.usage || {}); const c = body?.choices?.[0]; if (!isObject(c?.message) || !Object.hasOwn(c, 'finish_reason')) throw new ApiError('API 返回内容缺少 choices/message/content 或 finish_reason。'); const message: Data = Object.fromEntries(Object.entries(c.message).filter(([, v]) => v != null)), reason = c.finish_reason; messages.push(message);
    if (!message.tool_calls?.length) {if (reason !== 'stop') throw new ApiError(`回答未正常结束（${pyStr(reason)}）。`); log.messages = messages.slice(2); return [message.content || '', log];}
    for (const call of message.tool_calls) {const name = call.function.name; let arg: Data; try {arg = JSON.parse(call.function.arguments || '{}');} catch {arg = {};}
      let result: string; if (name === 'read_card') {log.cards_read.push(arg.name ?? null); result = (Object.hasOwn(cards, arg.name) ? cards[arg.name] : null) || 'No such card. Cards: ' + Object.keys(cards).sort().join(', ');} else if (name === 'check_record') {log.checks++; result = checkRecord(validator, arg.record_json ?? '');} else result = 'Unknown tool.'; messages.push({role: 'tool', tool_call_id: call.id, content: result});
    }
  }
}
export const checkFinal = (text: string, pid: string): void => validateFinal(text, pid);
export interface AgentOptions extends RunOptions {workers?: number; post?: Post;}
export async function runAgentApi(paths: Paths, config: ApiConfig | null, opts: AgentOptions = {}): Promise<number> {
  const emit = opts.emit ?? console.log, workers = opts.workers ?? 1, index = loadIndex(paths), system = renderCore(index.as_of); let res = runIngest(paths, undefined, !opts.dry_run), todo = select(pendingPackets(res), index, opts.only); const packets = readPackets(paths, index, todo);
  emit(`分步模式 | 模型：${config?.model ?? '-'} | 待处理：${Object.keys(todo).length} 个分包 | 已完成：${res.counts.packets_done}/${res.counts.packets_total} | 并行：${workers}`);
  if (opts.dry_run) {for (const pid of Object.keys(todo)) emit('  ' + pid + (todo[pid].length ? '（需修正）' : '')); emit('预览完成，未调用 API。'); return 0;}
  if (!Object.keys(todo).length) {writeOutputs(paths, res, opts.rules_format); emit('所选范围没有待处理分包。结果：' + path.join(paths.out_dir, 'rules.json')); return 0;}
  if (!opts.post && !config?.key) throw new ApiError('尚未配置 API 密钥。'); const post = opts.post ?? makePost(config!), validator = new Validator(loadCorpus(paths), index, loadSchema(paths), index.as_of), cards = loadCards(), archive = path.join(paths.work_dir, 'api'), errors: string[] = [];
  fs.mkdirSync(archive, {recursive: true}); fs.mkdirSync(paths.inbox_dir, {recursive: true});
  while (Object.keys(todo).length) {
    await pool(Object.entries(todo), Math.max(1, workers), async ([pid, problems]) => {try {
      const [text, log] = await converse(post, system, renderPacketInput(pid, packets[pid], problems), cards, validator), attempt = attemptName('AGENT', pid); writeJson(path.join(archive, attempt + '.json'), {packet_id: pid, model: config?.model ?? null, as_of: index.as_of, prompt_sha256: sha256(system), steps: log.steps, cards_read: log.cards_read, checks: log.checks, usage: log.usage, messages: log.messages}, false); writeText(path.join(archive, attempt + '.txt'), text); checkFinal(text, pid);
      // There is no await between saving the answer and the completed ingest:
      // concurrent requests cannot interleave these synchronous file mutations.
      writeText(path.join(paths.inbox_dir, attempt + '.jsonl'), text); res = runIngest(paths); writeOutputs(paths, res, opts.rules_format); const s = res.states[pid]; emit(`  ${pid}：${s.state}（${s.detail}）；${log.steps} 步，读了 ${log.cards_read.length ? repr(log.cards_read) : '-'}，自检 ${log.checks} 次。`);
    } catch (error) {if (!(error instanceof ApiError) && !(error instanceof Error && 'code' in error)) throw error; const msg = (error as Error).message; errors.push(pid + '：' + msg); emit(`  ${pid}：失败：${msg}`);}});
    todo = select(pendingPackets(res), index, opts.only); if (opts.once || errors.length) break;
  }
  emit(`已完成：${res.counts.packets_done}/${res.counts.packets_total} | 规则：${res.counts.rules} | 所选范围剩余：${Object.keys(todo).length}\n结果：${path.join(paths.out_dir, 'rules.json')}\n检查报告：${path.join(paths.work_dir, 'report.md')}`); if (errors.length) {emit(`有 ${errors.length} 个分包没有完成（API 或回答格式问题），已保存的进度仍在，重新运行会继续：\n  ${errors.join('\n  ')}`); return 1;} return Object.keys(todo).length ? 2 : 0;
}
