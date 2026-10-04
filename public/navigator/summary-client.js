import {lineReader} from './summary-shared.js';

export class SummaryRequestError extends Error {
  constructor(code, message) {super(message); this.code = code;}
}

// A separate connection lets the lookup remain interactive while the summary arrives.
export async function receiveSummary({query, language, fingerprint, signal, onEvent}, fetcher = fetch) {
  const response = await fetcher('/api/summary', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, signal,
    body: JSON.stringify({query, language, fingerprint}),
  });
  if (!response.ok) {
    const body = await response.json();
    throw new SummaryRequestError(body.code || 'request_failed', body.error || response.statusText);
  }
  if (!response.body || !response.headers.get('content-type')?.includes('application/x-ndjson')) throw new SummaryRequestError('incomplete', 'Missing summary stream');
  let started = false, terminal = false;
  const lines = lineReader(line => {
    if (!line.trim()) return;
    const event = JSON.parse(line);
    if (terminal) throw new SummaryRequestError('invalid_stream', 'Content after summary completion');
    if (event.type === 'start') {
      if (started || event.fingerprint !== fingerprint) throw new SummaryRequestError('invalid_stream', 'Summary does not match this lookup');
      started = true;
    } else if (!started || !['paragraph', 'complete', 'error'].includes(event.type)) throw new SummaryRequestError('invalid_stream', 'Invalid summary event');
    if (event.type === 'complete' || event.type === 'error') terminal = true;
    if (!signal.aborted) onEvent(event);
  });
  const reader = response.body.getReader(), decoder = new TextDecoder();
  try {
    while (true) {
      signal.throwIfAborted();
      const {value, done} = await reader.read();
      if (done) break;
      lines.push(decoder.decode(value, {stream: true}));
    }
    lines.push(decoder.decode()); lines.end();
    if (!terminal) throw new SummaryRequestError('incomplete', 'Summary stream ended early');
  } finally {
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}
