import http from 'node:http';
import https from 'node:https';
export class HttpError extends Error {constructor(public status: number, public body: string) {super(`HTTP Error ${status}`);}}
// Keep service calls open until the server completes or reports an error. There
// is no application timeout, retry, redirect, or response-length truncation.
export function request(url: string, body?: string | Buffer, headers: Record<string, string> = {}): Promise<string> {
  return new Promise((resolve, reject) => {
    const u = new URL(url), transport = u.protocol === 'https:' ? https : http;
    if (!['http:', 'https:'].includes(u.protocol)) {reject(new Error('Unsupported URL protocol')); return;}
    const data = body === undefined ? undefined : Buffer.isBuffer(body) ? body : Buffer.from(body);
    const req = transport.request(u, {method: data ? 'POST' : 'GET', headers: {...headers, ...(data ? {'Content-Length': String(data.length)} : {})}}, res => {
      const chunks: Buffer[] = []; res.on('data', chunk => chunks.push(Buffer.from(chunk))); res.on('error', reject);
      res.on('end', () => {const text = Buffer.concat(chunks).toString('utf8').replace(/^\uFEFF/, ''), status = res.statusCode ?? 500; status >= 200 && status < 300 ? resolve(text) : reject(new HttpError(status, text));});
    });
    req.on('error', reject); req.end(data);
  });
}
