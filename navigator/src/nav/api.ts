import fs from 'node:fs';
import path from 'node:path';
import {randomUUID} from 'node:crypto';
import type {Data} from '../types.js';
import {HttpError, request} from '../http.js';
import {isObject, pyStr, sha256, writeJson, writeText} from '../util.js';
import {Paths, ROOT} from './config.js';
import {pendingPackets, runIngest, writeOutputs} from './ingest.js';
import {loadIndex, renderPacketInput, renderPrompt} from './packets.js';
import {classify, extractJsonObjects} from './parse.js';
export class ApiError extends Error {}
export class ApiConfig {
  constructor(public key: string, public model = 'deepseek-flash', public base_url = 'https://api.deepseek.com') {}
  get endpoint(): string {
    let u: URL; try {u = new URL(this.base_url);} catch {throw new ApiError('API 地址必须是无用户名、密码或查询参数的 https 地址。');}
    if (!u.hostname || u.username || u.password || u.search || u.hash || !['http:', 'https:'].includes(u.protocol)) throw new ApiError('API 地址必须是无用户名、密码或查询参数的 https 地址。');
    if (u.protocol === 'http:' && !['localhost', '127.0.0.1', '[::1]'].includes(u.hostname)) throw new ApiError('远程 API 地址必须使用 https；http 仅用于本地测试。');
    return this.base_url.replace(/\/+$/, '') + '/chat/completions';
  }
}
export function loadApiConfig(envFile?: string, model?: string, baseUrl?: string, requireKey = true): ApiConfig {
  const values: Record<string, string> = {}, file = envFile ?? path.join(ROOT, '.env');
  if (fs.existsSync(file)) {
    const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/); for (let i = 0; i < lines.length; i++) {const line = lines[i].trim(); if (!line || line.startsWith('#')) continue; const j = line.indexOf('='); if (j < 0) throw new ApiError(`配置文件第 ${i + 1} 行应为 KEY=value。`); let v = line.slice(j + 1).trim(); if (v.length >= 2 && v[0] === v.at(-1) && ['"', "'"].includes(v[0])) v = v.slice(1, -1); values[line.slice(0, j).trim()] = v;}
  } else if (envFile !== undefined) throw new ApiError('指定的配置文件不存在。');
  const get = (k: string, d = ''): string => (process.env[k] ?? values[k] ?? d).trim(), key = get('NAV_API_KEY') || get('DEEPSEEK_API_KEY');
  if (requireKey && (!key || key === 'your-deepseek-api-key')) throw new ApiError('尚未配置密钥。请在 navigator/.env 填入 DEEPSEEK_API_KEY，或设置同名环境变量。');
  const config = new ApiConfig(key, model || get('NAV_API_MODEL', 'deepseek-flash'), baseUrl || get('NAV_API_BASE_URL', 'https://api.deepseek.com')); if (!config.model.trim()) throw new ApiError('模型名不能为空。请设置 NAV_API_MODEL 或 --model。'); config.endpoint; return config;
}
export class ChatClient {
  constructor(public config: ApiConfig) {}
  async post(messages: Data[], specs?: Data[]): Promise<Data> {
    const payload: Data = {model: this.config.model, stream: false, messages}; if (specs?.length) payload.tools = specs; let raw: string;
    try {raw = await request(this.config.endpoint, JSON.stringify(payload), {'Content-Type': 'application/json', Authorization: 'Bearer ' + this.config.key});}
    catch (error) {if (error instanceof HttpError) {const hints: Record<number, string> = {401: '密钥无效，请检查配置。', 402: '账户余额不足。', 403: '账户没有调用权限。', 429: '服务当前限制请求，请稍后重新运行。'}; throw new ApiError(`API 请求失败（HTTP ${error.status}）。${hints[error.status] || '请检查 API 地址、模型名或服务状态。'} 已保存的进度可继续使用。`);} throw new ApiError('无法完成 API 连接。请检查网络和 API 地址，然后重新运行。');}
    let body: unknown; try {body = JSON.parse(raw);} catch {throw new ApiError('API 返回的内容不是有效 JSON，请检查服务。');} if (!isObject(body)) throw new ApiError('API 返回的内容应为 JSON 对象。'); return body;
  }
  complete(prompt: string, packet: string): Promise<Data> {return this.post([{role: 'system', content: prompt}, {role: 'user', content: packet}]);}
}
export function answer(body: Data): [string, any] {
  const c = body?.choices?.[0]; if (!isObject(c) || !isObject(c.message) || !Object.hasOwn(c.message, 'content') || !Object.hasOwn(c, 'finish_reason')) throw new ApiError('API 返回内容缺少 choices/message/content 或 finish_reason。');
  const text = c.message.content; if (typeof text !== 'string' || !text.trim()) throw new ApiError('模型没有返回可用的文字回答。'); return [text, c.finish_reason];
}
export function select(pending: Record<string, string[]>, index: Data, only?: string[]): Record<string, string[]> {
  if (!only?.length) return pending; const unknown = [...new Set(only.filter(x => !Object.hasOwn(index.packets, x) && !Object.hasOwn(index.docs, x)))].sort(); if (unknown.length) throw new ApiError('未知文档或分包编号：' + unknown.join(', ')); return Object.fromEntries(Object.entries(pending).filter(([p]) => only.includes(p) || only.includes(index.packets[p].doc_id)));
}
export function readPackets(paths: Paths, index: Data, todo: Data): Record<string, string> {
  const packets: Record<string, string> = {}; for (const pid of Object.keys(todo)) {const f = path.join(paths.packets_dir, pid + '.md'); if (!fs.existsSync(f)) throw new ApiError(`缺少分包 ${pid}，请先运行 prepare。`); const data = fs.readFileSync(f); if (sha256(data) !== index.packets[pid].sha256) throw new ApiError(`分包 ${pid} 与目录记录不一致，请先运行 prepare。`); packets[pid] = data.toString('utf8');} return packets;
}
export interface RunOptions {only?: string[]; once?: boolean; dry_run?: boolean; rules_format?: string; emit?: (s: string) => void; client?: {complete(prompt: string, packet: string): Promise<Data> | Data};}
export const attemptName = (prefix: string, pid: string): string => `${prefix}_${pid}_${new Date().toISOString().replace(/[-:.Z]/g, '')}_${randomUUID().replaceAll('-', '')}`;
export function validateFinal(text: string, pid: string, noRecordsMessage = `${pid} 的回答没有规则或收据。`): void {
  const [objects, problems] = extractJsonObjects(text); if (problems.length) throw new ApiError(`${pid} 的回答有无法解析或未写完的 JSON，已保留原始回答，未导入。`);
  const relevant = objects.filter(o => classify(o) !== 'other'); if (!relevant.length) throw new ApiError(noRecordsMessage);
  if (relevant.some(o => o.packet_id !== pid)) throw new ApiError(`${pid} 的回答包含其他分包编号，已保留原始回答，未导入。`);
  const receipts = relevant.filter(o => classify(o) === 'receipt'); if (receipts.length > 1 || receipts.some(o => typeof o.n_rules !== 'number' || !Number.isInteger(o.n_rules) || o.n_rules < 0)) throw new ApiError(`${pid} 的收据重复或条数不是非负整数，已保留原始回答，未导入。`);
}
export async function runApi(paths: Paths, config: ApiConfig, opts: RunOptions = {}): Promise<number> {
  const emit = opts.emit ?? console.log, index = loadIndex(paths), prompt = renderPrompt(index.as_of); let res = runIngest(paths, undefined, !opts.dry_run), todo = select(pendingPackets(res), index, opts.only); const packets = readPackets(paths, index, todo);
  emit(`模型：${config.model} | 待处理：${Object.keys(todo).length} 个分包 | 已完成：${res.counts.packets_done}/${res.counts.packets_total}`);
  if (opts.dry_run) {for (const pid of Object.keys(todo)) emit('  ' + pid + (todo[pid].length ? '（需修正）' : '')); emit('预览完成，未调用 API。'); return 0;}
  if (!Object.keys(todo).length) {writeOutputs(paths, res, opts.rules_format); emit('所选范围没有待处理分包。结果：' + path.join(paths.out_dir, 'rules.json')); return 0;}
  if (!config.key) throw new ApiError('尚未配置 API 密钥。'); const client = opts.client ?? new ChatClient(config), archive = path.join(paths.work_dir, 'api'); fs.mkdirSync(archive, {recursive: true}); fs.mkdirSync(paths.inbox_dir, {recursive: true});
  while (Object.keys(todo).length) {
    for (const [pid, problems] of Object.entries(todo)) {
      emit(`正在处理 ${pid}${problems.length ? '（修正上一份回答）' : ''}…`); const textIn = renderPacketInput(pid, packets[pid], problems), body = await client.complete(prompt, textIn), attempt = attemptName('API', pid), file = path.join(archive, attempt + '.json');
      writeJson(file, {packet_id: pid, model: config.model, endpoint: config.endpoint, as_of: index.as_of, prompt_sha256: sha256(prompt), input_sha256: sha256(textIn), response: body}, false); const [text, reason] = answer(body); writeText(path.join(archive, attempt + '.txt'), text);
      if (reason !== 'stop') throw new ApiError(`${pid} 的回答未正常结束（${pyStr(reason)}）。原始回答已存入 ${file}；未作为完成结果导入。`);
      validateFinal(text, pid, `${pid} 的回答没有规则或收据，原始内容已保存到 ${file}。`); writeText(path.join(paths.inbox_dir, attempt + '.jsonl'), text); res = runIngest(paths); writeOutputs(paths, res, opts.rules_format); const state = res.states[pid]; emit(`  ${pid}：${state.state}（${state.detail}）；回答已保存。`);
    }
    todo = select(pendingPackets(res), index, opts.only); if (opts.once) break;
  }
  emit(`已完成：${res.counts.packets_done}/${res.counts.packets_total} | 规则：${res.counts.rules} | 所选范围剩余：${Object.keys(todo).length}\n结果：${path.join(paths.out_dir, 'rules.json')}\n检查报告：${path.join(paths.work_dir, 'report.md')}`); return Object.keys(todo).length ? 2 : 0;
}
