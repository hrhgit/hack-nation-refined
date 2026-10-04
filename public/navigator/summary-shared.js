// Used by both the browser and the server. Display timing is not evidence.
export function summaryEvidence(data) {
  const { computed_ms, ...evidence } = data;
  // Match the JSON actually delivered to the browser (including omitted fields).
  return JSON.parse(JSON.stringify(evidence));
}

export function canonicalJson(value) {
  if (Array.isArray(value)) return '[' + value.map(canonicalJson).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map((key) => JSON.stringify(key) + ':' + canonicalJson(value[key])).join(',') + '}';
  }
  return JSON.stringify(value);
}

export async function summaryFingerprint(data) {
  const bytes = new TextEncoder().encode(canonicalJson(summaryEvidence(data)));
  const hash = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(hash)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

// Network chunks need not end on a line (or even on a UTF-8 character).
// Callers decode bytes incrementally before passing text here.
export function lineReader(onLine) {
  let pending = '';
  return {
    push(text) {
      pending += text;
      let end;
      while ((end = pending.indexOf('\n')) !== -1) {
        const line = pending.slice(0, end).replace(/\r$/, '');
        pending = pending.slice(end + 1);
        onLine(line);
      }
    },
    end() {
      if (pending) onLine(pending.replace(/\r$/, ''));
      pending = '';
    },
  };
}
