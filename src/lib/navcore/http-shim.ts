// fetch-based replacement for navigator/src/http.ts (same exports and policy:
// no application timeout, retry or truncation).
export class HttpError extends Error {
  constructor(public status: number, public body: string) { super(`HTTP Error ${status}`); }
}
export async function request(url: string, body?: string | Uint8Array, headers: Record<string, string> = {}): Promise<string> {
  const u = new URL(url);
  if (!["http:", "https:"].includes(u.protocol)) throw new Error("Unsupported URL protocol");
  const res = await fetch(u, { method: body === undefined ? "GET" : "POST", headers, body: body as BodyInit | undefined });
  const text = (await res.text()).replace(/^\uFEFF/, "");
  if (res.status < 200 || res.status >= 300) throw new HttpError(res.status, text);
  return text;
}
export async function requestStream(url: string, body: string, headers: Record<string, string>, onText: (text: string) => void): Promise<void> {
  const u = new URL(url);
  if (!["http:", "https:"].includes(u.protocol)) throw new Error("Unsupported URL protocol");
  const res = await fetch(u, { method: "POST", headers, body });
  if (res.status < 200 || res.status >= 300) throw new HttpError(res.status, await res.text());
  if (!res.headers.get("content-type")?.includes("text/event-stream")) { await res.body?.cancel(); throw new Error("Expected an event stream"); }
  const reader = res.body!.getReader(), decoder = new TextDecoder();
  for (;;) { const { done, value } = await reader.read(); if (done) break; const t = decoder.decode(value, { stream: true }); if (t) onText(t); }
  const rest = decoder.decode(); if (rest) onText(rest);
}
