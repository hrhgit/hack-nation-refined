// Bundles the navigator's read-only data into the in-memory filesystem:
// /navigator/<x> becomes /nav/<x>; the starter pack keeps its own folder.
import { load } from "./memfs";

const raw = import.meta.glob(
  [
    "/navigator/work/{rules_enriched,addresses_resolved,index,audit}.json",
    "/navigator/lookup/*.json",
    "/navigator/changes/*.json",
    "/navigator/prompts/**/*",
    "/navigator/corpus_extra/**/*",
    "/starter-pack/*/corpus/**/*",
    "/starter-pack/*/schema/*",
    "/starter-pack/*/dev/*",
    "/starter-pack/*/data/*",
  ],
  { query: "?raw", import: "default", eager: true },
) as Record<string, string>;

for (const [file, text] of Object.entries(raw)) {
  load(file.startsWith("/navigator/") ? "/nav/" + file.slice("/navigator/".length) : file, text, 0);
}
