// @lovable.dev/vite-tanstack-config already includes the following — do NOT add them manually
// or the app will break with duplicate plugins:
//   - TanStack devtools (dev-only, first), tanstackStart, viteReact, tailwindcss, tsConfigPaths,
//     nitro (build-only using cloudflare as a default target), VITE_* env injection, @ path alias,
//     React/TanStack dedupe, error logger plugins, and sandbox detection (port/host/strictPort).
// You can pass additional config via defineConfig({ vite: { ... }, etc... }) if needed.
import path from "node:path";
import { defineConfig } from "@lovable.dev/vite-tanstack-config";

const NAV_SRC = path.resolve(__dirname, "navigator/src");
const SHIMS = path.resolve(__dirname, "src/lib/navcore");

// Lets the original navigator code run in the Worker unchanged: its disk and
// http access are redirected to in-memory / fetch-based shims.
const navigatorShims = {
  name: "navigator-shims",
  enforce: "pre" as const,
  resolveId(source: string, importer?: string) {
    if (source.startsWith("navigator-core/")) return path.join(NAV_SRC, source.slice("navigator-core/".length));
    if (!importer || !importer.startsWith(NAV_SRC)) return null;
    if (source === "node:fs" || source === "fs") return path.join(SHIMS, "memfs.ts");
    if (source === "node:url" || source === "url") return path.join(SHIMS, "url-shim.ts");
    if (/(^|\/)http\.js$/.test(source) && path.resolve(path.dirname(importer), source) === path.join(NAV_SRC, "http.js")) return path.join(SHIMS, "http-shim.ts");
    return null;
  },
};

export default defineConfig({
  tanstackStart: {
    // Redirect TanStack Start's bundled server entry to src/server.ts (our SSR error wrapper).
    // nitro/vite builds from this
    server: { entry: "server" },
  },
  vite: { plugins: [navigatorShims] },
});
