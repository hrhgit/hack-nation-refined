// Runs the original navigator web API (navigator/src/web/server.ts) inside the
// Worker. Long extraction runs in a separate "/run" request kept open by the
// page; a heartbeat file tells other requests the run is still alive.
import "./seed";
import * as nav from "navigator-core/web/server.ts";
import * as lawImportsMod from "navigator-core/web/law-imports.ts";
const ImportError: any = lawImportsMod.ImportError;
import { existsSync, readFileSync, writeFileSync } from "./memfs";
import { flushPersisted, loadPersisted } from "./store.server";

const HEARTBEAT_MS = 10_000, ALIVE_MS = 60_000;
const imports: any = nav.lawImports;
const local: Map<string, Promise<void>> = imports.running;
const beatFile = (id: string) => `${imports.dir}/${id}/heartbeat`;
const beat = (id: string) => writeFileSync(beatFile(id), String(Date.now()));
const alive = (id: string) => {
  if (local.has(id)) return true;
  const f = beatFile(id);
  return existsSync(f) && Date.now() - Number(readFileSync(f, "utf8")) < ALIVE_MS;
};
imports.running = { has: alive, set: (k: string, v: Promise<void>) => local.set(k, v), delete: (k: string) => local.delete(k) };
// The submitting request returns at once; the page then opens /run.
imports.launch = (job: { id: string }) => beat(job.id);

const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" } });

export async function lookup(q: Record<string, string[]>) {
  await loadPersisted();
  return nav.apiLookup(q);
}

async function run(id: string): Promise<Response> {
  const job = imports.read(id);
  if (job.status !== "running" || local.has(id)) return json(409, { error: "当前没有等待执行的提取任务。" });
  beat(id);
  const promise: Promise<void> = imports.extract(job);
  local.set(id, promise);
  const timer = setInterval(() => { beat(id); flushPersisted().catch(() => {}); }, HEARTBEAT_MS);
  const quick = setInterval(() => { flushPersisted().catch(() => {}); }, 1500);
  try { await promise; } finally { clearInterval(timer); clearInterval(quick); local.delete(id); }
  return json(200, imports.detail(id));
}

async function serveImports(request: Request, pathname: string): Promise<Response> {
  try {
    const route = /^\/api\/imports(?:\/([0-9a-f-]{36})(?:\/(apply|retry|preview|run))?)?$/.exec(pathname);
    if (!route) throw new ImportError("提交记录不存在。", 404);
    const [, id, action] = route;
    if (request.method === "GET" && !action) return json(200, id ? imports.detail(id) : imports.list());
    if (request.method !== "POST" || (id && !action)) throw new ImportError("此操作不支持该请求方式。", 405);
    if (request.headers.get("sec-fetch-site") === "cross-site") throw new ImportError("请从本系统页面提交正文。", 403);
    const origin = request.headers.get("origin");
    if (origin) { let o: URL; try { o = new URL(origin); } catch { throw new ImportError("提交来源不正确。", 403); } if (o.host !== new URL(request.url).host) throw new ImportError("请从本系统页面提交正文。", 403); }
    if (action === "run") return await run(id!);
    if (!/^application\/json(?:\s*;|$)/i.test(request.headers.get("content-type") || "")) throw new ImportError("请以正文表单提交。", 415);
    let body: unknown; try { body = await request.json(); } catch { throw new ImportError("提交内容不是有效 JSON。"); }
    const result = !id ? imports.submit(body) : action === "apply" ? imports.apply(id) : action === "retry" ? imports.retry(id) : imports.preview(id);
    return json(!id || action === "retry" ? 202 : 200, result);
  } catch (error) {
    return json(error instanceof ImportError ? (error as any).status : 400, { error: (error as Error).message, disclaimer: "Not legal advice. Based only on the cited sources and the listed address facts." });
  }
}

export async function handle(request: Request): Promise<Response> {
  const url = new URL(request.url);
  try {
    await loadPersisted();
  } catch (e) {
    return json(500, { error: (e as Error).message });
  }
  try {
    if (url.pathname === "/api/imports" || url.pathname.startsWith("/api/imports/")) return await serveImports(request, url.pathname);
    const routes = nav.ROUTES as Record<string, (q: Record<string, string[]>) => unknown>;
    if (request.method !== "GET" || !Object.hasOwn(routes, url.pathname)) return json(404, { error: "Not found" });
    const q: Record<string, string[]> = Object.create(null);
    for (const [k, v] of url.searchParams) if (v) (q[k] ??= []).push(v);
    try { return json(200, routes[url.pathname]!(q)); }
    catch (e) { const err = e as Error; return json(e instanceof nav.NotFound ? 404 : "code" in err ? 500 : 400, { error: err.message }); }
  } finally {
    await flushPersisted().catch((e) => console.error("nav flush failed", e));
  }
}
