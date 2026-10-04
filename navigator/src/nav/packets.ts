import fs from 'node:fs';
import path from 'node:path';
import {length, readJson, setKey, sha256, slice, sortedEntries, writeText} from '../util.js';
import type {Data} from '../types.js';
import {KNOWN_JURISDICTIONS, ROOT, PIPELINE_VERSION, Paths} from './config.js';
import {Doc, loadCorpus} from './corpus.js';
import {mergeScores} from './keywords.js';
import {Block, cleanText, selectBlocks, splitBlocks} from './textutil.js';
export const DEFAULT_MAX_CHARS = 24000, DEFAULT_BUDGET = 80000, DEFAULT_PASTE_CHARS = 50000;
export class Packet {
  constructor(public packet_id: string, public doc_id: string, public part: number, public parts: number, public text: string, public hits: Record<string, number>, public title_hint: string, public context: string[] = [], public notes: string[] = []) {}
  get chars(): number {return length(this.text);}
}
const omit = (n: number): string => `[[omitted: ${n.toLocaleString('en-US')} characters not relevant to the six categories]]`;
export function buildDocPackets(doc: Doc, maxChars = DEFAULT_MAX_CHARS, budget = DEFAULT_BUDGET): [Packet[], Data] {
  const [clean, rmLines, rmChars] = cleanText(doc.body), blocks = splitBlocks(clean), keep = selectBlocks(blocks, budget), groups: Block[][] = [];
  let cur: Block[] = [], curLen = 0;
  for (const b of blocks) if (keep[b.idx]) {if (cur.length && curLen + length(b.text) + 2 > maxChars) {groups.push(cur); cur = []; curLen = 0;} cur.push(b); curLen += length(b.text) + 2;}
  if (cur.length) groups.push(cur); const droppedBefore: Record<number, number> = {}; let prev = -1;
  for (const b of blocks) if (keep[b.idx]) {droppedBefore[b.idx] = blocks.slice(prev + 1, b.idx).reduce((n, x) => n + length(x.text), 0); prev = b.idx;}
  const tail = blocks.slice(prev + 1).reduce((n, b) => n + length(b.text), 0), title = slice(clean.split('\n').find(l => l.trim())?.trim() ?? '', 0, 120);
  const packets = groups.map((group, gi) => {
    const parts: string[] = []; for (const b of group) {if (droppedBefore[b.idx]) parts.push(omit(droppedBefore[b.idx])); parts.push(b.text);} if (gi === groups.length - 1 && tail) parts.push(omit(tail));
    const notes: string[] = []; if (groups.length > 1) notes.push(`part ${gi + 1} of ${groups.length} of a long document; the rest is in the other packets`);
    const dropped = keep.filter(k => !k).length; if (dropped) notes.push(`${dropped} of ${blocks.length} blocks of this document were left out as least relevant`);
    return new Packet(`${doc.doc_id}-${String(gi + 1).padStart(2, '0')}`, doc.doc_id, gi + 1, groups.length, parts.join('\n\n'), mergeScores(group.map(b => b.scores)), title, gi > 0 && group[0].idx > 0 ? [blocks[group[0].idx - 1].heading] : [], notes);
  });
  return [packets, {raw_chars: length(doc.body), clean_chars: length(clean), nav_lines_removed: rmLines, nav_chars_removed: rmChars, blocks: blocks.length, blocks_kept: keep.filter(Boolean).length, dropped_blocks: blocks.filter(b => !keep[b.idx]).map(b => ({idx: b.idx, chars: length(b.text), heading: b.heading})), packets: packets.map(p => p.packet_id)}];
}
export function renderPacket(p: Packet, doc: Doc, asOf: string): string {
  const hits = Object.entries(p.hits).sort((a, b) => b[1] - a[1]).filter(([, v]) => v).map(([k, v]) => `${k}=${v}`).join(', ') || 'none';
  return [`<<<PACKET ${p.packet_id}>>>`, `doc_id: ${doc.doc_id}`, `packet_id: ${p.packet_id}`, `part: ${p.part} of ${p.parts}`, `source_url: ${doc.url}`, `retrieved: ${doc.retrieved}`, `manifest_jurisdiction: ${doc.jurisdictions || 'unknown'}`, `as_of_date: ${asOf}`, `document_title_hint: ${p.title_hint}`, `keyword_hints (rough, may be wrong): ${hits}`, ...p.notes.map(n => 'note: ' + n), ...p.context.map(c => 'preceding_heading: ' + c), '<<<TEXT>>>', p.text, `<<<END PACKET ${p.packet_id}>>>`].join('\n') + '\n';
}
export function renderPrompt(asOf: string): string {
  let raw = fs.readFileSync(path.join(ROOT, 'prompts/extract_prompt.md'), 'utf8');
  if (raw.includes('{{PRIMER}}')) raw = raw.replaceAll('{{PRIMER}}', fs.readFileSync(path.join(ROOT, 'prompts/primer.md'), 'utf8').trim());
  return raw.replaceAll('{{AS_OF}}', asOf).replaceAll('{{JURISDICTIONS}}', KNOWN_JURISDICTIONS.map(j => `"${j}"`).join(', '));
}
export function renderDelivery(outFile: string): string {return fs.readFileSync(path.join(ROOT, 'prompts/delivery.typescript.md'), 'utf8').replaceAll('{{OUT_FILE}}', outFile).replaceAll('{{WORKDIR}}', ROOT);}
export function answerPath(paths: Paths, base: string): string {let cand = path.join(paths.inbox_dir, base + '.jsonl'), n = 2; while (fs.existsSync(cand)) cand = path.join(paths.inbox_dir, `${base}_r${n++}.jsonl`); return cand;}
export function loadIndex(paths: Paths): Data {if (!fs.existsSync(paths.index_file)) throw new Error('No packet index yet. Run: npm run nav -- prepare'); return readJson(paths.index_file);}
export function prepare(paths: Paths, asOf: string, maxChars = DEFAULT_MAX_CHARS, budget = DEFAULT_BUDGET, only?: string[]): Data {
  const docs = loadCorpus(paths); fs.mkdirSync(paths.packets_dir, {recursive: true}); fs.mkdirSync(paths.inbox_dir, {recursive: true}); let index: Data, todo: Doc[];
  if (only?.length) {
    index = fs.existsSync(paths.index_file) ? readJson(paths.index_file) : {packets: {}, docs: {}};
    for (const did of only) {for (const [pid, v] of Object.entries<Data>(index.packets)) if (v.doc_id === did) {fs.rmSync(path.join(paths.packets_dir, pid + '.md'), {force: true}); delete index.packets[pid];} delete index.docs[did];}
    const missing = only.filter(d => !docs[d]); if (missing.length) throw new Error('Unknown doc_id(s): ' + missing.join(', ')); todo = only.map(d => docs[d]);
  } else {fs.rmSync(paths.packets_dir, {recursive: true, force: true}); fs.mkdirSync(paths.packets_dir, {recursive: true}); index = {packets: {}, docs: {}}; todo = sortedEntries(docs).map(([, v]) => v);}
  for (const doc of todo) {
    if (!doc.has_text) {setKey(index.docs, doc.doc_id, {no_text: true, jurisdictions: doc.jurisdictions, url: doc.url, source_type: doc.source_type, capture: doc.capture, status: doc.status, origin: doc.origin}); continue;}
    const [packets, stats] = buildDocPackets(doc, maxChars, budget); setKey(index.docs, doc.doc_id, {...stats, no_text: false, jurisdictions: doc.jurisdictions, url: doc.url, source_type: doc.source_type, origin: doc.origin, file_sha256: doc.file_sha256});
    for (const p of packets) {const body = renderPacket(p, doc, asOf); writeText(path.join(paths.packets_dir, p.packet_id + '.md'), body); index.packets[p.packet_id] = {doc_id: doc.doc_id, part: p.part, parts: p.parts, chars: length(body), sha256: sha256(body), hits: p.hits};}
  }
  Object.assign(index, {as_of: asOf, pipeline_version: PIPELINE_VERSION, max_chars: maxChars, budget}); index.packets = Object.fromEntries(sortedEntries(index.packets)); index.docs = Object.fromEntries(sortedEntries(index.docs));
  writeText(paths.index_file, JSON.stringify(index, null, 1)); writeText(path.join(paths.work_dir, 'PROMPT.md'), renderPrompt(asOf)); writeGaps(paths, index); return index;
}
export function writeGaps(paths: Paths, index: Data): void {
  const rows = Object.entries<Data>(index.docs).filter(([, v]) => v.no_text), out = ['# Documents without text (not extractable until someone supplies the text)', '', `The corpus lists ${Object.keys(index.docs).length} documents but only ${Object.keys(index.docs).length - rows.length} have text. The rest cannot produce rules or quoted spans.`, '', 'To add one by hand (reading a page is allowed; do not bulk-scrape sites whose terms forbid it):', '', '    npm run nav -- add-doc --file page.txt --jurisdiction "Hoboken, NJ" --url <page url>', '', '| doc_id | jurisdiction | source type | capture | url |', '|---|---|---|---|---|'];
  for (const [id, v] of rows) out.push(`| ${id} | ${v.jurisdictions} | ${slice(v.source_type, 0, 24)} | ${v.capture} | ${v.url} |`); writeText(path.join(paths.work_dir, 'COVERAGE_GAPS.md'), out.join('\n') + '\n');
}
export function renderPacketInput(pid: string, text: string, problems: string[]): string {if (!problems.length) return text; return [`!!! CORRECTIONS NEEDED for packet ${pid}. An earlier answer for it had these problems:`, ...problems.map(m => '    - ' + m), '    Re-emit the corrected records for this packet (you may re-emit all of them), then its receipt.', '    `n_rules` in the receipt counts the records in THIS answer.\n'].join('\n') + '\n' + text;}
export function makeBatches(paths: Paths, pending: Record<string, string[]>, pasteChars = DEFAULT_PASTE_CHARS): string[] {
  const index = loadIndex(paths), prompt = renderPrompt(index.as_of); fs.rmSync(paths.paste_dir, {recursive: true, force: true}); fs.mkdirSync(paths.paste_dir, {recursive: true});
  const batches: [string, string][][] = []; let cur: [string, string][] = [], size = 0;
  for (const [pid, problems] of sortedEntries(pending)) {const file = path.join(paths.packets_dir, pid + '.md'); if (!fs.existsSync(file)) continue; const text = renderPacketInput(pid, fs.readFileSync(file, 'utf8'), problems); if (cur.length && size + length(text) > pasteChars) {batches.push(cur); cur = []; size = 0;} cur.push([pid, text]); size += length(text);}
  if (cur.length) batches.push(cur);
  return batches.map((batch, i) => {const ids = batch.map(([p]) => p), name = `BATCH-${String(i + 1).padStart(2, '0')}_${ids[0]}_to_${ids.at(-1)}.md`, outfile = answerPath(paths, name.slice(0, -3)); const body = [prompt, '\n---\n', renderDelivery(outfile), '\n---\n', '# SOURCE PACKETS', '', `This batch contains ${ids.length} packet(s): ${ids.join(', ')}.`, 'Now write your answer as described under DELIVERY: for each packet, in order, its JSON records and then its receipt line. JSON Lines only.', '', ...batch.map(([, t]) => t)].join('\n'); writeText(path.join(paths.paste_dir, name), body); return name;});
}
