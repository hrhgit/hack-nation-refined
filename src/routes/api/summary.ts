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
        // The reader may leave early; generation continues so the result is still cached.
        let open = true;
        const emit = (event: unknown) => {
          if (!open) return;
          try { controller.enqueue(encoder.encode(JSON.stringify(event) + "\n")); } catch { open = false; }
        };
        // Check evidence first so a stale/missing-key error can return a normal JSON status.
        const first: unknown[] = [];
        let started = false;
        let firstEvent!: () => void;
        const gotEvent = new Promise<void>((r) => { firstEvent = r; });
        const work = runSummary(data, language, body.fingerprint, (e) => {
          if (started) emit(e); else { first.push(e); firstEvent(); }
        });
        try {
          await Promise.race([work, gotEvent]);
        } catch (error) {
          if (error instanceof SummaryError) return json({ code: error.code, error: error.message }, error.status);
          return json({ code: "summary_unavailable", error: "Summary unavailable" }, 500);
        }
        started = true;
        first.forEach(emit);
        work.then(() => { if (open) controller.close(); }, (error) => {
          emit({ type: "error", code: error instanceof SummaryError ? error.code : "generation_failed", error: String(error?.message ?? error) });
          if (open) controller.close();
        });
        return new Response(stream, { headers: { "Content-Type": "application/x-ndjson", "Cache-Control": "no-store" } });
      },
    },
  },
});
