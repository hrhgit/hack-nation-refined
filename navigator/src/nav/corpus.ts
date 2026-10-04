import fs from 'node:fs';
import path from 'node:path';
import {csvRecords, csvRow, hashFile, writeText} from '../util.js';
import {Paths} from './config.js';
export const MANIFEST_COLUMNS = ['doc_id', 'jurisdictions', 'url', 'source_type', 'capture', 'retrieved_at', 'sha256', 'text_file', 'status'];
export class Doc {
  origin = 'starter'; body = ''; header_url = ''; header_retrieved = ''; file_sha256 = '';
  constructor(public doc_id: string, public jurisdictions: string, public url: string, public source_type: string, public capture: string, public retrieved_at: string, public status: string, public text_path: string | null) {}
  get has_text(): boolean {return Boolean(this.body.trim());}
  get retrieved(): string {return this.header_retrieved || this.retrieved_at;}
}
export function splitHeader(raw: string): [Record<string, string>, string] {
  const lines = raw.split('\n'), meta: Record<string, string> = {}; let i = 0;
  for (; i < lines.length; i++) {const m = /^(SOURCE|RETRIEVED):\s*(.*)$/.exec(lines[i]); if (!m) break; meta[m[1]] = m[2].trim();}
  return [meta, lines.slice(i).join('\n').replace(/^\n+/, '')];
}
export function loadCorpus(paths: Paths): Record<string, Doc> {
  const docs: Record<string, Doc> = Object.create(null);
  for (const [file, base, origin] of [[paths.manifest, paths.corpus_dir, 'starter'], [paths.extra_manifest, paths.extra_dir, 'extra']]) {
    if (!fs.existsSync(file)) continue;
    for (const r of csvRecords(fs.readFileSync(file, 'utf8'))) {
      const id = (r.doc_id || '').trim(); if (!id) continue; const tf = (r.text_file || '').trim();
      const doc = new Doc(id, (r.jurisdictions || '').trim(), (r.url || '').trim(), (r.source_type || '').trim(), (r.capture || '').trim(), (r.retrieved_at || '').trim(), (r.status || '').trim(), tf ? path.join(base, tf) : null); doc.origin = origin;
      if (doc.text_path && fs.existsSync(doc.text_path)) {doc.file_sha256 = hashFile(doc.text_path); const [meta, body] = splitHeader(fs.readFileSync(doc.text_path, 'utf8').replace(/\r\n?/g, '\n')); doc.body = body; doc.header_url = meta.SOURCE || ''; doc.header_retrieved = meta.RETRIEVED || '';}
      docs[id] = doc;
    }
  }
  return docs;
}
export function nextExtraId(paths: Paths): string {let n = 0; if (fs.existsSync(paths.extra_manifest)) for (const r of csvRecords(fs.readFileSync(paths.extra_manifest, 'utf8'))) {const m = /^X(\d+)$/.exec(r.doc_id || ''); if (m) n = Math.max(n, +m[1]);} return 'X' + String(n + 1).padStart(3, '0');}
export function addExtraDoc(paths: Paths, text: string, jurisdiction: string, url: string, docId = '', sourceType = 'official', retrieved = ''): string {
  const id = docId || nextExtraId(paths), date = retrieved || new Date().toISOString().slice(0, 16).replace('T', ' ') + ' UTC', rel = `text/${id}.txt`;
  if (!/^[A-Za-z]\d+$/.test(id)) throw new Error('文档编号必须是字母加数字');
  writeText(path.join(paths.extra_dir, rel), `SOURCE: ${url}\nRETRIEVED: ${date}\n\n${text.replace(/\r\n?/g, '\n').replace(/^\n+|\n+$/g, '')}\n`);
  const row = [id, jurisdiction, url, sourceType, 'yes', date, '', rel, 'ok'];
  if (!fs.existsSync(paths.extra_manifest)) writeText(paths.extra_manifest, csvRow(MANIFEST_COLUMNS) + '\r\n');
  fs.appendFileSync(paths.extra_manifest, csvRow(row) + '\r\n'); return id;
}
