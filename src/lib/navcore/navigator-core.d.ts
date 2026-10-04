// The original navigator TypeScript is compiled by Vite but typechecked by its
// own project (navigator/tsconfig.json), not by the app's stricter settings.
declare module "navigator-core/*" {
  const mod: any;
  export = mod;
}
