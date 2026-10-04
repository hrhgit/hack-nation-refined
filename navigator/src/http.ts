import http from 'node:http';
import https from 'node:https';
import {StringDecoder} from 'node:string_decoder';
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

// Same no-timeout/no-truncation policy as request(), with incremental decoding.
export async function requestStream(url: string, body: string, headers: Record<string, string>, onText: (text: string) => void): Promise<void> {
  const u = new URL(url), transport = u.protocol === 'https:' ? https : http;
  if (!['http:', 'https:'].includes(u.protocol)) throw new Error('Unsupported URL protocol');
  const data = Buffer.from(body);
  const response = await new Promise<http.IncomingMessage>((resolve, reject) => {
    const req = transport.request(u, {method: 'POST', headers: {...headers, 'Content-Length': String(data.length)}}, resolve);
    req.on('error', reject); req.end(data);
  });
  const decoder = new StringDecoder('utf8'), status = response.statusCode ?? 500;
  if (status < 200 || status >= 300) {
    let errorBody = '';
    for await (const chunk of response) errorBody += decoder.write(chunk);
    throw new HttpError(status, errorBody + decoder.end());
  }
  if (!response.headers['content-type']?.includes('text/event-stream')) {
    response.destroy(); throw new Error('Expected an event stream');
  }
  for await (const chunk of response) onText(decoder.write(chunk));
  const tail = decoder.end(); if (tail) onText(tail);
}
