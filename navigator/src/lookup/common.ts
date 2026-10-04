import type {Data} from '../types.js';
import {isoDate, repr} from '../util.js';
import {ROOT, findDataDir, FALLBACK_CATEGORIES} from '../nav/config.js';
export {ROOT};
export {readJson, writeJson, hashFile as sha256} from '../util.js';
export const pack = (): string => findDataDir();
export const DEFAULT_DATE = '2026-10-01';
export const DISCLAIMER = 'Not legal advice. Based only on the cited sources and the listed address facts.';
export const CATEGORIES = new Set(FALLBACK_CATEGORIES);
export function queryDate(value: unknown): string {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error('查询日期必须是 YYYY-MM-DD');
  return isoDate(...value.split('-').map(Number) as [number, number, number]);
}
export function dateInterval(value: unknown): [string, string] {
  if (typeof value !== 'string' || !/^\d{4}(?:-\d{2}(?:-\d{2})?)?$/.test(value)) throw new Error('规则日期格式错误: ' + repr(value));
  const [y, m, d] = value.split('-').map(Number);
  if (d !== undefined) {const day = isoDate(y, m, d); return [day, day];}
  if (m !== undefined) {const first = isoDate(y, m, 1); const next = new Date(first + 'T00:00:00Z'); next.setUTCMonth(next.getUTCMonth() + 1); next.setUTCDate(0); return [first, next.toISOString().slice(0, 10)];}
  return [isoDate(y, 1, 1), isoDate(y, 12, 31)];
}
export function matches(rule: Data, selector: Data): boolean {
  for (const [key, expected] of Object.entries(selector)) {
    if (key.endsWith('_contains')) {if (!String(rule[key.slice(0, -9)] || '').toLowerCase().includes(String(expected).toLowerCase())) return false;}
    else if (key === 'citation_regex') {if (!new RegExp(expected, 'i').test(rule.citation ?? '')) return false;}
    else if (rule[key] !== expected) return false;
  }
  return true;
}
