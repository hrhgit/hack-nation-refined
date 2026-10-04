import { createFileRoute } from "@tanstack/react-router";

const handle = async ({ request }: { request: Request }) => (await import("@/lib/navcore/core.server")).handle(request);

export const Route = createFileRoute("/api/$")({
  server: { handlers: { GET: handle, POST: handle } },
});
