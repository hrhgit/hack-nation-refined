import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseArgs} from 'node:util';
import type {Data} from './types.js';
export function argumentsFor(argv: string[], strings: string[], booleans: string[] = []): {values: Data; command: string} {
  const options = Object.fromEntries([...strings.map(k => [k, {type: 'string'}]), ...booleans.map(k => [k, {type: 'boolean'}]), ['help', {type: 'boolean', short: 'h'}]]) as any;
  const {values, positionals} = parseArgs({args: argv, options, allowPositionals: true}); if (positionals.length > 1) throw new Error('多余的命令：' + positionals.slice(1).join(' ')); return {values, command: positionals[0] || ''};
}
export const isMain = (url: string): boolean => Boolean(process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(url));
export const integerOption = (v: any, fallback: number): number => {if (v === undefined) return fallback; if (!/^-?\d+$/.test(v)) throw new Error('参数必须是整数：' + v); return Number(v);};
export const onlyOption = (v: any): string[] | undefined => typeof v === 'string' ? v.split(',').map(s => s.trim()).filter(Boolean) : undefined;
export const requireFields = (values: Data, fields: string[]): void => {for (const f of fields) if (!values[f]) throw new Error('缺少参数：--' + f);};
