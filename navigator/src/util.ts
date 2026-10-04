import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import type {Data} from './types.js';

export const clone = <T>(value: T): T => structuredClone(value);
export const length = (s: string): number => Array.from(s).length;
export const slice = (s: string, a = 0, b?: number): string => Array.from(s).slice(a, b).join('');
export const cmp = (a: any, b: any): number => {
  if (Array.isArray(a) && Array.isArray(b)) {
    for (let i = 0; i < Math.min(a.length, b.length); i++) {const n = cmp(a[i], b[i]); if (n) return n;}
    return a.length - b.length;
  }
  return a < b ? -1 : a > b ? 1 : 0;
};
export const sortedEntries = <T>(obj: Record<string, T>): [string, T][] => Object.entries(obj).sort(([a], [b]) => cmp(a, b));
export const unique = <T>(items: T[]): T[] => Array.from(new Set(items));
export function stable(value: any): any {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === 'object') return Object.fromEntries(sortedEntries(value).map(([k, v]) => [k, stable(v)]));
  return value;
}
export const equal = (a: any, b: any): boolean => JSON.stringify(stable(a)) === JSON.stringify(stable(b));
export function jsonProblem(text: string, error: Error): string {
  const m = /at position (\d+)/.exec(error.message); let offset = m ? +m[1] : text.length, why = 'Expecting value';
  if (/property name|double-quoted property/.test(error.message) || /^\s*\{\s*$/.test(text)) why = 'Expecting property name enclosed in double quotes';
  else if (/Expected ':'/.test(error.message)) why = "Expecting ':' delimiter";
  else if (/Expected ','/.test(error.message)) why = "Expecting ',' delimiter";
  else if (/after JSON/.test(error.message)) why = 'Extra data';
  else if (/Unterminated string/.test(error.message)) {why = 'Unterminated string starting at'; offset = text.lastIndexOf('"');}
  else if (!m && !/end of JSON/.test(error.message)) offset = Math.max(0, text.search(/\S/));
  const prefix = text.slice(0, offset), lines = prefix.split('\n'), chars = length(prefix);
  return `${why}: line ${lines.length} column ${length(lines.at(-1)!) + 1} (char ${chars})`;
}
export const isObject = (v: unknown): v is Data => v !== null && typeof v === 'object' && !Array.isArray(v);
export const readJson = (p: string): any => JSON.parse(fs.readFileSync(p, 'utf8'));
// JSON keys are ordinary data, including names such as __proto__. Assignment
// must not invoke Object.prototype setters or read inherited properties.
export function setKey<T>(target: Record<string, T>, key: string, value: T): void {Object.defineProperty(target, key, {value, enumerable: true, configurable: true, writable: true});}
export const sha256 = (data: string | Buffer): string => createHash('sha256').update(data).digest('hex');
export const hashFile = (p: string): string => sha256(fs.readFileSync(p));
export function writeText(p: string, text: string | Buffer): void {
  fs.mkdirSync(path.dirname(p), {recursive: true});
  fs.writeFileSync(p, text);
}
export function writeJson(p: string, value: any, sort = true, indent = 2): void {
  fs.mkdirSync(path.dirname(p), {recursive: true});
  fs.writeFileSync(p + '.tmp', JSON.stringify(sort ? stable(value) : value, null, indent) + '\n');
  fs.renameSync(p + '.tmp', p);
}
export function walk(p: string): string[] {
  if (!fs.existsSync(p)) return [];
  return fs.readdirSync(p, {withFileTypes: true}).flatMap(e => e.isDirectory() ? walk(path.join(p, e.name)) : e.isFile() ? [path.join(p, e.name)] : []);
}
export function counter(items: any[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const item of items) {const key = pyStr(item); setKey(out, key, (Object.hasOwn(out, key) ? out[key] : 0) + 1);}
  return out;
}
// Explanations and validation messages are part of the established interface.
export function repr(v: any): string {
  if (v === null || v === undefined) return 'None';
  if (typeof v === 'boolean') return v ? 'True' : 'False';
  if (typeof v === 'string') {
    const quote = v.includes("'") && !v.includes('"') ? '"' : "'";
    const escaped = v.replaceAll('\\', '\\\\').replaceAll('\n', '\\n').replaceAll('\r', '\\r').replaceAll('\t', '\\t').replaceAll(quote, '\\' + quote);
    return quote + escaped + quote;
  }
  if (Array.isArray(v)) return '[' + v.map(repr).join(', ') + ']';
  if (isObject(v)) return '{' + Object.entries(v).map(([k, x]) => repr(k) + ': ' + repr(x)).join(', ') + '}';
  return String(v);
}
export const pyStr = (v: any): string => typeof v === 'string' ? v : repr(v);
export const truth = (v: any): boolean => Array.isArray(v) ? v.length > 0 : isObject(v) ? Object.keys(v).length > 0 : Boolean(v);
export const escapeRegex = (s: string): string => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
export function parseCsv(text: string): string[][] {
  const rows: string[][] = []; let row: string[] = [], field = '', quoted = false;
  text = text.replace(/^\uFEFF/, '');
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"' && quoted && text[i + 1] === '"') {field += '"'; i++;}
    else if (c === '"' && (quoted || !field)) quoted = !quoted;
    else if (c === ',' && !quoted) {row.push(field); field = '';}
    else if ((c === '\n' || c === '\r') && !quoted) {
      if (c === '\r' && text[i + 1] === '\n') i++;
      if (row.length || field) {row.push(field); rows.push(row);}
      row = []; field = '';
    } else field += c;
  }
  if (row.length || field) {row.push(field); rows.push(row);}
  return rows;
}
export function csvRecords(text: string): Data[] {
  const [headers, ...rows] = parseCsv(text);
  return headers ? rows.map(row => Object.fromEntries(headers.map((h, i) => [h, row[i] ?? '']))) : [];
}
export const csvRow = (items: any[]): string => items.map(x => /[",\r\n]/.test(String(x)) ? '"' + String(x).replaceAll('"', '""') + '"' : String(x)).join(',');
export function isoDate(y: number, m: number, d: number): string {
  if (y < 1 || y > 9999) throw new Error(`year must be in 1..9999, not ${y}`);
  if (m < 1 || m > 12) throw new Error(`month must be in 1..12, not ${m}`);
  const last = monthDays(y, m);
  if (d < 1 || d > last) throw new Error(`day ${d} must be in range 1..${last} for month ${m} in year ${y}`);
  return `${String(y).padStart(4, '0')}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
}
export const monthDays = (y: number, m: number): number => m === 2 ? (y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0) ? 29 : 28) : [4, 6, 9, 11].includes(m) ? 30 : 31;
export const addDays = (iso: string, days: number): string => new Date(new Date(iso + 'T00:00:00Z').getTime() + days * 86400000).toISOString().slice(0, 10);
export function yearsBefore(day: string, years: number): string {
  const [y, m, d] = day.split('-').map(Number);
  return isoDate(y - years, m, Math.min(d, monthDays(y - years, m)));
}
export async function pool<T, R>(items: T[], workers: number, fn: (x: T) => Promise<R>): Promise<R[]> {
  if (!Number.isInteger(workers) || workers < 1) throw new Error('workers must be a positive integer');
  const results: R[] = new Array(items.length); let next = 0;
  await Promise.all(Array.from({length: Math.min(workers, items.length)}, async () => {
    while (next < items.length) {const i = next++; results[i] = await fn(items[i]);}
  }));
  return results;
}
