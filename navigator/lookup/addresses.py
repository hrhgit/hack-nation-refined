"""Census address matches plus incorporated-place lookup, cached for offline use.

Census address batches only return state/county/tract/block, not legal cities.
Use their matched coordinates to request Incorporated Places separately.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .common import PACK, ROOT, read_json, write_json

BASE_URL = "https://geocoding.geo.census.gov/geocoder"
BENCHMARK = "Public_AR_Current"
VINTAGE = "Current_Current"
STATE_FIPS = {"CA": "06", "NJ": "34", "MA": "25"}


def integer(value, field):
    if value in ("", None):
        return None
    if isinstance(value, bool) or not re.fullmatch(r"\d+", str(value)):
        raise ValueError("%s 必须是非负整数: %r" % (field, value))
    return int(value)


def unit_lower_bound(description):
    """Read explicit unit counts; store conservative lower bounds, not invented totals."""
    text = description.casefold()
    if "five or more apartments" in text:
        return 5
    patterns = [
        r"(\d+)\s*(?:\+|or more)\s*(?:units|apartments)",
        r"(?:apartment\s+)?(\d+)\s*(?:to|-)\s*\d+\s*-?\s*(?:units|unit|apartments)",
        r"(?:apt\s+)(\d+)\s*-\s*\d+\s*units",
        r">\s*(\d+)\s*-?\s*unit",
        r"(?<![a-z\d])(\d+)u(?![a-z\d])",
        r"(\d+)\s+units?\s+or more",
    ]
    bounds = []
    for index, pattern in enumerate(patterns):
        for match in re.finditer(pattern, text):
            bounds.append(int(match.group(1)) + (1 if index == 3 else 0))
    # Multiple explicit buildings (e.g. 7U/24U): no assumption about whether to sum.
    return min(bounds) if bounds else None


def load_addresses(path=PACK / "data" / "sample_addresses.csv"):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    by_id = {}
    for row in rows:
        address_id = row["address_id"]
        if not address_id or address_id in by_id:
            raise ValueError("地址编号为空或重复: %r" % address_id)
        for field in ("year_built", "units"):
            row[field] = integer(row.get(field), field)
        row["units_at_least"] = unit_lower_bound(row.get("use_description", ""))
        by_id[address_id] = row
    return dict(sorted(by_id.items()))


def _multipart(rows):
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    for row in rows:
        writer.writerow([row[k] for k in ("address_id", "street_address", "postal_city", "state", "zip")])
    content = buffer.getvalue().encode("utf-8")
    boundary = "navigator-" + hashlib.sha256(content).hexdigest()
    body = ("--%s\r\nContent-Disposition: form-data; name=\"benchmark\"\r\n\r\n%s\r\n"
            "--%s\r\nContent-Disposition: form-data; name=\"addressFile\"; filename=\"addresses.csv\"\r\n"
            "Content-Type: text/csv\r\n\r\n" % (boundary, BENCHMARK, boundary)).encode()
    body += content + ("\r\n--%s--\r\n" % boundary).encode()
    return body, boundary


def parse_batch(text, expected_ids):
    records = {}
    for row in csv.reader(io.StringIO(text)):
        if not row:
            continue
        address_id = row[0]
        if address_id not in expected_ids or address_id in records or len(row) < 3:
            raise ValueError("Census 批量结果编号重复、未知或格式错误")
        item = {"matched": row[2] == "Match", "match_status": row[2], "raw": row}
        if item["matched"]:
            if len(row) < 6:
                raise ValueError("Census 匹配结果没有坐标")
            longitude, latitude = row[5].split(",")
            item.update(longitude=float(longitude), latitude=float(latitude), matched_address=row[4])
        records[address_id] = item
    if set(records) != set(expected_ids):
        raise ValueError("Census 批量结果没有覆盖所有提交的地址")
    return records


class CensusResolver:
    def __init__(self, cache_dir=ROOT / "work" / "geocode_cache", offline=False,
                 refresh=False, workers=6, base_url=BASE_URL, mode="single"):
        self.cache_dir = Path(cache_dir)
        self.offline, self.refresh, self.workers = offline, refresh, workers
        self.base_url = base_url.rstrip("/")
        self.mode = mode

    def _request(self, request):
        # No application timeout or silent fallback on a network/service error.
        with urllib.request.urlopen(request) as response:
            return response.read().decode("utf-8-sig")

    def _batch(self, rows):
        body, boundary = _multipart(rows)
        key = hashlib.sha256(self.base_url.encode() + body).hexdigest()
        path = self.cache_dir / ("batch-" + key + ".json")
        if path.exists() and not self.refresh:
            raw = read_json(path)["response"]
        else:
            if self.offline:
                raise ValueError("离线缓存缺少地址批量结果；先运行 resolve")
            request = urllib.request.Request(self.base_url + "/locations/addressbatch", data=body,
                                             headers={"Content-Type": "multipart/form-data; boundary=" + boundary})
            raw = self._request(request)
            parse_batch(raw, {r["address_id"] for r in rows})
            write_json(path, {"benchmark": BENCHMARK, "response": raw})
        return parse_batch(raw, {r["address_id"] for r in rows})

    def _place(self, item):
        params = {"x": item["longitude"], "y": item["latitude"], "benchmark": BENCHMARK,
                  "vintage": VINTAGE, "layers": "Incorporated Places", "format": "json"}
        url = self.base_url + "/geographies/coordinates?" + urllib.parse.urlencode(params)
        path = self.cache_dir / ("place-" + hashlib.sha256(url.encode()).hexdigest() + ".json")
        if path.exists() and not self.refresh:
            result = read_json(path)
        else:
            if self.offline:
                raise ValueError("离线缓存缺少城市边界结果；先运行 resolve")
            result = json.loads(self._request(url))
            if "geographies" not in result.get("result", {}):
                raise ValueError("Census 没有返回城市边界资料")
            write_json(path, result)
        return result["result"]["geographies"].get("Incorporated Places", [])

    def _address(self, row):
        params = {k: row[k] for k in ("state", "zip")}
        params.update(street=row["street_address"], city=row["postal_city"], benchmark=BENCHMARK,
                      vintage=VINTAGE, layers="Incorporated Places", format="json")
        url = self.base_url + "/geographies/address?" + urllib.parse.urlencode(params)
        path = self.cache_dir / ("address-" + hashlib.sha256(url.encode()).hexdigest() + ".json")
        if path.exists() and not self.refresh:
            result = read_json(path)
        else:
            if self.offline:
                raise ValueError("离线缓存缺少地址结果；先运行 resolve")
            result = json.loads(self._request(url))
            if not isinstance(result.get("result", {}).get("addressMatches"), list):
                raise ValueError("Census 没有返回地址匹配资料")
            write_json(path, result)
        found = result["result"]["addressMatches"]
        if len(found) != 1:
            return {"matched": False, "match_status": "No_Match" if not found else "Tie"}, []
        match = found[0]
        if "geographies" not in match or "coordinates" not in match:
            raise ValueError("Census 地址结果缺少坐标或边界资料")
        return {"matched": True, "match_status": "Match", "matched_address": match["matchedAddress"],
                "longitude": match["coordinates"]["x"], "latitude": match["coordinates"]["y"]}, match["geographies"].get("Incorporated Places", [])

    def resolve(self, addresses, aliases=None, progress=None):
        if aliases is None:
            aliases = read_json(Path(__file__).with_name("postal_cities.json"))
        rows = list(addresses.values())
        matches, places = {}, {}
        if self.mode == "single":
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                futures = {pool.submit(self._address, row): row["address_id"] for row in rows}
                for future in as_completed(futures):
                    aid = futures[future]
                    matches[aid], places[aid] = future.result()
                    if progress:
                        progress(len(places), len(futures))
        elif self.mode == "batch":
            # Service limit, not a product/data truncation limit: process every batch.
            for start in range(0, len(rows), 10000):
                matches.update(self._batch(rows[start:start + 10000]))
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                futures = {pool.submit(self._place, m): aid for aid, m in matches.items() if m["matched"]}
                for future in as_completed(futures):
                    aid = futures[future]
                    places[aid] = future.result()
                    if progress:
                        progress(len(places), len(futures))
        else:
            raise ValueError("Census 查询方式必须是 single 或 batch")
        resolved = {}
        for aid, row in addresses.items():
            match = matches[aid]
            place_list = places.get(aid, [])
            item = dict(row)
            item.update(legal_city=None, resolved_by="unresolved", jurisdiction_known=False)
            geocode = {k: v for k, v in match.items() if k != "raw"}
            geocode.update(source="census", benchmark=BENCHMARK, vintage=VINTAGE,
                           place_name=None, place_geoid=None)
            if match["matched"] and len(place_list) <= 1:
                if not place_list:
                    # Successfully resolved point outside any incorporated place.
                    item.update(resolved_by="geocoder", jurisdiction_known=True)
                    geocode["note"] = "Census 坐标不在建制市范围内"
                else:
                    place = place_list[0]
                    if place.get("STATE") == STATE_FIPS.get(row["state"]):
                        name = place.get("BASENAME") or re.sub(r" (city|town|borough)$", "", place["NAME"])
                        item.update(legal_city=name + ", " + row["state"], resolved_by="geocoder", jurisdiction_known=True)
                        geocode.update(place_name=place["NAME"], place_geoid=place["GEOID"])
                    else:
                        geocode["note"] = "Census 匹配到了其他州，未采用该城市"
            if not item["jurisdiction_known"]:
                alias = aliases.get(row["state"], {}).get(row["postal_city"].strip().casefold())
                if alias:
                    item.update(legal_city=alias, resolved_by="postal_city_fallback", jurisdiction_known=True)
                    geocode["note"] = "Census 未确定建制市，明确采用邮寄城市对照表"
                else:
                    geocode["note"] = "Census 和邮寄城市对照表均未确定建制市"
            item["geocode"] = geocode
            resolved[aid] = item
        return resolved
