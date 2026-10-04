import { createFileRoute } from "@tanstack/react-router";
import { runSummary, SummaryError, type SummaryLanguage } from "@/lib/navigator-summary.server";

const json = (body: unknown, status: number) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

export const Route = createFileRoute("/api/summary")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        let body: { query?: Record<string, string>; language?: string; fingerprint?: string };
        try { body = await request.json(); } catch { return json({ code: "bad_request", error: "Invalid JSON" }, 400); }
        const id = body.query?.address_id ?? "";
        const language = (["en", "es", "zh"].includes(body.language ?? "") ? body.language : "en") as SummaryLanguage;
        if (!/^[A-Za-z0-9_-]+$/.test(id) || typeof body.fingerprint !== "string") return json({ code: "bad_request", error: "Invalid query" }, 400);
        const snap = await fetch(new URL(`/navigator/data/lookup/${id}.json`, request.url));
        if (!snap.ok) return json({ code: "not_found", error: "Unknown address" }, 404);
        const data = await snap.json();
        const encoder = new TextEncoder();
        let controller!: ReadableStreamDefaultController<Uint8Array>;
        const stream = new ReadableStream<Uint8Array>({ start(c) { controller = c; } });
        const emit = (event: unknown) => controller.enqueue(encoder.encode(JSON.stringify(event) + "\n"));
        // Check evidence first so a stale/missing-key error can return a normal JSON status.
        const first: unknown[] = [];
        let started = false;
        const work = runSummary(data, language, body.fingerprint, (e) => (started ? emit(e) : first.push(e)));
        try {
          await Promise.race([work, new Promise((r) => setTimeout(r, 0))]);
        } catch (error) {
          if (error instanceof SummaryError) return json({ code: error.code, error: error.message }, error.status);
          return json({ code: "summary_unavailable", error: "Summary unavailable" }, 500);
        }
        started = true;
        first.forEach(emit);
        work.then(() => controller.close(), (error) => {
          emit({ type: "error", code: error instanceof SummaryError ? error.code : "generation_failed", error: String(error?.message ?? error) });
          controller.close();
        });
        return new Response(stream, { headers: { "Content-Type": "application/x-ndjson", "Cache-Control": "no-store" } });
      },
    },
  },
});
