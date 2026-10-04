import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {readJson, walk} from '../util.js';
import type {Data} from '../types.js';

export const ROOT = path.resolve(process.env.NAV_ROOT ?? path.join(path.dirname(fileURLToPath(import.meta.url)), '../..'));
export const PROJECT = path.dirname(ROOT);
export const PIPELINE_VERSION = '0.1.0';
export const DEFAULT_AS_OF = '2026-10-01';
export const KNOWN_JURISDICTIONS = ['CA', 'NJ', 'MA', 'Los Angeles, CA', 'San Francisco, CA', 'San Diego, CA', 'Berkeley, CA', 'Santa Ana, CA', 'Jersey City, NJ', 'Hoboken, NJ', 'Newark, NJ', 'Boston, MA', 'Cambridge, MA'];
export const STATE_NAMES: Record<string, string> = {california: 'CA', 'new jersey': 'NJ', massachusetts: 'MA'};
export const FALLBACK_CATEGORIES = ['rent_increase_limits', 'just_cause_eviction', 'security_deposits', 'application_screening_fees', 'screening_restrictions', 'algorithmic_rent_setting'];
export const LIFECYCLES = ['enacted', 'pending_bill', 'failed'];
export class Paths {
  constructor(public data_dir: string, public work_dir = path.join(ROOT, 'work'), public out_dir = path.join(ROOT, 'outputs'), public extra_dir = path.join(ROOT, 'corpus_extra')) {}
  get manifest(): string {return path.join(this.data_dir, 'corpus/corpus_manifest.csv');}
  get corpus_dir(): string {return path.join(this.data_dir, 'corpus');}
  get schema_file(): string {return path.join(this.data_dir, 'schema/rule_record.schema.json');}
  get extra_manifest(): string {return path.join(this.extra_dir, 'extra_manifest.csv');}
  get packets_dir(): string {return path.join(this.work_dir, 'packets');}
  get paste_dir(): string {return path.join(this.work_dir, 'paste');}
  get inbox_dir(): string {return path.join(this.work_dir, 'out');}
  get index_file(): string {return path.join(this.work_dir, 'index.json');}
}
export function expand(p: string): string {return p.startsWith('~/') ? path.join(process.env.HOME ?? '', p.slice(2)) : p;}
export function findDataDir(): string {
  if (process.env.NAV_DATA_DIR) return path.resolve(expand(process.env.NAV_DATA_DIR));
  const manifest = walk(path.join(PROJECT, 'starter-pack')).filter(x => x.endsWith('/corpus/corpus_manifest.csv')).sort()[0];
  if (manifest) return path.dirname(path.dirname(manifest));
  throw new Error('Starter pack not found. Set NAV_DATA_DIR to the folder that contains corpus/corpus_manifest.csv');
}
export const defaultPaths = (): Paths => new Paths(findDataDir());
export const loadSchema = (paths: Paths): Data => fs.existsSync(paths.schema_file) ? readJson(paths.schema_file) : {required: [], properties: {category: {enum: FALLBACK_CATEGORIES}}};
export const categories = (schema: Data): string[] => [...(schema.properties?.category?.enum ?? FALLBACK_CATEGORIES)];
