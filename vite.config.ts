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
  resolveId(source: string) {
    if (source.startsWith("navigator-core/")) return path.join(NAV_SRC, source.slice("navigator-core/".length));
    return null;
  },
  // Rewritten in the source text: builtin ids like node:fs skip resolveId in dev SSR.
  transform(code: string, id: string) {
    if (!id.startsWith(NAV_SRC + "/")) return null;
    const out = code
      .replace(/from\s+['"]node:fs['"]/g, `from ${JSON.stringify(path.join(SHIMS, "memfs.ts"))}`)
      .replace(/from\s+['"]node:url['"]/g, `from ${JSON.stringify(path.join(SHIMS, "url-shim.ts"))}`)
      .replace(/from\s+['"](?:\.\.?\/)+http\.js['"]/g, (m) => {
        const rel = m.match(/['"](.*)['"]/)![1];
        return path.resolve(path.dirname(id), rel) === path.join(NAV_SRC, "http.js") ? `from ${JSON.stringify(path.join(SHIMS, "http-shim.ts"))}` : m;
      });
    return out === code ? null : { code: out, map: null };
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
