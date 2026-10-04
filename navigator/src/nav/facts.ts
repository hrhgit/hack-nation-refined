import {addDays, isoDate, pyStr, unique} from '../util.js';
import * as P from './fact-patterns.js';
export const ISO_ANY = P.ISO_ANY;
const all = (rx: RegExp, s: string): RegExpExecArray[] => Array.from(s.matchAll(new RegExp(rx.source, rx.flags + 'g')));
function iso(y: number, m: number, d: number): string | null {try {return isoDate(y, m, d);} catch {return null;}}
const mon = (name: string): number => P.MONTHS[name.toLowerCase().replace(/\.$/, '')];
export function normalizeDate(raw: unknown): string | null {
  if (raw == null) return null;
  const s = pyStr(raw).trim();
  if (P.ISO_ANY.test(s)) return P.ISO_FULL.test(s) && !iso(Number(s.slice(0, 4)), Number(s.slice(5, 7)), Number(s.slice(8, 10))) ? null : s;
  let m = P.RX_MDY.exec(s); if (m) return iso(+m[3], mon(m[1]), +m[2]);
  m = P.RX_DMY.exec(s); if (m) return iso(+m[3], mon(m[2]), +m[1]);
  m = P.RX_SLASH.exec(s); if (m && m[0] === s) return iso(+m[3] < 100 ? +m[3] + 2000 : +m[3], +m[1], +m[2]);
  m = P.RX_MY.exec(s); return m && m[0] === s ? `${m[2].padStart(4, '0')}-${String(mon(m[1])).padStart(2, '0')}` : null;
}
export function dateStart(s: string): string {const [y, m = 1, d = 1] = s.split('-').map(Number); return isoDate(y, m, d);}
export function docDates(text: string): Set<string> {
  const out = new Set<string>(); const add = (x: string | null): void => {if (x) {out.add(x); out.add(x.slice(0, 7)); out.add(x.slice(0, 4));}};
  for (const m of all(P.RX_MDY, text)) add(iso(+m[3], mon(m[1]), +m[2]));
  for (const m of all(P.RX_DMY, text)) add(iso(+m[3], mon(m[2]), +m[1]));
  for (const m of all(P.RX_SLASH, text)) add(iso(+m[3] < 100 ? +m[3] + 2000 : +m[3], +m[1], +m[2]));
  for (const m of all(P.RX_ISO, text)) add(iso(+m[1], +m[2], +m[3]));
  for (const m of all(P.RX_HYPHEN, text)) add(iso(+m[3], +m[1], +m[2]));
  for (const m of all(P.RX_MY, text)) {const ym = `${m[2].padStart(4, '0')}-${String(mon(m[1])).padStart(2, '0')}`; out.add(ym); out.add(ym.slice(0, 4));}
  for (const m of all(P.RX_YEAR, text)) out.add(m[1]);
  return out;
}
export const dateSupported = (eff: string, dates: Set<string>): boolean => dates.has(eff);
export function deriveStatus(lifecycle: string, effective: string | null, asOf: string): string {
  if (lifecycle === 'pending_bill') return 'pending';
  if (lifecycle === 'failed') return 'failed';
  return effective && dateStart(effective) > dateStart(asOf) ? 'not_yet_effective' : 'in_force';
}
export function canon(n: number): string {
  if (!Number.isFinite(n)) return String(n).toLowerCase();
  if (n === 0) return Object.is(n, -0) ? '-0' : '0';
  const rounded = Number(n.toPrecision(6)), exponent = Math.floor(Math.log10(Math.abs(rounded)));
  if (exponent < -4 || exponent >= 6) {
    const [coefficient, e] = rounded.toExponential(5).split('e');
    return coefficient.replace(/\.?0+$/, '') + 'e' + (Number(e) >= 0 ? '+' : '-') + String(Math.abs(Number(e))).padStart(2, '0');
  }
  return String(rounded);
}
export const unspaceNumbers = (text: string): string => text.replace(/(?<=\d)\s*,\s*(?=\d{3}\b)/g, ',').replace(/\$\s+(?=\d)/g, '$').replace(/\(\s+(?=\d)|(?<=\d)\s+\)/g, m => m.startsWith('(') ? '(' : ')');
export function numbersIn(text: string): Set<string> {
  text = unspaceNumbers(text); const out = new Set<string>();
  for (const m of all(P.RX_NUM, text)) {const n = Number(m[0].replaceAll(',', '')); if (!Number.isNaN(n)) out.add(canon(n));}
  const low = text.toLowerCase();
  for (const m of low.matchAll(/\b(\w+) and (?:one[- ]half|a half)\b/gi)) if (Object.hasOwn(P.WORDS, m[1])) out.add(canon(P.WORDS[m[1]] + .5));
  for (const _ of low.matchAll(/\bone[- ]half\b|\ba half\b/gi)) out.add('0.5');
  for (const m of low.matchAll(/[a-z]+/g)) if (Object.hasOwn(P.WORDS, m[0])) out.add(canon(P.WORDS[m[0]]));
  return out;
}
export const numericSignature = (value: string | null): Set<string> => numbersIn(value ?? '');
export function unsupportedNumbers(value: string, docNumbers: Set<string>): string[] {
  return unique(all(P.RX_NUM, value.replaceAll('%', ' ')).map(m => canon(Number(m[0].replaceAll(',', '')))).filter(t => !docNumbers.has(t))).sort();
}
export function normalizeCitation(c: string): string {
  let s = (c ?? '').replace(/\s+/g, ' ').trim().replace(/\b(?:Section|Sec\.)\s+(?=\d)/gi, '§').replace(/§\s+§/g, '§§').replace(/§§?\s+/g, m => m.trimEnd());
  s = s.replace(new RegExp(P.SUBD_WORDS.source, 'gi'), '').replace(new RegExp(P.SUBDIV.source, 'g'), '');
  return s.replace(/^[ ,;]+|[ ,;]+$/g, '');
}
export function splitCitation(c: string): [string, string | null] {
  const s = (c ?? '').replace(/\s+/g, ' ').trim(); let cut: [number, number] | null = null;
  const m = P.ASPECT_COLON.exec(s); if (m && m.index >= 4) cut = [m.index, m.index + m[0].length];
  for (const mm of s.matchAll(/,\s+/g)) {
    if (cut && mm.index >= cut[0]) break;
    const before = s.slice(0, mm.index), after = s.slice(mm.index + mm[0].length);
    if (!after || P.CITE_CONTINUES.test(after)) continue;
    if (/\d/.test(before) || /^[a-z]/.test(after)) {cut = [mm.index, mm.index + mm[0].length]; break;}
  }
  return cut ? [s.slice(0, cut[0]).replace(/^[ ,;]+|[ ,;]+$/g, ''), s.slice(cut[1]).trim()] : [s, null];
}
export function citationKey(c: string): string {
  const base = (c ?? '').replace(/\([^)]*\)/g, ' '), toks = unique(Array.from(base.matchAll(/[0-9][0-9A-Za-z.:\-]*/g), m => m[0].replace(/^[.:-]+|[.:-]+$/g, '').toLowerCase()).filter(Boolean)).sort();
  return toks.length ? toks.join('|') : (c ?? '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}
export const keyTokens = (key: string): Set<string> => new Set(key ? key.split('|') : []);
export function normalizeJurisdiction(raw: string, known: string[], names: Record<string, string>): string | null {
  const s = (raw ?? '').replace(/\s+/g, ' ').trim(); if (!s) return null;
  if (Object.hasOwn(names, s.toLowerCase())) return names[s.toLowerCase()];
  if (/^[A-Za-z]{2}$/.test(s)) return s.toUpperCase();
  const s2 = s.replace(/^(?:the )?city (?:and county )?of /i, '').replace(/\s*,\s*/g, ', ');
  let m: string[] | null = /^(.+), ([A-Za-z]{2})$/.exec(s2);
  if (!m) {const m2 = /^(.+), (California|New Jersey|Massachusetts)$/i.exec(s2); if (!m2) return null; m = [m2[0], m2[1], names[m2[2].toLowerCase()]];}
  const normalized = `${m[1].trim()}, ${m[2].toUpperCase()}`;
  return known.find(k => k.toLowerCase() === normalized.toLowerCase()) ?? normalized;
}
export const levelOf = (j: string): 'state' | 'city' => /^[A-Z]{2}$/.test(j) ? 'state' : 'city';
export const stateOf = (j: string): string => j ? j.slice(-2).toUpperCase() : '';
function count(word: string): number | null {
  let w = word.trim().toLowerCase(); const m = /^(\d{1,3})(?:st|nd|rd|th)?$/.exec(w); if (m) return +m[1];
  if (Object.hasOwn(P.ORDINALS, w)) return P.ORDINALS[w]; w = w.replaceAll(' ', '-'); if (Object.hasOwn(P.ORDINALS, w)) return P.ORDINALS[w];
  const parts = w.split('-');
  if (parts.length === 1 && Object.hasOwn(P.WORDS, w)) return P.WORDS[w];
  return parts.length === 2 && parts.every(p => Object.hasOwn(P.WORDS, p)) && P.WORDS[parts[0]] >= 20 ? P.WORDS[parts[0]] + P.WORDS[parts[1]] : null;
}
export function addMonthsFirstDay(iso: string, n: number): string {const idx = +iso.slice(0, 4) * 12 + +iso.slice(5, 7) - 1 + n; return `${String(Math.floor(idx / 12)).padStart(4, '0')}-${String(idx % 12 + 1).padStart(2, '0')}-01`;}
export interface ActDates {approved: string; effective: string; clause: string; method: string;}
export function actDates(text: string): ActDates | null {
  const clauses = [['nth_month', P.RX_NTH_MONTH], ['immediate', P.RX_IMMEDIATE], ['days_after', P.RX_DAYS_AFTER]] as [string, RegExp][];
  const found = clauses.flatMap(([kind, rx]) => all(rx, text).map(m => ({kind, m})));
  if (found.length !== 1) return null;
  const approved = unique([...all(P.RX_APPROVED, text).map(m => iso(+m[3], mon(m[1]), +m[2])), ...all(P.RX_ADOPTED_DAY_OF, text).map(m => iso(+m[3], mon(m[2]), +m[1]))].filter((x): x is string => x !== null)).sort();
  if (approved.length !== 1) return null;
  const {kind, m} = found[0], ap = approved[0]; let eff: string;
  if (kind === 'immediate') eff = ap;
  else {const n = m.groups?.d ? +m.groups.d : count(m.groups?.n ?? ''); if (n === null) return null; eff = kind === 'nth_month' ? addMonthsFirstDay(ap, n) : addDays(ap, n);}
  return {approved: ap, effective: eff, clause: m[0].replace(/\s+/g, ' '), method: kind};
}
