import fs from 'node:fs';
import path from 'node:path';
import type {Data} from '../types.js';
import {csvRecords, csvRow, parseCsv, pool, pyStr, readJson, repr, setKey, sha256, sortedEntries, writeJson} from '../util.js';
import {request} from '../http.js';
import {ROOT, pack} from './common.js';
export const BASE_URL = 'https://geocoding.geo.census.gov/geocoder', BENCHMARK = 'Public_AR_Current', VINTAGE = 'Current_Current';
export const STATE_FIPS: Record<string, string> = {CA: '06', NJ: '34', MA: '25'};
export function integer(v: unknown, field: string): number | null {if (v === '' || v == null) return null; if (typeof v === 'boolean' || !/^\d+$/.test(pyStr(v))) throw new Error(`${field} 必须是非负整数: ${repr(v)}`); return Number(v);}
export function unitLowerBound(description: string): number | null {
  const s = description.toLowerCase(); if (s.includes('five or more apartments')) return 5;
  const patterns = [/(\d+)\s*(?:\+|or more)\s*(?:units|apartments)/g, /(?:apartment\s+)?(\d+)\s*(?:to|-)\s*\d+\s*-?\s*(?:units|unit|apartments)/g, /(?:apt\s+)(\d+)\s*-\s*\d+\s*units/g, />\s*(\d+)\s*-?\s*unit/g, /(?<![a-z\d])(\d+)u(?![a-z\d])/g, /(\d+)\s+units?\s+or more/g];
  const bounds = patterns.flatMap((p, i) => Array.from(s.matchAll(p), m => +m[1] + (i === 3 ? 1 : 0))); return bounds.length ? Math.min(...bounds) : null;
}
export function loadAddresses(file = path.join(pack(), 'data/sample_addresses.csv')): Data {
  const out: Data = {}; for (const row of csvRecords(fs.readFileSync(file, 'utf8'))) {const id = row.address_id; if (!id || Object.hasOwn(out, id)) throw new Error('地址编号为空或重复: ' + repr(id)); for (const f of ['year_built', 'units']) row[f] = integer(row[f], f); row.units_at_least = unitLowerBound(row.use_description || ''); setKey(out, id, row);} return Object.fromEntries(sortedEntries(out));
}
export function multipart(rows: Data[]): [Buffer, string] {
  const content = rows.map(r => csvRow(['address_id', 'street_address', 'postal_city', 'state', 'zip'].map(k => r[k])) + '\n').join(''), boundary = 'navigator-' + sha256(content);
  return [Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="benchmark"\r\n\r\n${BENCHMARK}\r\n--${boundary}\r\nContent-Disposition: form-data; name="addressFile"; filename="addresses.csv"\r\nContent-Type: text/csv\r\n\r\n${content}\r\n--${boundary}--\r\n`), boundary];
}
export function parseBatch(text: string, ids: Set<string>): Data {
  const records: Data = {};
  for (const row of parseCsv(text)) {
    const id = row[0]; if (!ids.has(id) || Object.hasOwn(records, id) || row.length < 3) throw new Error('Census 批量结果编号重复、未知或格式错误');
    const item: Data = {matched: row[2] === 'Match', match_status: row[2], raw: row};
    if (item.matched) {if (row.length < 6) throw new Error('Census 匹配结果没有坐标'); const coords = row[5].split(','); if (coords.length !== 2) throw new Error(`not enough values to unpack (expected 2, got ${coords.length})`); const [x, y] = coords.map(Number); if (!Number.isFinite(x) || !Number.isFinite(y)) throw new Error('could not convert string to float'); Object.assign(item, {longitude: x, latitude: y, matched_address: row[4]});} setKey(records, id, item);
  }
  if (Object.keys(records).length !== ids.size) throw new Error('Census 批量结果没有覆盖所有提交的地址'); return records;
}
const urlencode = (values: Data): string => Object.entries(values).map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v)).replaceAll('%20', '+').replaceAll("'", '%27').replaceAll('(', '%28').replaceAll(')', '%29').replaceAll('!', '%21')}`).join('&');
export class CensusResolver {
  base_url: string;
  constructor(public cache_dir = path.join(ROOT, 'work/geocode_cache'), public offline = false, public refresh = false, public workers = 6, baseUrl = BASE_URL, public mode = 'single') {this.base_url = baseUrl.replace(/\/+$/, '');}
  private async batch(rows: Data[]): Promise<Data> {
    const [body, boundary] = multipart(rows), file = path.join(this.cache_dir, 'batch-' + sha256(Buffer.concat([Buffer.from(this.base_url), body])) + '.json'); let raw: string;
    if (fs.existsSync(file) && !this.refresh) raw = readJson(file).response;
    else {if (this.offline) throw new Error('离线缓存缺少地址批量结果；先运行 resolve'); raw = await request(this.base_url + '/locations/addressbatch', body, {'Content-Type': 'multipart/form-data; boundary=' + boundary}); parseBatch(raw, new Set(rows.map(r => r.address_id))); writeJson(file, {benchmark: BENCHMARK, response: raw});}
    return parseBatch(raw, new Set(rows.map(r => r.address_id)));
  }
  private async place(item: Data): Promise<Data[]> {
    const float = (n: number): string => Number.isInteger(n) ? n.toFixed(1) : String(n), url = this.base_url + '/geographies/coordinates?' + urlencode({x: float(item.longitude), y: float(item.latitude), benchmark: BENCHMARK, vintage: VINTAGE, layers: 'Incorporated Places', format: 'json'}), file = path.join(this.cache_dir, 'place-' + sha256(url) + '.json'); let result: Data;
    if (fs.existsSync(file) && !this.refresh) result = readJson(file);
    else {if (this.offline) throw new Error('离线缓存缺少城市边界结果；先运行 resolve'); result = JSON.parse(await request(url)); if (!result.result?.geographies) throw new Error('Census 没有返回城市边界资料'); writeJson(file, result);} return result.result.geographies['Incorporated Places'] || [];
  }
  private async address(row: Data): Promise<[Data, Data[]]> {
    const url = this.base_url + '/geographies/address?' + urlencode({state: row.state, zip: row.zip, street: row.street_address, city: row.postal_city, benchmark: BENCHMARK, vintage: VINTAGE, layers: 'Incorporated Places', format: 'json'}), file = path.join(this.cache_dir, 'address-' + sha256(url) + '.json'); let result: Data;
    if (fs.existsSync(file) && !this.refresh) result = readJson(file);
    else {if (this.offline) throw new Error('离线缓存缺少地址结果；先运行 resolve'); result = JSON.parse(await request(url)); if (!Array.isArray(result.result?.addressMatches)) throw new Error('Census 没有返回地址匹配资料'); writeJson(file, result);}
    const found = result.result.addressMatches; if (found.length !== 1) return [{matched: false, match_status: found.length ? 'Tie' : 'No_Match'}, []];
    const match = found[0]; if (!match.geographies || !match.coordinates) throw new Error('Census 地址结果缺少坐标或边界资料');
    return [{matched: true, match_status: 'Match', matched_address: match.matchedAddress, longitude: match.coordinates.x, latitude: match.coordinates.y}, match.geographies['Incorporated Places'] || []];
  }
  async resolve(addresses: Data, aliases = readJson(path.join(ROOT, 'lookup/postal_cities.json')), progress?: (done: number, total: number) => void): Promise<Data> {
    const rows: Data[] = Object.values(addresses), matches: Data = Object.create(null), places: Data = Object.create(null); let done = 0;
    if (this.mode === 'single') await pool(rows, this.workers, async row => {const id = row.address_id; [matches[id], places[id]] = await this.address(row); progress?.(++done, rows.length);});
    else if (this.mode === 'batch') {for (let i = 0; i < rows.length; i += 10000) Object.assign(matches, await this.batch(rows.slice(i, i + 10000))); const selected = Object.entries<Data>(matches).filter(([, m]) => m.matched); await pool(selected, this.workers, async ([id, m]) => {places[id] = await this.place(m); progress?.(++done, selected.length);});}
    else throw new Error('Census 查询方式必须是 single 或 batch');
    const resolved: Data = {};
    for (const [id, row] of Object.entries<Data>(addresses)) {
      const match = matches[id], list: Data[] = places[id] || [], item: Data = {...row, legal_city: null, resolved_by: 'unresolved', jurisdiction_known: false}, geocode: Data = {...Object.fromEntries(Object.entries(match).filter(([k]) => k !== 'raw')), source: 'census', benchmark: BENCHMARK, vintage: VINTAGE, place_name: null, place_geoid: null};
      if (match.matched && list.length <= 1) {
        if (!list.length) {Object.assign(item, {resolved_by: 'geocoder', jurisdiction_known: true}); geocode.note = 'Census 坐标不在建制市范围内';}
        else {const p = list[0]; if (p.STATE === STATE_FIPS[row.state]) {const name = p.BASENAME || p.NAME.replace(/ (city|town|borough)$/, ''); Object.assign(item, {legal_city: name + ', ' + row.state, resolved_by: 'geocoder', jurisdiction_known: true}); Object.assign(geocode, {place_name: p.NAME, place_geoid: p.GEOID});} else geocode.note = 'Census 匹配到了其他州，未采用该城市';}
      }
      if (!item.jurisdiction_known) {const stateAliases = Object.hasOwn(aliases, row.state) ? aliases[row.state] : {}, city = row.postal_city.trim().toLowerCase(), alias = Object.hasOwn(stateAliases, city) ? stateAliases[city] : null; if (alias) {Object.assign(item, {legal_city: alias, resolved_by: 'postal_city_fallback', jurisdiction_known: true}); geocode.note = 'Census 未确定建制市，明确采用邮寄城市对照表';} else geocode.note = 'Census 和邮寄城市对照表均未确定建制市';}
      item.geocode = geocode; setKey(resolved, id, item);
    }
    return resolved;
  }
}
