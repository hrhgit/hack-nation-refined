// In-memory replacement for node:fs used by the original navigator code.
// The Worker has no writable disk, so files live in memory; files under
// PERSIST_PREFIX are mirrored to the database by store.server.ts.
import { Buffer } from "node:buffer";
import path from "node:path";

export const PERSIST_PREFIX = "/nav/work/law_imports/";

type Entry = { data: Buffer; mtimeMs: number };
// Shared through globalThis so every copy of this module sees one filesystem.
type State = { files: Map<string, Entry>; dirs: Set<string>; dirty: Set<string>; removed: Set<string> };
const g = globalThis as unknown as { __navfs?: State };
const state = (g.__navfs ??= { files: new Map(), dirs: new Set(["/"]), dirty: new Set(), removed: new Set() });
const files = state.files;
const dirs = state.dirs;
export const dirty = state.dirty;
export const removed = state.removed;

const norm = (p: string) => path.posix.resolve(String(p));
const persisted = (p: string) => p.startsWith(PERSIST_PREFIX);
let clock = 0;
const tick = () => { const t = Date.now(); clock = t > clock ? t : clock + 0.001; return clock; };

function addDirs(p: string) {
  let d = path.posix.dirname(p);
  while (!dirs.has(d)) { dirs.add(d); d = path.posix.dirname(d); }
}
function mark(p: string, gone: boolean) {
  if (!persisted(p)) return;
  if (gone) { dirty.delete(p); removed.add(p); } else { removed.delete(p); dirty.add(p); }
}
const enoent = (p: string) => Object.assign(new Error(`ENOENT: no such file or directory, '${p}'`), { code: "ENOENT" });

/** Seed or load a file without marking it for persistence. */
export function load(p: string, data: string | Buffer, mtimeMs = Date.now()) {
  p = norm(p); files.set(p, { data: Buffer.isBuffer(data) ? data : Buffer.from(data), mtimeMs }); addDirs(p);
}
export function drop(p: string) {
  p = norm(p); files.delete(p);
  for (let d = path.posix.dirname(p); d.startsWith(PERSIST_PREFIX) && ![...files.keys()].some((k) => k.startsWith(d + "/")); d = path.posix.dirname(d)) dirs.delete(d);
}
export function listFiles(prefix: string): string[] { return [...files.keys()].filter((k) => k.startsWith(prefix)); }
export function readRaw(p: string): Entry | undefined { return files.get(norm(p)); }

function isDir(p: string) {
  if (dirs.has(p)) return true;
  const pre = p.endsWith("/") ? p : p + "/";
  for (const k of files.keys()) if (k.startsWith(pre)) return true;
  return false;
}

export function existsSync(p: string) { p = norm(p); return files.has(p) || isDir(p); }
export function readFileSync(p: string, enc?: any): any {
  const e = files.get(norm(p)); if (!e) throw enoent(p);
  const encoding = typeof enc === "string" ? enc : enc?.encoding;
  return encoding ? e.data.toString(encoding) : Buffer.from(e.data);
}
export function writeFileSync(p: string, data: string | Uint8Array) {
  p = norm(p); files.set(p, { data: typeof data === "string" ? Buffer.from(data) : Buffer.from(data), mtimeMs: tick() }); addDirs(p); mark(p, false);
}
export function appendFileSync(p: string, data: string) {
  const old = files.get(norm(p))?.data ?? Buffer.alloc(0);
  writeFileSync(p, Buffer.concat([old, Buffer.from(data)]));
}
export function mkdirSync(p: string, _o?: unknown) { p = norm(p); dirs.add(p); addDirs(p + "/x"); }
export function renameSync(a: string, b: string) {
  a = norm(a); b = norm(b); const e = files.get(a); if (!e) throw enoent(a);
  files.delete(a); mark(a, true); files.set(b, { data: e.data, mtimeMs: tick() }); addDirs(b); mark(b, false);
}
export function unlinkSync(p: string) { p = norm(p); if (!files.delete(p)) throw enoent(p); mark(p, true); }
export function rmSync(p: string, o: { recursive?: boolean; force?: boolean } = {}) {
  p = norm(p);
  if (files.delete(p)) { mark(p, true); return; }
  if (isDir(p) && o.recursive) {
    const pre = p + "/";
    for (const k of [...files.keys()]) if (k.startsWith(pre)) { files.delete(k); mark(k, true); }
    for (const d of [...dirs]) if (d === p || d.startsWith(pre)) dirs.delete(d);
    return;
  }
  if (!o.force) throw enoent(p);
}
function children(p: string): Map<string, boolean> {
  const pre = p === "/" ? "/" : p + "/", out = new Map<string, boolean>();
  for (const k of files.keys()) if (k.startsWith(pre)) { const rest = k.slice(pre.length), i = rest.indexOf("/"); out.set(i < 0 ? rest : rest.slice(0, i), i < 0 ? false : true); }
  for (const d of dirs) if (d.startsWith(pre) && d !== p) { const rest = d.slice(pre.length), i = rest.indexOf("/"); out.set(i < 0 ? rest : rest.slice(0, i), true); }
  return out;
}
export function readdirSync(p: string, o?: { withFileTypes?: boolean }): any[] {
  p = norm(p); if (!isDir(p)) throw enoent(p);
  const items = [...children(p)].sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
  return o?.withFileTypes ? items.map(([name, dir]) => ({ name, isDirectory: () => dir, isFile: () => !dir })) : items.map(([n]) => n);
}
export function statSync(p: string) {
  p = norm(p); const e = files.get(p);
  if (e) return { isFile: () => true, isDirectory: () => false, mtimeMs: e.mtimeMs, size: e.data.length };
  if (isDir(p)) return { isFile: () => false, isDirectory: () => true, mtimeMs: 0, size: 0 };
  throw enoent(p);
}
export function realpathSync(p: string) { return norm(p); }
export function utimesSync() {}
export function mkdtempSync(prefix: string) { const p = prefix + Math.random().toString(36).slice(2); mkdirSync(p); return p; }

const fs = { existsSync, readFileSync, writeFileSync, appendFileSync, mkdirSync, renameSync, unlinkSync, rmSync, readdirSync, statSync, realpathSync, utimesSync, mkdtempSync };
export default fs;
