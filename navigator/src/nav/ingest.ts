import fs from 'node:fs';
import path from 'node:path';
import type {Data} from '../types.js';
import {clone, cmp, equal, isObject, length, pyStr, readJson, repr, sha256, slice, truth, unique, walk, writeJson, writeText} from '../util.js';
import * as facts from './facts.js';
import * as schema from './schema.js';
import * as conditions from './conditions.js';
import {KNOWN_JURISDICTIONS, LIFECYCLES, PIPELINE_VERSION, STATE_NAMES, Paths, categories, loadSchema} from './config.js';
import {Doc, loadCorpus} from './corpus.js';
import {scoreText} from './keywords.js';
import {chapterOf, chapterCitation} from './chapters.js';
import {loadIndex} from './packets.js';
import {classify, extractJsonObjects} from './parse.js';
import {DocIndex} from './spans.js';
import {renderReport} from './report.js';
export const NULLISH = new Set(['', 'null', 'none', 'n/a', 'na', 'unknown', 'not stated', 'not specified', 'not applicable', '-']);
const FEDERAL_CITATION = /\bU\.?\s?S\.?\s?C\b|\bC\.?\s?F\.?\s?R\b(?!\w)|\bPub(?:lic|\.)\s?L(?:aw|\.)/i;
const LIFECYCLE_ALIASES: Data = {in_force: 'enacted', 'in force': 'enacted', effective: 'enacted', law: 'enacted', adopted: 'enacted', pending: 'pending_bill', bill: 'pending_bill', proposed: 'pending_bill', struck: 'failed', defeated: 'failed', vetoed: 'failed', withdrawn: 'failed'};
export const SCHEMA_ORDER = ['team_rule_id', 'jurisdiction', 'level', 'category', 'status', 'title', 'requirement', 'key_value', 'coverage_conditions', 'exemptions', 'overrides', 'interaction', 'effective_date', 'citation', 'source_doc_id', 'source_url', 'quoted_span', 'confidence', 'conflict_flag', 'conflict_note'];
const HEADLINE_WORDS: Data = {rent_increase_limits: 'cap|maximum|limit|percent|%|cpi|allowable|annual|rent control|stabiliz|prohibit', just_cause_eviction: 'just cause|good cause|grounds|causes?|eviction|terminat', security_deposits: 'cap|maximum|exceed|limit|deposit', application_screening_fees: 'cap|maximum|fee|limit', screening_restrictions: 'criminal|source of income|credit|screen|background|fair chance|voucher', algorithmic_rent_setting: 'unlawful|prohibit|ban|algorithm|pricing'};
const EXCEPTION_WORDS = /exception|exempt|small landlord|service member|qualif|interest|photograph|itemiz|return|nonrefundable|bad faith|retaliat|procedur|notice|filing|coverage|definition|penalt|remed/i;
const OVERRIDE_FIELDS = new Set(['effective_date', 'lifecycle', 'key_value', 'title', 'requirement', 'conflict_flag', 'conflict_note']);
export const val = (v: any): any => typeof v === 'string' ? NULLISH.has(v.trim().toLowerCase()) ? null : v.trim() : v ?? null;
const toBool = (v: any): boolean | null => typeof v === 'boolean' ? v : typeof v === 'string' && ['true', 'false'].includes(v.trim().toLowerCase()) ? v.trim().toLowerCase() === 'true' : v == null ? false : null;
export function sourcePriority(doc?: Doc): number {const st = (doc?.source_type ?? '').toLowerCase(); return st.includes('city-linked') ? 2 : st.includes('official') || st.includes('code publisher') ? 3 : 1;}
export function toSchemaRecord(rule: Data, id: string): Data {return Object.fromEntries(SCHEMA_ORDER.map(k => [k, k === 'team_rule_id' ? id : rule[k] ?? null]));}
export class Validator {
  cats: string[]; indexes: Record<string, DocIndex> = Object.create(null); datesCache: Record<string, Set<string>> = Object.create(null); numsCache: Record<string, Set<string>> = Object.create(null); scoresCache: Record<string, Record<string, number>> = Object.create(null); actCache: Record<string, facts.ActDates | null> = Object.create(null);
  constructor(public docs: Record<string, Doc>, public index: Data, public schema: Data, public as_of: string) {this.cats = categories(schema);}
  act(did: string): facts.ActDates | null {if (!Object.hasOwn(this.actCache, did)) this.actCache[did] = facts.actDates(this.docs[did].body); return this.actCache[did];}
  docIndex(did: string): DocIndex {return this.indexes[did] ??= new DocIndex(this.docs[did].body);}
  dates(did: string): Set<string> {if (!this.datesCache[did]) {const found = facts.docDates(this.docs[did].body), a = this.act(did); if (a) for (const x of [a.effective, a.effective.slice(0, 7), a.effective.slice(0, 4)]) found.add(x); this.datesCache[did] = found;} return this.datesCache[did];}
  nums(did: string): Set<string> {return this.numsCache[did] ??= facts.numbersIn(this.docs[did].body);}
  scores(did: string): Record<string, number> {return this.scoresCache[did] ??= scoreText(this.docs[did].body);}
  check(raw: Data): [Data | null, string[], string[]] {
    const errors: string[] = [], warns: string[] = [];
    for (const k of ['packet_id', 'doc_id', 'jurisdiction', 'category', 'lifecycle', 'title', 'requirement', 'citation', 'quoted_span', 'effective_date', 'key_value', 'coverage_conditions', 'exemptions', 'penalty', 'interaction', 'conflict_note', 'valid_through']) if (raw[k] != null && typeof raw[k] !== 'string') errors.push(k + ' must be text or null');
    if (isObject(raw.applicability)) for (const k of ['built_on_or_before', 'built_after', 'date_basis', 'other']) if (raw.applicability[k] != null && typeof raw.applicability[k] !== 'string') errors.push('applicability.' + k + ' must be text or null');
    if (errors.length) return [null, errors, warns]; const g = (k: string): any => val(raw[k]), pid = g('packet_id'), did = g('doc_id');
    if (!Object.hasOwn(this.index.packets, pid)) return [null, ['unknown packet_id ' + repr(pid)], []]; const pdoc = this.index.packets[pid].doc_id, doc = this.docs[pdoc];
    if (did && did !== pdoc) errors.push(`doc_id ${repr(did)} does not match packet ${pid} (document ${pdoc})`);
    if (!doc?.has_text) return [null, [`document ${pdoc} has no text`], []];
    for (const k of ['jurisdiction', 'category', 'lifecycle', 'title', 'requirement', 'citation', 'quoted_span']) if (!g(k)) errors.push('missing ' + k);
    const category = (g('category') || '').toLowerCase().replaceAll('-', '_').replaceAll(' ', '_'); if (category && !this.cats.includes(category)) errors.push(`category ${repr(g('category'))} is not one of ${this.cats.join(', ')}`);
    let lifecycle = (g('lifecycle') || '').toLowerCase(); lifecycle = LIFECYCLE_ALIASES[lifecycle] || lifecycle;
    if (lifecycle && !LIFECYCLES.includes(lifecycle)) errors.push(`lifecycle ${repr(g('lifecycle'))} must be enacted, pending_bill or failed`); else if (lifecycle && g('lifecycle').toLowerCase() !== lifecycle) warns.push(`lifecycle ${repr(g('lifecycle'))} read as ${repr(lifecycle)}`);
    const jur = g('jurisdiction') ? facts.normalizeJurisdiction(g('jurisdiction'), KNOWN_JURISDICTIONS, STATE_NAMES) : null;
    if (g('jurisdiction') && !jur) errors.push(`jurisdiction ${repr(g('jurisdiction'))} must be a state code or 'City, ST'`); else if (jur && !KNOWN_JURISDICTIONS.includes(jur)) warns.push(`jurisdiction ${repr(jur)} is outside the challenge scope`);
    const notes: string[] = []; let eff = g('effective_date'), dateSource: string | null = eff != null ? 'model' : null; const act = lifecycle === 'enacted' ? this.act(pdoc) : null;
    if (eff != null) {
      const norm = facts.normalizeDate(eff);
      if (!norm) errors.push(`effective_date ${repr(eff)} is not a date (use YYYY-MM-DD, YYYY-MM or YYYY)`);
      else {if (norm !== eff) warns.push(`effective_date ${repr(eff)} rewritten as ${norm}`); eff = norm;
        if (act && act.effective.startsWith(eff) && eff !== act.effective) {notes.push(`effective_date ${eff} made exact (${act.effective}) from the act's own clause`); eff = act.effective; dateSource = 'act clause';}
        else if (act && eff !== act.effective) warns.push(`effective_date ${eff} differs from ${act.effective}, which the act's own clause gives (${act.clause}, approved ${act.approved})`);
        else if (!facts.dateSupported(eff, this.dates(pdoc))) warns.push(`effective_date ${eff} does not appear in ${pdoc}: check it`);
      }
    } else if (act) {eff = act.effective; dateSource = 'act clause'; notes.push(`effective_date ${act.effective} worked out from the act's own clause (${act.clause}) and its approval date ${act.approved}`);}
    let span: string | null = null; const rawSpan = g('quoted_span');
    if (rawSpan?.includes('[[omitted')) errors.push('quoted_span crosses an omitted section: quote one contiguous passage');
    else if (rawSpan) {const m = this.docIndex(pdoc).locate(rawSpan); if (!m) errors.push(`quoted_span not found in ${pdoc} (not verbatim): copy the sentence exactly`); else if (length(m.text) < 20) errors.push('quoted_span is shorter than 20 characters'); else {span = m.text; if (m.method !== 'exact') warns.push(`quoted_span realigned to the source (${m.method} match, ${m.score.toFixed(2)})`); if (length(span) > 1200) warns.push(`quoted_span is ${length(span)} characters long`);}}
    const locateQuote = (q: string): string | null => q.includes('[[omitted') ? null : this.docIndex(pdoc).locate(q)?.text ?? null;
    let validThrough = g('valid_through'); if (validThrough != null) {const vt = facts.normalizeDate(validThrough); if (!vt) warns.push(`valid_through ${repr(validThrough)} is not a date: ignored`); else if (!facts.dateSupported(vt, this.dates(pdoc))) warns.push(`valid_through ${vt} is not printed in ${pdoc}: check it`); validThrough = vt;}
    const applicability = conditions.parse(raw.applicability, warns, this.dates(pdoc), this.nums(pdoc), locateQuote), relations = conditions.parseRelations(raw.relations, warns, locateQuote), [citation, aspect] = facts.splitCitation(facts.normalizeCitation(g('citation') || ''));
    if (g('citation') && !citation) errors.push('citation is empty after cleanup'); const parts = citation.split(/\s*;\s*/).filter(Boolean);
    if (parts.length && parts.every(x => FEDERAL_CITATION.test(x))) errors.push(`citation ${repr(citation)} is a federal law; this program records only state and city rules (federal law is ignored): leave this record out`);
    if (aspect) notes.push('citation descriptor moved out of the citation: ' + aspect);
    let conf = raw.confidence ?? null; if (conf === null) warns.push('no confidence given'); else if (typeof conf === 'object' || (typeof conf === 'string' && !conf.trim()) || Number.isNaN(Number(conf))) {warns.push(`confidence ${repr(conf)} is not a number`); conf = null;} else conf = Math.max(0, Math.min(1, Number(conf)));
    let cf = toBool(raw.conflict_flag); if (cf === null) {warns.push(`conflict_flag ${repr(raw.conflict_flag)} read as false`); cf = false;}
    const keyValue = g('key_value'); if (keyValue) {const bad = facts.unsupportedNumbers(pyStr(keyValue), this.nums(pdoc)); if (bad.length) warns.push(`key_value numbers not found in ${pdoc}: ${bad.join(', ')}`);}
    if (this.cats.includes(category) && !this.scores(pdoc)[category]) warns.push(`${pdoc} never mentions anything about ${category}`);
    if (jur && doc.jurisdictions) {const dj = doc.jurisdictions.trim(), sameState = facts.stateOf(jur) === facts.stateOf(dj) && facts.levelOf(jur) === 'state'; if (jur.toLowerCase() !== dj.toLowerCase() && !sameState) warns.push(`rule jurisdiction ${jur} differs from document jurisdiction ${dj}`);}
    if (raw.status && LIFECYCLES.includes(lifecycle)) {const derived = facts.deriveStatus(lifecycle, eff && facts.ISO_ANY.test(eff) ? eff : null, this.as_of); if (pyStr(raw.status).toLowerCase() !== derived) warns.push(`model said status ${repr(raw.status)}, derived ${repr(derived)}`);}
    if (lifecycle === 'enacted' && /^(?:[SH]\.?\s?\d{3,5}|[AS]B\s?\d+)$/.test(citation) && !eff) warns.push('citation looks like a bill number but lifecycle is enacted: confirm it was signed');
    if (errors.length) return [null, errors, warns];
    const rule: Data = {jurisdiction: jur, level: facts.levelOf(jur!), category, lifecycle, status: facts.deriveStatus(lifecycle, eff, this.as_of), title: g('title'), requirement: g('requirement'), key_value: keyValue, coverage_conditions: g('coverage_conditions'), applicability, exemptions: g('exemptions'), penalty: g('penalty'), overrides: [], interaction: g('interaction'), effective_date: eff, valid_through: validThrough, relations, citation, aspect, citation_kind: /\d/.test(citation) ? 'numbered' : 'descriptive', source_doc_id: pdoc, source_url: doc.url, retrieved: doc.retrieved, quoted_span: span, confidence: conf, conflict_flag: cf, conflict_note: g('conflict_note'), packet_id: pid, date_source: dateSource, warnings: warns, notes};
    const bad = schema.check(toSchemaRecord(rule, 'r-0000'), this.schema); return bad.length ? [null, bad.map(b => 'schema: ' + b), warns] : [rule, [], warns];
  }
}
type Key = [string, string, string];
const groupKey = (r: Data): Key => [r.jurisdiction, r.category, facts.citationKey(r.citation)];
const keyStr = (k: Key): string => JSON.stringify(k);
const fullTokens = (c: string): string[] => unique(Array.from((c || '').matchAll(/[0-9][0-9A-Za-z.:\-]*/g), m => m[0].replace(/^[.:-]+|[.:-]+$/g, '').toLowerCase()).filter(Boolean));
const subset = (a: string[], b: string[]): boolean => a.every(x => b.includes(x));
const mergeKey = (r: Data): Key => {const ch = r.level === 'city' ? chapterOf(r.citation) : null; return ch ? [r.jurisdiction, r.category, 'ch:' + ch] : groupKey(r);};
function foldNested(groups: Map<string, Data[]>): Map<string, Data[]> {
  const toks = Object.fromEntries([...groups].map(([k, g]) => [k, unique(g.flatMap(r => fullTokens(r.citation)))])), target: Record<string, string> = {};
  for (const k of [...groups.keys()].sort((a, b) => toks[a].length - toks[b].length)) {
    if (toks[k].join('').length < 5) continue; const key: Key = JSON.parse(k);
    const bigger = [...groups.keys()].filter(o => o !== k && equal(JSON.parse(o).slice(0, 2), key.slice(0, 2)) && toks[k].length < toks[o].length && subset(toks[k], toks[o])).sort((a, b) => toks[a].length - toks[b].length); if (bigger.length) target[k] = bigger[0];
  }
  const out = new Map<string, Data[]>(); for (let [k, g] of groups) {while (target[k]) k = target[k]; out.set(k, [...out.get(k) || [], ...g]);} return out;
}
export function headlineKey(r: Data, pos: (r: Data) => number): [number, number] {const text = [r.aspect, r.title, r.key_value].filter(Boolean).join(' '); let score = new RegExp(HEADLINE_WORDS[r.category] || '$^', 'i').test(text) ? 3 : 0; if (EXCEPTION_WORDS.test(text)) score -= 2; score += (r.key_value ? 1 : 0) + (r.effective_date ? 1 : 0) + (!r.aspect ? 2 : 0) + (r.confidence || 0); return [-score, pos(r)];}
function consolidate(group: Data[], docs: Record<string, Doc>, pos: (r: Data) => number): [Data, string[]] {
  const byDoc = new Map<string, Data[]>(); for (const r of group) byDoc.set(r.source_doc_id, [...byDoc.get(r.source_doc_id) || [], r]); const heads: [string, Data][] = [], subs: Data[] = [];
  for (const [did, recs] of byDoc) {const ranked = [...recs].sort((a, b) => cmp(headlineKey(a, pos), headlineKey(b, pos))); heads.push([did, ranked[0]]); subs.push(...ranked.slice(1));}
  heads.sort((a, b) => cmp([-sourcePriority(docs[a[0]]), -(a[1].confidence || 0), a[0]], [-sourcePriority(docs[b[0]]), -(b[1].confidence || 0), b[0]]));
  const primary: Data = {...heads[0][1], relations: [...heads[0][1].relations || []], warnings: [...heads[0][1].warnings], notes: [...heads[0][1].notes]};
  for (const [did, h] of heads.slice(1)) {
    for (const f of ['key_value', 'coverage_conditions', 'exemptions', 'penalty', 'interaction', 'effective_date']) if (primary[f] == null && h[f] != null) {primary[f] = h[f]; primary.notes.push(f + ' filled in from ' + did);}
    primary.applicability = {...primary.applicability, coverage_quotes: [...primary.applicability.coverage_quotes]}; conditions.merge(primary, h, did, primary.notes, primary.warnings); for (const w of h.warnings) if (!primary.warnings.includes(w)) primary.warnings.push(w);
  }
  const conflicts: string[] = [];
  for (const [did, b] of heads.slice(1)) {const a = heads[0][1]; if (a.effective_date && b.effective_date && a.effective_date !== b.effective_date) conflicts.push(`effective_date: ${a.source_doc_id} says ${a.effective_date}, ${did} says ${b.effective_date}`); const sa = [...facts.numericSignature(a.key_value)].sort(), sb = [...facts.numericSignature(b.key_value)].sort(); if (sa.length && sb.length && !equal(sa, sb)) conflicts.push(`key_value: ${a.source_doc_id} says ${repr(a.key_value)}, ${did} says ${repr(b.key_value)}`); if (a.lifecycle !== b.lifecycle) conflicts.push(`lifecycle: ${a.source_doc_id} says ${a.lifecycle}, ${did} says ${b.lifecycle}`);}
  const notes = unique(conflicts).sort(); if (notes.length) {primary.conflict_flag = true; const extra = 'Sources disagree: ' + notes.join('; '); primary.conflict_note = primary.conflict_note ? primary.conflict_note + ' | ' + extra : extra;}
  primary.sources = heads.map(([did, h]) => ({doc_id: did, url: h.source_url, retrieved: h.retrieved, quoted_span: h.quoted_span, effective_date: h.effective_date, key_value: h.key_value, lifecycle: h.lifecycle})); primary.sub_rules = subs.map(x => ({doc_id: x.source_doc_id, aspect: x.aspect ?? null, citation: x.citation, title: x.title, key_value: x.key_value, effective_date: x.effective_date, quoted_span: x.quoted_span})); primary.merged_from = group.length;
  const cited = unique<string>(group.map(g => g.citation)), sets = unique(group.map(g => JSON.stringify(fullTokens(g.citation).sort()))).map(s => JSON.parse(s) as string[]), chain = sets.every(x => sets.every(y => subset(x, y) || subset(y, x))), ch = primary.level === 'city' ? chapterOf(primary.citation) : null;
  if (sets.length > 1 && chain) {const plainest = [...cited].sort((a, b) => cmp([fullTokens(a).length, length(a)], [fullTokens(b).length, length(b)]))[0]; primary.notes.push(`citations ${slice([...cited].sort().join('; '), 0, 200)} merged; kept ${plainest}`); primary.citation = plainest;}
  else if (ch && sets.length > 1) {for (const x of subs) conditions.merge(primary, x, x.source_doc_id, [], []); primary.notes.push(`${cited.length} sections of chapter ${ch} merged into one rule: ${slice([...cited].sort().join('; '), 0, 300)}`); primary.citation = chapterCitation(primary.citation, ch); primary.citation_kind = 'numbered';}
  return [primary, notes];
}
export function loadOverrides(paths: Paths): Data[] {const file = path.join(paths.work_dir, 'overrides.json'); if (!fs.existsSync(file)) return []; const data = readJson(file), items: Data[] = Array.isArray(data) ? data : data.overrides; for (const ov of items) {for (const k of ['id', 'match', 'set', 'reason', 'source']) if (!Object.hasOwn(ov, k)) throw new Error(`overrides.json: entry ${repr(ov.id)} is missing ${repr(k)}`); const bad = Object.keys(ov.set).filter(k => !OVERRIDE_FIELDS.has(k)); if (bad.length) throw new Error(`overrides.json: ${ov.id} may not set ${bad.sort().join(', ')}`);} return items;}
export function applyOverrides(rules: Data[], overrides: Data[], asOf: string): [Data[], string[]] {
  const applied: Data[] = [], unused: string[] = []; for (const ov of overrides) {const m = ov.match, hits = rules.filter(r => (!m.jurisdiction || r.jurisdiction === m.jurisdiction) && (!m.category || r.category === m.category) && (!m.source_doc_id || r.source_doc_id === m.source_doc_id) && (!m.citation_contains || r.citation.toLowerCase().includes(m.citation_contains.toLowerCase()))); if (!hits.length) {unused.push(ov.id); continue;}
    for (const r of hits) {const before = Object.fromEntries(Object.keys(ov.set).map(k => [k, r[k] ?? null])); Object.assign(r, ov.set); r.status = facts.deriveStatus(r.lifecycle, r.effective_date, asOf); if (Object.hasOwn(ov.set, 'effective_date')) r.date_source = 'override ' + ov.id; r.notes = [...r.notes || [], `override ${ov.id}: ${ov.reason}`]; const rec = {id: ov.id, rule: `${r.jurisdiction} | ${r.category} | ${r.citation}`, before, after: {...ov.set}, reason: ov.reason, source: ov.source}; r.overrides_applied = [...r.overrides_applied || [], rec]; applied.push(rec);}
  } return [applied, unused];
}
// Historical saved answers used Python's numeric equality for receipt counts;
// incoming API answers are validated more strictly before entering the inbox.
const countEqual = (v: unknown, n: number): boolean => typeof v === 'boolean' ? Number(v) === n : v === n;
export class PacketResp {records: Data[] = []; rules: Data[] = []; receipt: Data | null = null; rejected = 0; constructor(public file = '') {} get accepted(): number {return this.rules.length;} get clean(): boolean {return this.receipt !== null && countEqual(this.receipt.n_rules, this.records.length) && !this.rejected;}}
export interface IngestResult {as_of: string; files: Data[]; parse_problems: [string, string][]; rules: Data[]; rejected: Data[]; states: Record<string, Data>; conflicts: [string, string[]][]; near_duplicates: [string, string, string][]; counts: Record<string, number>; problems: Record<string, string[]>; matrix_extra: string[]; dropped: [string, string, string][]; overrides_applied: Data[]; overrides_unused: string[];}
export function listInbox(paths: Paths): string[] {return walk(paths.inbox_dir).filter(p => !/^[._]/.test(path.basename(p)) && ['.txt', '.md', '.json', '.jsonl'].includes(path.extname(p).toLowerCase())).sort((a, b) => cmp([fs.statSync(a).mtimeMs, path.basename(a)], [fs.statSync(b).mtimeMs, path.basename(b)]));}
export function runIngest(paths: Paths, asOf?: string, persistIds = true): IngestResult {
  const index = loadIndex(paths), as_of = asOf || index.as_of, docs = loadCorpus(paths), schema = loadSchema(paths), validator = new Validator(docs, index, schema, as_of), docsPackets: Record<string, string[]> = Object.create(null);
  const positions: Record<string, number> = {}, pos = (r: Data): number => {const k = JSON.stringify([r.source_doc_id, r.quoted_span]); if (!(k in positions)) {const i = docs[r.source_doc_id].body.indexOf(r.quoted_span); positions[k] = i < 0 ? 1e9 : length(docs[r.source_doc_id].body.slice(0, i));} return positions[k];};
  for (const [pid, m] of Object.entries<Data>(index.packets)) (docsPackets[m.doc_id] ??= []).push(pid);
  const files: Data[] = [], parseProblems: [string, string][] = [], rejected: Data[] = [], responses = new Map<string, PacketResp[]>(); let nRecords = 0;
  for (const file of listInbox(paths)) {
    const data = fs.readFileSync(file), [objs, problems] = extractJsonObjects(data.toString('utf8')), name = path.basename(file); files.push({name: path.relative(paths.inbox_dir, file), sha256: sha256(data), bytes: data.length, objects: objs.length}); parseProblems.push(...problems.map(p => [name, p] as [string, string])); const resp = new Map<string, PacketResp>();
    for (const obj of objs) {const kind = classify(obj); if (kind === 'other') continue; let pid = val(obj.packet_id); const did = val(obj.doc_id); if (kind === 'record' && !pid && docsPackets[did]?.length === 1) {pid = docsPackets[did][0]; obj.packet_id = pid;}
      const key = pid || '?', bucket = resp.get(key) ?? new PacketResp(name); resp.set(key, bucket); if (kind === 'receipt') {bucket.receipt = obj; continue;}
      nRecords++; bucket.records.push(obj); const [rule, errs] = validator.check(obj); if (errs.length) {bucket.rejected++; rejected.push({file: name, packet_id: pid, reasons: errs, record: obj});} else {rule!._file = name; rule!._raw = obj; bucket.rules.push(rule!);}
    }
    for (const [pid, bucket] of resp) if (Object.hasOwn(index.packets, pid)) {
      const groups = new Map<string, Data[]>(); for (const r of bucket.rules) {const key = keyStr(groupKey(r)); groups.set(key, [...groups.get(key) || [], r]);}
      for (const grp of groups.values()) if (grp.length > 1) {const ranked = [...grp].sort((a, b) => cmp(headlineKey(a, pos), headlineKey(b, pos))), keep = ranked[0]; for (const x of ranked.slice(1)) {bucket.rules.splice(bucket.rules.indexOf(x), 1); bucket.rejected++; rejected.push({file: name, packet_id: pid, record: x._raw, reasons: [`one record per law and category: you also wrote '${slice(keep.title, 0, 60)}' for ${keep.citation} (${keep.category}). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date`]});}}
      responses.set(pid, [...responses.get(pid) || [], bucket]);
    }
  }
  const latest = Object.fromEntries([...responses].map(([pid, rs]) => [pid, rs.at(-1)!])); for (const rj of rejected) rj.open = Boolean(latest[rj.packet_id] && latest[rj.packet_id].file === rj.file);
  const states: Record<string, Data> = {}, problems: Record<string, string[]> = {};
  for (const pid of Object.keys(index.packets)) {const r = latest[pid]; if (!r) {states[pid] = {state: 'pending', detail: 'no answer yet'}; problems[pid] = []; continue;} const msgs: string[] = []; let state: string, detail: string;
    if (!r.receipt) {state = 'incomplete'; detail = 'no receipt line (answer probably cut off)'; msgs.push('no receipt line was found; the answer was probably cut off. Re-emit the records and the receipt');}
    else if (!countEqual(r.receipt.n_rules, r.records.length)) {state = 'mismatch'; detail = `receipt says ${pyStr(r.receipt.n_rules ?? null)} record(s), ${r.records.length} parsed`; msgs.push(`receipt n_rules=${pyStr(r.receipt.n_rules ?? null)} but ${r.records.length} records were parsed`);}
    else if (r.rejected) {state = 'needs_fix'; detail = `${r.rejected} record(s) rejected`;} else {state = 'done'; detail = `${r.accepted} rule(s)`;}
    if (r.rejected) for (const rj of rejected) if (rj.packet_id === pid && rj.file === r.file) msgs.push(`record '${slice(pyStr(rj.record.title), 0, 60)}' (${slice(pyStr(rj.record.citation), 0, 50)}): ${rj.reasons.join('; ')}`);
    states[pid] = {state, detail, file: r.file}; problems[pid] = state === 'done' ? [] : msgs;
  }
  const pool: Data[] = [], dropped: [string, string, string][] = [];
  for (const [pid, rs] of responses) if (rs.at(-1)!.clean) {pool.push(...rs.at(-1)!.rules); const kept = new Set(rs.at(-1)!.rules.map(x => keyStr(groupKey(x)))), seen = new Set<string>(); for (const old of rs.slice(0, -1)) for (const x of old.rules) {const k = keyStr(groupKey(x)); if (!kept.has(k) && !seen.has(k)) {seen.add(k); dropped.push([pid, `${x.jurisdiction} | ${x.category}`, x.citation]);}}} else for (const r of rs) pool.push(...r.rules);
  let groups = new Map<string, Data[]>(); for (const r of pool) {const key = keyStr(mergeKey(r)); groups.set(key, [...groups.get(key) || [], r]);} groups = foldNested(groups);
  const merged: Data[] = [], conflicts: [string, string[]][] = []; for (const [key, grp] of groups) {const [r, notes] = consolidate(grp, docs, pos); merged.push(r); if (notes.length) conflicts.push([JSON.parse(key).slice(0, 2).join(' / ') + ' ' + r.citation, notes]);}
  const [applied, unused] = applyOverrides(merged, loadOverrides(paths), as_of), catOrder = categories(schema); merged.sort((a, b) => cmp([a.level === 'state' ? 0 : 1, a.jurisdiction, catOrder.includes(a.category) ? catOrder.indexOf(a.category) : 99, a.citation], [b.level === 'state' ? 0 : 1, b.jurisdiction, catOrder.includes(b.category) ? catOrder.indexOf(b.category) : 99, b.citation]));
  const near: [string, string, string][] = []; for (let i = 0; i < merged.length; i++) for (const b of merged.slice(i + 1)) {const a = merged[i]; if (a.jurisdiction === b.jurisdiction && a.category === b.category) {const ta = [...facts.keyTokens(facts.citationKey(a.citation))].sort(), tb = [...facts.keyTokens(facts.citationKey(b.citation))].sort(); if (ta.length && tb.length && ta.some(x => tb.includes(x)) && !equal(ta, tb)) near.push([a.jurisdiction + ' / ' + a.category, a.citation, b.citation]);}}
  assignIds(paths, merged, persistIds);
  const counts = {files: files.length, records_parsed: nRecords, accepted: pool.length, rejected: rejected.filter(r => r.open).length, rejected_fixed: rejected.filter(r => !r.open).length, rules: merged.length, packets_total: Object.keys(index.packets).length, packets_done: Object.values(states).filter(s => s.state === 'done').length};
  return {as_of, files, parse_problems: parseProblems, rules: merged, rejected, states, conflicts, near_duplicates: near, counts, problems, matrix_extra: [], dropped, overrides_applied: applied, overrides_unused: unused};
}
export function assignIds(paths: Paths, rules: Data[], persist = true): Data {const file = path.join(paths.work_dir, 'id_registry.json'), reg = fs.existsSync(file) ? readJson(file) : {next: 1, ids: {}}; for (const r of rules) {const key = groupKey(r).join('|'); if (!Object.hasOwn(reg.ids, key)) {reg.ids[key] = 'r-' + String(reg.next++).padStart(4, '0');} r.team_rule_id = reg.ids[key];} if (persist) writeJson(file, reg, false, 1); return reg.ids;}
export function writeOutputs(paths: Paths, res: IngestResult, format = 'wrapped'): Record<string, string> {
  const records = res.rules.map(r => toSchemaRecord(r, r.team_rule_id)), ruleFile = path.join(paths.out_dir, 'rules.json'); writeJson(ruleFile, format === 'wrapped' ? {rules: records} : records, false);
  const enriched = res.rules.map(r => {const e = toSchemaRecord(r, r.team_rule_id); for (const k of ['lifecycle', 'applicability', 'penalty', 'retrieved', 'packet_id', 'aspect', 'citation_kind', 'date_source', 'warnings', 'notes', 'sources', 'sub_rules', 'merged_from', 'overrides_applied', 'valid_through', 'relations']) e[k] = r[k] ?? null; e.as_of = res.as_of; return e;});
  writeJson(path.join(paths.work_dir, 'rules_enriched.json'), enriched, false); writeText(path.join(paths.work_dir, 'rejected.jsonl'), res.rejected.map(r => JSON.stringify(r) + '\n').join('')); writeJson(path.join(paths.work_dir, 'problems.json'), res.problems, false, 1); writeText(path.join(paths.work_dir, 'report.md'), renderReport(paths, res));
  const audit = {pipeline_version: PIPELINE_VERSION, as_of: res.as_of, ran_at: new Date().toISOString().slice(0, 19).replace('T', ' ') + ' UTC', inputs: res.files, counts: res.counts, outputs: {'rules.json': sha256(fs.readFileSync(ruleFile))}}; writeJson(path.join(paths.work_dir, 'audit.json'), audit, false);
  return {rules: ruleFile, report: path.join(paths.work_dir, 'report.md')};
}
export const pendingPackets = (res: IngestResult): Record<string, string[]> => Object.fromEntries(Object.entries(res.states).filter(([, s]) => s.state !== 'done').map(([pid]) => [pid, res.problems[pid] ?? []]));
