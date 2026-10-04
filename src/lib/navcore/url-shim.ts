// The navigator code locates its data relative to its own file; in the Worker
// that data lives in memory under /nav (see seed.ts).
export const fileURLToPath = (_u: unknown): string => "/nav/src/nav/config.js";
export const pathToFileURL = (p: string): URL => new URL("file://" + p);
export default { fileURLToPath, pathToFileURL };
