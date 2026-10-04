import type {Data} from '../types.js';
import {equal, isObject, length, pyStr, repr, slice, stable, unique} from '../util.js';
import {canon, dateStart, normalizeDate} from './facts.js';
export const CONTRACT_VERSION = 2;
export const DATE_KEYS = ['built_on_or_before', 'built_before', 'built_after', 'built_on_or_after'];
export const APPL_KEYS = [...DATE_KEYS, 'date_basis', 'min_units', 'max_units', 'exempt_if_newer_than_years', 'covered_if_newer_than_years', 'owner_dependent', 'owner_exempt_if_units_at_most', 'other', 'program_notes', 'per_tenancy', 'coverage_quotes', 'deferred', 'alternatives', 'contract'];
export const DATE_BASES = new Set(['certificate_of_occupancy', 'construction_date', 'unspecified']);
export const MAX_QUOTES = 4;
const BASIS: Record<string, string> = {certificate_of_occupancy: 'certificate_of_occupancy', construction: 'construction_date', construction_date: 'construction_date', unspecified: 'unspecified'};
const COVERED: Record<string, string> = {on_or_before: 'built_on_or_before', before: 'built_before', after: 'built_after', on_or_after: 'built_on_or_after'};
const EXEMPT: Record<string, string> = {after: 'built_on_or_before', on_or_after: 'built_before', before: 'built_on_or_after', on_or_before: 'built_after'};
const getBasis = (v: any): string | null => {const k = (text(v) || '').toLowerCase(); return Object.hasOwn(BASIS, k) ? BASIS[k] : null;};
const PROGRAM_NOTE = /affordab|subsid|deed|restrict|low.income|moderate.income|very low|public housing|housing authority|government|HUD\b|section ?8|\b202\b|\b811\b|nonprofit|non-profit|transitional|institution|hospital|care facility|religious|dormitor|student|hotel|motel|mobile ?home|condominium|single.family|alienable|rent control|rent stabilization|rent regulat|cooperative/i;
const NULLISH = new Set(['', 'null', 'none', 'n/a', 'na', 'unknown', 'not stated', 'not specified', 'not applicable', '-']);
export type Locate = (quote: string) => string | null;
export function empty(): Data {return {...Object.fromEntries(APPL_KEYS.map(k => [k, null])), owner_dependent: false, coverage_quotes: [], deferred: [], alternatives: [], program_notes: []};}
function text(v: any): string | null {return typeof v === 'string' && !NULLISH.has(v.trim().toLowerCase()) ? v.trim() : null;}
function integer(v: any): number | null {
  if (typeof v === 'number' && Number.isInteger(v) && v >= 0) return v;
  return typeof v === 'string' && /^\s*\d+\s*$/.test(v) ? Number(v) : null;
}
const bool = (v: any): boolean => typeof v === 'boolean' ? v : typeof v === 'string' && v.trim().toLowerCase() === 'true';
function stricter(key: string, old: string | null, next: string): string {return old === null ? next : (dateStart(old) <= dateStart(next)) === ['built_on_or_before', 'built_before'].includes(key) ? old : next;}
function applyFlats(out: Data, flats: Data): void {
  for (const [k, v] of Object.entries(flats)) {
    if (DATE_KEYS.includes(k)) out[k] = stricter(k, out[k], v);
    else if (['min_units', 'exempt_if_newer_than_years'].includes(k)) out[k] = out[k] == null ? v : Math.max(out[k], v);
    else if (['max_units', 'covered_if_newer_than_years'].includes(k)) out[k] = out[k] == null ? v : Math.min(out[k], v);
  }
}
function window(item: Data): Set<string> {return new Set((item.flats_all || [item.flats || {}]).map((m: Data) => JSON.stringify(stable(Object.fromEntries(Object.entries(m).filter(([k]) => k !== 'date_basis'))))));}
const subset = (a: Set<string>, b: Set<string>): boolean => Array.from(a).every(x => b.has(x));
export function addDeferred(items: Data[], next: Data): void {
  const mine = window(next);
  for (let i = 0; i < items.length; i++) {
    const theirs = window(items[i]); if (equal(Array.from(mine).sort(), Array.from(theirs).sort())) return;
    if (subset(theirs, mine)) {items[i] = next; return;} if (subset(mine, theirs)) return;
  }
  items.push(next);
}
function covered(c: Data, flats: Data, out: Data): void {
  const also = text(c.also);
  if (also === null) {applyFlats(out, flats); return;}
  const item = {flats: {...flats}, also: slice(also, 0, 200)};
  if (!out.alternatives.some((x: Data) => equal(x, item))) out.alternatives.push(item);
}
function finishExempt(out: Data, members: Data[], conditional: boolean, note: string, b: string | null, basis: string[]): void {
  if (members.length === 1 && !conditional) {applyFlats(out, members[0]); if (b) basis.push(b); return;}
  const addBasis = (m: Data): Data => ({...m, ...(b ? {date_basis: b} : {})});
  const item = members.length === 1 ? {flats: addBasis(members[0]), note, conditional: true} : {flats_all: members.map(addBasis), note, conditional};
  addDeferred(out.deferred, item);
}
function exempt(c: Data, flats: Data, note: string, b: string | null, out: Data, groups: Data, basis: string[]): void {
  const gid = text(c.group), conditional = c.conditional === true;
  if (gid) {const g = groups[gid] ??= {members: [], conditional: false, notes: [], basis: []}; g.members.push({...flats}); g.conditional ||= conditional; g.notes.push(note); if (b) g.basis.push(b); return;}
  finishExempt(out, [{...flats}], conditional, note, b, basis);
}
function condition(c: any, out: Data, unresolved: string[], basis: string[], warns: string[], dates: Set<string> | null, nums: Set<string> | null, groups: Data): void {
  if (!isObject(c)) {warns.push(`applicability condition ${repr(c)} is not an object: ignored`); return;}
  const kind = text(c.type), role = (text(c.role) || '').toLowerCase();
  const label = pyStr(kind) + ' ' + repr(Object.fromEntries(Object.entries(c).filter(([k]) => k !== 'type')));
  const doubt = (why: string): void => {warns.push(`applicability condition ignored (${why}): ${slice(label, 0, 160)}`); unresolved.push(`a coverage condition the model reported could not be matched to the source (${slice(label, 0, 120)})`);};
  const numSupported = (n: number): boolean => !nums || [n, n - 1, n + 1].some(x => x >= 0 && nums.has(canon(x)));
  if (kind === 'built') {
    const op = (text(c.op) || '').toLowerCase(), date = typeof c.date === 'string' ? normalizeDate(c.date) : null;
    if (!['covered', 'exempt'].includes(role) || !Object.hasOwn(COVERED, op) || date === null) return doubt('needs role covered/exempt, an op and a date');
    if (dates && !dates.has(date)) return doubt(`date ${date} is not in the source`);
    const key = (role === 'covered' ? COVERED : EXEMPT)[op], b = getBasis(c.basis);
    if (role === 'exempt') return exempt(c, {[key]: date}, `built ${op.replaceAll('_', ' ')} ${date}`, b, out, groups, basis);
    covered(c, {[key]: date, ...(b ? {date_basis: b} : {})}, out); if (b) basis.push(b);
  } else if (kind === 'built_within_years') {
    const years = integer(c.years);
    if (!['covered', 'exempt'].includes(role) || years === null) return doubt('needs role covered/exempt and a whole number of years');
    if (!numSupported(years)) return doubt(`${years} years is not in the source`);
    const b = getBasis(c.basis);
    if (role === 'covered') {applyFlats(out, {covered_if_newer_than_years: years}); if (b) basis.push(b); return;}
    exempt(c, {exempt_if_newer_than_years: years}, `built within the last ${years} years`, b, out, groups, basis);
  } else if (kind === 'units') {
    const op = (text(c.op) || '').toLowerCase(), n = integer(c.n);
    if (!['covered', 'exempt'].includes(role) || !['at_least', 'more_than', 'at_most', 'fewer_than'].includes(op) || n === null) return doubt('needs role covered/exempt, an op and a whole number');
    if (!numSupported(n)) return doubt(`${n} units is not in the source`);
    const coveredValues: Record<string, [number | null, number | null]> = {at_least: [n, null], more_than: [n + 1, null], at_most: [null, n], fewer_than: [null, n - 1]};
    const exemptValues: Record<string, [number | null, number | null]> = {at_most: [n + 1, null], fewer_than: [n, null], at_least: [null, n - 1], more_than: [null, n]};
    const [lo, hi] = (role === 'covered' ? coveredValues : exemptValues)[op], flats = lo !== null ? {min_units: lo} : {max_units: hi};
    if (role === 'exempt') return exempt(c, flats, `${op.replaceAll('_', ' ')} ${n} units`, null, out, groups, basis);
    covered(c, flats, out);
  } else if (kind === 'owner') {
    const who = text(c.who), limit = c.unit_limit != null ? integer(c.unit_limit) : null;
    if (!['covered', 'exempt'].includes(role) || who === null) return doubt('needs role covered/exempt and who');
    if (limit !== null && !numSupported(limit)) return doubt(`${limit} units is not in the source`);
    if (role === 'exempt' && limit === null && /single.family|condominium|alienable|mobile ?home|government|public(?:ly)?[- ]owned|public housing|housing authority|(?:city|county|state|municipal)[- ]owned/i.test(who)) {out.program_notes.push(who); return;}
    out.owner_dependent = true;
    if (role === 'exempt') {if (limit === null) out._owner_unbounded = true; else if (out.owner_exempt_if_units_at_most == null || limit > out.owner_exempt_if_units_at_most) out.owner_exempt_if_units_at_most = limit;}
    else if (limit !== null) applyFlats(out, {max_units: limit});
  } else if (kind === 'other') {
    const t = text(c.text); if (t) (role !== 'covered' && PROGRAM_NOTE.test(t) ? out.program_notes : unresolved).push(t);
  } else warns.push('applicability condition of unknown type ignored: ' + slice(label, 0, 120));
}
export function parse(a: any, warns: string[], dates: Set<string> | null = null, nums: Set<string> | null = null, locate: Locate | null = null): Data {
  const out = empty(); if (a == null) return out;
  if (!isObject(a)) {warns.push('applicability is not an object: ignored'); return out;}
  const unresolved: string[] = [], basis: string[] = [], groups: Data = Object.create(null); let conds = a.conditions;
  if ('conditions' in a) out.contract = CONTRACT_VERSION;
  if (conds != null && !Array.isArray(conds)) {warns.push('applicability.conditions is not a list: ignored'); conds = null;}
  for (const c of conds || []) condition(c, out, unresolved, basis, warns, dates, nums, groups);
  for (const g of Object.values(groups)) finishExempt(out, g.members, g.conditional, g.notes.join(' and '), g.basis[0] ?? null, basis);
  for (const k of DATE_KEYS) {
    const v = text(a[k]); if (v !== null && out[k] === null) {const nd = normalizeDate(v); if (nd === null) warns.push(`applicability.${k} ${repr(v)} is not a date: ignored`); else out[k] = nd;}
  }
  for (const k of ['min_units', 'max_units', 'exempt_if_newer_than_years', 'owner_exempt_if_units_at_most']) {
    const v = integer(typeof a[k] === 'string' ? text(a[k]) : a[k]);
    if (a[k] != null && v === null) warns.push(`applicability.${k} ${repr(a[k])} is not an integer: ignored`);
    if (v !== null && out[k] === null) out[k] = v;
  }
  if (bool(a.owner_dependent)) out.owner_dependent = true;
  const legacyBasis = text(a.date_basis), chosen = basis.filter(b => b !== 'unspecified');
  out.date_basis = (chosen.length ? chosen : basis)[0] ?? (legacyBasis && DATE_BASES.has(legacyBasis) ? legacyBasis : null);
  const legacyOther = text(a.other); if (legacyOther) unresolved.push(legacyOther);
  out.other = unique(unresolved).join('; ') || null; out.program_notes = unique(out.program_notes); out.per_tenancy = text(a.per_tenancy);
  let quotes = a.coverage_quotes;
  if (quotes != null && !Array.isArray(quotes)) {warns.push('applicability.coverage_quotes is not a list: ignored'); quotes = [];}
  const kept: string[] = [];
  for (const raw of (quotes || []).slice(0, MAX_QUOTES)) {
    let q = text(raw); if (q === null || q.includes('[[omitted')) continue;
    if (locate) {q = locate(q); if (q === null) {warns.push('applicability.coverage_quotes: a passage is not in the source and was dropped'); continue;}}
    if (length(q) >= 15 && length(q) <= 600 && !kept.includes(q)) kept.push(q);
  }
  out.coverage_quotes = kept; if (out._owner_unbounded) out.owner_exempt_if_units_at_most = null; delete out._owner_unbounded;
  return out;
}
export function parseRelations(raw: any, warns: string[], locate: Locate | null = null): Data[] {
  const out: Data[] = []; if (raw == null) return out;
  if (!Array.isArray(raw)) {warns.push('relations is not a list: ignored'); return out;}
  for (const r of raw) {
    const kind = isObject(r) ? text(r.type) : null; let quote = isObject(r) ? text(r.quote) : null;
    if (!['preempts_local', 'yields_to_local'].includes(kind ?? '') || quote === null) {warns.push('a relation without a known type or quote was dropped'); continue;}
    if (locate) {quote = locate(quote); if (quote === null) {warns.push(`a ${kind} relation whose quote is not in the source was dropped`); continue;}}
    if (length(quote) >= 15 && !out.some(x => x.type === kind && x.quote === quote)) out.push({type: kind, quote});
  }
  return out;
}
export function merge(primary: Data, other: Data, docId: string, notes: string[], warns: string[]): void {
  const a = primary.applicability, b = other.applicability;
  for (const k of [...DATE_KEYS, 'min_units', 'max_units', 'exempt_if_newer_than_years', 'covered_if_newer_than_years', 'owner_exempt_if_units_at_most', 'date_basis']) {
    if (a[k] == null && b[k] != null) {a[k] = b[k]; notes.push(`applicability.${k} taken from ${docId}`);}
    else if (b[k] != null && a[k] !== b[k]) warns.push(`applicability.${k} differs between sources: ${primary.source_doc_id} says ${pyStr(a[k])}, ${docId} says ${pyStr(b[k])}`);
  }
  if (b.owner_dependent && !a.owner_dependent) {a.owner_dependent = true; notes.push('owner_dependent taken from ' + docId);}
  for (const k of ['other', 'per_tenancy']) if (b[k] && !(a[k] || '').includes(b[k])) a[k] = [a[k], b[k]].filter(Boolean).join('; ');
  for (const q of b.coverage_quotes || []) if (!a.coverage_quotes.includes(q) && a.coverage_quotes.length < MAX_QUOTES) a.coverage_quotes.push(q);
  for (const item of b.deferred || []) addDeferred(a.deferred, item);
  for (const item of b.alternatives || []) {a.alternatives ??= []; if (!a.alternatives.some((x: Data) => equal(x, item))) a.alternatives.push(item);}
  for (const t of b.program_notes || []) if (!a.program_notes.includes(t)) a.program_notes.push(t);
  if (a.contract == null) a.contract = b.contract ?? null;
  if (primary.valid_through == null && other.valid_through != null) {primary.valid_through = other.valid_through; notes.push('valid_through filled in from ' + docId);}
  primary.relations ??= []; for (const r of other.relations || []) if (!primary.relations.some((x: Data) => equal(x, r))) primary.relations.push(r);
}
