import {length, slice} from '../util.js';
import {isRelevant, scoreText} from './keywords.js';
export const NAV_RUN_MIN = 8, NAV_MARKER = '[[omitted: page navigation]]';
function navish(line: string): boolean {
  const s = line.trim();
  return !!s && length(s) <= 45 && s.split(/\s+/).length <= 5 && !/[.;:!?]$/.test(s) && !/\d/.test(s) && !/^\(?[A-Za-z]{1,3}[\).]\s/.test(s);
}
function softWrap(line: string): string[] {
  if (length(line) <= 1200) return [line]; const parts: string[] = [];
  while (length(line) > 1200) {
    const chars = Array.from(line); let cut = chars.slice(0, 1000).lastIndexOf(' ');
    if (cut < 500) {cut = chars.indexOf(' ', 1000); if (cut < 0) break;}
    parts.push(chars.slice(0, cut).join('')); line = chars.slice(cut + 1).join('');
  }
  parts.push(line); return parts;
}
export function cleanText(body: string): [string, number, number] {
  const text = body.replaceAll('\u00a0', ' ').replaceAll('\u200b', '').replaceAll('\ufeff', '').replaceAll('\u00ad', '').replaceAll('\f', '\n');
  const lines = text.split('\n').map(s => s.trimEnd()), keep = lines.map(() => true), marks = new Set<number>(); let i = 0;
  while (i < lines.length) {
    if (navish(lines[i])) {
      let j = i, count = 0, last = i;
      while (j < lines.length && (!lines[j].trim() || navish(lines[j]))) {if (lines[j].trim()) {count++; last = j;} j++;}
      if (count >= 8) {for (let k = i; k <= last; k++) keep[k] = false; marks.add(i);}
      i = Math.max(j, i + 1);
    } else i++;
  }
  const removedLines = lines.filter((ln, k) => !keep[k] && ln.trim()).length;
  const removedChars = lines.reduce((sum, ln, k) => sum + (!keep[k] ? length(ln) + 1 : 0), 0);
  const out: string[] = []; let blank = 0;
  lines.forEach((ln, pos) => {
    if (!keep[pos]) {if (marks.has(pos)) {out.push(NAV_MARKER); blank = 0;} return;}
    if (!ln.trim()) {blank++; if (blank <= 1) out.push('');}
    else {blank = 0; out.push(ln);}
  });
  return [out.flatMap(softWrap).join('\n').replace(/^\n+|\n+$/g, ''), removedLines, removedChars];
}
const HEADING = /^\s*(?:§+\s*\d[\w.\-]*|Sec(?:tion|\.)\s+\d[\w.\-]*|\d{1,3}(?:\.\d{1,4}){1,3}\.?\s+\S|\d{4}(?:\.\d+)?\.\s*$|(?:CHAPTER|ARTICLE|DIVISION|TITLE|PART|SUBCHAPTER)\s+[\w.\-]+|SECTION\s+\d+\.|\d{1,3}\.\s+[A-Z][^\n]{3,80}$|[A-Z][A-Z0-9 ,&'\-]{8,80}$)/;
export class Block {
  constructor(public idx: number, public text: string, public scores = scoreText(text)) {}
  get relevant(): boolean {return isRelevant(this.scores);}
  get heading(): string {return slice(this.text.split('\n').find(s => s.trim())?.trim() ?? '', 0, 100);}
}
export function splitBlocks(clean: string): Block[] {
  const blocks: Block[] = []; let cur: string[] = [], size = 0;
  const flush = (): void => {const txt = cur.join('\n').replace(/^\n+|\n+$/g, ''); if (txt.trim()) blocks.push(new Block(blocks.length, txt)); cur = []; size = 0;};
  for (const line of clean.split('\n')) {
    const blank = !line.trim();
    if (cur.length && size >= 700 && !blank && HEADING.test(line)) flush();
    else if (cur.length && size >= 3500 && blank) {flush(); continue;}
    else if (cur.length && size + length(line) + 1 > 6000) flush();
    cur.push(line); size += length(line) + 1;
  }
  flush(); return blocks;
}
export function selectBlocks(blocks: Block[], budget: number): boolean[] {
  if (blocks.reduce((s, b) => s + length(b.text), 0) <= budget) return blocks.map(() => true);
  const keep = blocks.map(() => false), score = (i: number): number => Object.values(blocks[i].scores).reduce((a, b) => a + b, 0);
  const order = blocks.map((_, i) => i).sort((a, b) => score(b) - score(a) || a - b); let used = 0;
  for (const i of order) {if (score(i) <= 0) break; if (used + length(blocks[i].text) > budget) continue; keep[i] = true; used += length(blocks[i].text);}
  for (const i of order) if (keep[i]) for (const j of [i - 1, i + 1]) if (j >= 0 && j < blocks.length && !keep[j] && used + length(blocks[j].text) <= budget && score(j) > 0) {keep[j] = true; used += length(blocks[j].text);}
  return keep;
}
