import type {Data} from '../types.js';
import {equal, isObject, length, repr} from '../util.js';
const types: Record<string, (v: unknown) => boolean> = {
  string: v => typeof v === 'string', number: v => typeof v === 'number',
  integer: v => typeof v === 'number' && Number.isInteger(v), boolean: v => typeof v === 'boolean',
  array: Array.isArray, object: isObject, null: v => v === null,
};
function typeName(v: unknown): string {return v === null ? 'NoneType' : Array.isArray(v) ? 'list' : isObject(v) ? 'dict' : typeof v === 'string' ? 'str' : typeof v === 'boolean' ? 'bool' : Number.isInteger(v) ? 'int' : 'float';}
export function check(obj: any, schema: Data, p = '$'): string[] {
  const errors: string[] = [], t = schema.type;
  if (t != null) {
    const list: string[] = Array.isArray(t) ? t : [t];
    if (!list.some(x => {if (!Object.hasOwn(types, x)) throw new Error(repr(x)); return types[x](obj);})) return [`${p}: expected ${list.join('/')}, got ${typeName(obj)}`];
  }
  if ('enum' in schema && !schema.enum.some((v: unknown) => equal(v, obj))) errors.push(`${p}: ${repr(obj)} not in ${repr(schema.enum)}`);
  if (typeof obj === 'string') {
    if ('minLength' in schema && length(obj) < schema.minLength) errors.push(`${p}: shorter than ${schema.minLength} characters`);
    if ('pattern' in schema && !new RegExp(schema.pattern).test(obj)) errors.push(`${p}: ${repr(obj)} does not match ${schema.pattern}`);
  }
  if (typeof obj === 'number') {
    if ('minimum' in schema && obj < schema.minimum) errors.push(`${p}: below minimum ${schema.minimum}`);
    if ('maximum' in schema && obj > schema.maximum) errors.push(`${p}: above maximum ${schema.maximum}`);
  }
  if (Array.isArray(obj) && 'items' in schema) obj.forEach((v, i) => errors.push(...check(v, schema.items, `${p}[${i}]`)));
  if (isObject(obj)) {
    for (const k of schema.required ?? []) if (!Object.hasOwn(obj, k)) errors.push(`${p}: missing required field ${repr(k)}`);
    for (const [k, sub] of Object.entries(schema.properties ?? {})) if (Object.hasOwn(obj, k)) errors.push(...check(obj[k], sub as Data, `${p}.${k}`));
  }
  return errors;
}
