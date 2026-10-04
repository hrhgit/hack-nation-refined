// Mirrors files under PERSIST_PREFIX between the in-memory filesystem and the
// nav_files table, because the Worker has no durable disk.
import { Buffer } from "node:buffer";
import { PERSIST_PREFIX, dirty, removed, load, drop, listFiles, readRaw } from "./memfs";

const db = async () => (await import("@/integrations/supabase/client.server")).supabaseAdmin;
const inflight = new Set<string>();

export async function loadPersisted(): Promise<void> {
  const client = await db();
  const seen = new Set<string>();
  for (let from = 0; ; from += 1000) {
    const { data, error } = await client.from("nav_files").select("path, content, mtime_ms").like("path", PERSIST_PREFIX + "%").order("path").range(from, from + 999);
    if (error) throw new Error("无法读取已保存的解析记录：" + error.message);
    for (const row of data) {
      seen.add(row.path);
      if (dirty.has(row.path) || inflight.has(row.path) || removed.has(row.path)) continue;
      const mine = readRaw(row.path);
      if (!mine || mine.mtimeMs <= row.mtime_ms) load(row.path, row.content, row.mtime_ms);
    }
    if (data.length < 1000) break;
  }
  for (const p of listFiles(PERSIST_PREFIX)) if (!seen.has(p) && !dirty.has(p) && !inflight.has(p)) drop(p);
}

export async function flushPersisted(): Promise<void> {
  if (!dirty.size && !removed.size) return;
  const client = await db();
  const write = [...dirty], gone = [...removed];
  dirty.clear(); removed.clear(); write.forEach((p) => inflight.add(p));
  try {
    const rows = write.map((p) => { const e = readRaw(p); return e ? { path: p, content: Buffer.from(e.data).toString("utf8"), mtime_ms: e.mtimeMs, updated_at: new Date().toISOString() } : null; }).filter((r): r is NonNullable<typeof r> => r !== null);
    for (let i = 0; i < rows.length; i += 200) {
      const { error } = await client.from("nav_files").upsert(rows.slice(i, i + 200));
      if (error) throw new Error(error.message);
    }
    for (let i = 0; i < gone.length; i += 200) {
      const { error } = await client.from("nav_files").delete().in("path", gone.slice(i, i + 200));
      if (error) throw new Error(error.message);
    }
  } catch (e) {
    write.forEach((p) => { if (!removed.has(p)) dirty.add(p); }); gone.forEach((p) => { if (!dirty.has(p)) removed.add(p); });
    throw e;
  } finally {
    write.forEach((p) => inflight.delete(p));
  }
}
