import type {Data} from '../types.js';
import {isObject, slice} from '../util.js';
export function classify(obj: Data): 'record' | 'receipt' | 'other' {
  if ('category' in obj || 'quoted_span' in obj) return 'record';
  return 'packet_id' in obj && 'n_rules' in obj ? 'receipt' : 'other';
}
function braceEnd(text: string, start: number): number | null {
  let depth = 0, inString = false, escaped = false;
  for (let j = start; j < text.length; j++) {
    const ch = text[j];
    if (inString) {
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === '"') inString = false;
    } else if (ch === '"') inString = true;
    else if (ch === '{') depth++;
    else if (ch === '}' && --depth === 0) return j;
  }
  return null;
}
export function extractJsonObjects(text: string): [Data[], string[]] {
  const objects: Data[] = [], problems: string[] = []; let suspect: string | null = null, i = 0;
  while (i < text.length) {
    if (text[i] !== '{') {i++; continue;}
    const end = braceEnd(text, i);
    if (end === null) {
      const tail = text.slice(i);
      if (suspect === null && (slice(tail, 0, 3000).includes('"category"') || slice(tail, 0, 400).includes('"packet_id"'))) suspect = slice(tail, 0, 120).replaceAll('\n', ' ');
      i++; continue;
    }
    const chunk = text.slice(i, end + 1); let obj: unknown;
    try {obj = JSON.parse(chunk);} catch {
      try {obj = JSON.parse(chunk.replace(/,\s*([}\]])/g, '$1'));} catch {obj = null;}
    }
    if (isObject(obj)) {objects.push(obj); if (classify(obj) !== 'other') suspect = null; i = end + 1;}
    else {if (chunk.includes('"category"') || chunk.includes('"quoted_span"')) problems.push('unparseable JSON object near: ' + slice(chunk, 0, 120).replaceAll('\n', ' ')); i++;}
  }
  if (suspect !== null) problems.push('truncated JSON object (answer cut off?) near: ' + suspect);
  return [objects, problems];
}
