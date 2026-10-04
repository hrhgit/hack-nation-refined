import {cmp} from '../util.js';
export interface SpanMatch {start: number; end: number; method: string; score: number; text: string;}
export const tokens = (text: string): string[] => Array.from(text.matchAll(/[\p{L}\p{N}_]+/gu), m => m[0].toLowerCase());

// Same matching-block algorithm as Python SequenceMatcher with autojunk=False.
// Keeping its tie order is necessary when a passage repeats the same words.
function matchingBlocks(a: string[], b: string[]): [number, number, number][] {
  const b2j = new Map<string, number[]>();
  b.forEach((word, i) => {if (!b2j.has(word)) b2j.set(word, []); b2j.get(word)!.push(i);});
  const longest = (alo: number, ahi: number, blo: number, bhi: number): [number, number, number] => {
    let besti = alo, bestj = blo, bestsize = 0, last = new Map<number, number>();
    for (let i = alo; i < ahi; i++) {
      const current = new Map<number, number>();
      for (const j of b2j.get(a[i]) ?? []) {
        if (j < blo) continue; if (j >= bhi) break;
        const k = (last.get(j - 1) ?? 0) + 1; current.set(j, k);
        if (k > bestsize) {besti = i - k + 1; bestj = j - k + 1; bestsize = k;}
      }
      last = current;
    }
    while (besti > alo && bestj > blo && a[besti - 1] === b[bestj - 1]) {besti--; bestj--; bestsize++;}
    while (besti + bestsize < ahi && bestj + bestsize < bhi && a[besti + bestsize] === b[bestj + bestsize]) bestsize++;
    return [besti, bestj, bestsize];
  };
  const queue: [number, number, number, number][] = [[0, a.length, 0, b.length]], found: [number, number, number][] = [];
  while (queue.length) {
    const [alo, ahi, blo, bhi] = queue.pop()!, [i, j, k] = longest(alo, ahi, blo, bhi);
    if (!k) continue; found.push([i, j, k]);
    if (alo < i && blo < j) queue.push([alo, i, blo, j]);
    if (i + k < ahi && j + k < bhi) queue.push([i + k, ahi, j + k, bhi]);
  }
  found.sort(cmp); const merged: [number, number, number][] = [];
  for (const [i, j, k] of found) {
    const last = merged.at(-1);
    if (last && last[0] + last[2] === i && last[1] + last[2] === j) last[2] += k;
    else merged.push([i, j, k]);
  }
  return merged;
}
export class DocIndex {
  toks: string[] = []; starts: number[] = []; ends: number[] = [];
  first = new Map<string, number[]>(); private tri?: Map<string, number[]>; private chars: string[];
  constructor(public body: string) {
    this.chars = Array.from(body); let previous = 0, offset = 0;
    for (const m of body.matchAll(/[\p{L}\p{N}_]+/gu)) {
      offset += Array.from(body.slice(previous, m.index)).length; previous = m.index;
      const word = m[0].toLowerCase();
      if (!this.first.has(word)) this.first.set(word, []);
      this.first.get(word)!.push(this.toks.length); this.toks.push(word);
      this.starts.push(offset); offset += Array.from(m[0]).length; this.ends.push(offset); previous += m[0].length;
    }
  }
  private exact(t: string[], from = 0): [number, number] | null {
    for (const p of this.first.get(t[0]) ?? []) if (p >= from && t.every((x, i) => this.toks[p + i] === x)) return [p, p + t.length - 1];
    return null;
  }
  private make(a: number, b: number, span: string, method: string, score: number): SpanMatch {
    let s = this.starts[a], e = this.ends[b]; const sp = Array.from(span.trim()), lead = new Set<string>();
    for (const c of sp) {if (!'"\'“‘([§'.includes(c)) break; lead.add(c);}
    let k = sp.length; while (k > 0 && !/[\p{L}\p{N}]/u.test(sp[k - 1])) k--;
    const trail = new Set(sp.slice(k)); let n = 0;
    while (e < this.chars.length && trail.has(this.chars[e]) && n++ < sp.length - k) e++;
    n = 0; while (s > 0 && lead.has(this.chars[s - 1]) && n++ < lead.size) s--;
    return {start: s, end: e, method, score, text: this.chars.slice(s, e).join('').trim()};
  }
  locate(span: string): SpanMatch | null {
    const t = tokens(span); if (t.length < 3) return null;
    const hit = this.exact(t); if (hit) return this.make(...hit, span, 'exact', 1);
    const parts = span.split(/\[?\s*(?:\.\.\.|…)\s*\]?/).filter(p => tokens(p).length >= 3);
    if (parts.length >= 2) {
      let pos = 0, first: number | null = null, last = 0, ok = true;
      for (const part of parts) {const r = this.exact(tokens(part), pos); if (!r) {ok = false; break;} first ??= r[0]; last = r[1]; pos = last + 1;}
      if (ok && first !== null) return this.make(first, last, span, 'ellipsis', 1);
    }
    if (t.length < 6) return null;
    if (!this.tri) {
      this.tri = new Map();
      for (let i = 0; i < this.toks.length - 2; i++) {const k = this.toks.slice(i, i + 3).join('\0'); if (!this.tri.has(k)) this.tri.set(k, []); this.tri.get(k)!.push(i);}
    }
    const votes = new Map<number, number>();
    for (let i = 0; i < t.length - 2; i++) for (const p of this.tri.get(t.slice(i, i + 3).join('\0')) ?? []) votes.set(p - i, (votes.get(p - i) ?? 0) + 1);
    let best: [number, number, number] | null = null;
    for (const [cand] of Array.from(votes).sort((a, b) => b[1] - a[1]).slice(0, 5)) {
      const lo = Math.max(0, cand - 3), hi = Math.min(this.toks.length, cand + t.length + 3), blocks = matchingBlocks(this.toks.slice(lo, hi), t);
      if (!blocks.length) continue;
      const ratio = blocks.reduce((sum, b) => sum + b[2], 0) / t.length, a = lo + blocks[0][0], end = lo + blocks.at(-1)![0] + blocks.at(-1)![2] - 1;
      if (end - a + 1 > 2 * t.length + 10) continue;
      if (!best || ratio > best[0]) best = [ratio, a, end];
    }
    return best && best[0] >= .85 ? this.make(best[1], best[2], span, 'fuzzy', Number(best[0].toFixed(3))) : null;
  }
}
