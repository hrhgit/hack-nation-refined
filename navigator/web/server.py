"""Local web interface over stages B and C; every answer is computed on request from the current files."""
from __future__ import annotations

import argparse
import csv
import json
import mimetypes
import re
import time
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from changes import ChangeTracker
from lookup.common import DEFAULT_DATE, DISCLAIMER, PACK, ROOT, query_date, read_json
from lookup.engine import LookupEngine, load_rules, state_of, status_on

STATIC = Path(__file__).with_name("static")
CATEGORY_ORDER = ["rent_increase_limits", "just_cause_eviction", "security_deposits",
                  "application_screening_fees", "screening_restrictions", "algorithmic_rent_setting"]
RULE_FIELDS = ("team_rule_id", "jurisdiction", "level", "category", "title", "requirement", "key_value",
               "coverage_conditions", "exemptions", "penalty", "interaction", "effective_date", "valid_through",
               "citation", "source_doc_id", "source_url", "quoted_span", "confidence", "conflict_flag",
               "conflict_note", "retrieved", "lifecycle", "packet_id", "date_source")
ADDRESS_FIELDS = ("address_id", "street_address", "postal_city", "legal_city", "state", "zip", "year_built",
                  "units", "units_at_least", "resolved_by")
CONTEXT = 1500


class NotFound(Exception):
    pass


def engine():
    return LookupEngine(load_rules(), read_json(ROOT / "work" / "addresses_resolved.json"))


def documents():
    return read_json(ROOT / "work" / "index.json")["docs"]


def extraction_progress():
    """How much of the corpus the current rule file covers; a partial file must not read as a full answer."""
    counts = read_json(ROOT / "work" / "audit.json")["counts"]
    return {"done": counts["packets_done"], "total": counts["packets_total"]}


def rule_view(rule, as_of, eng, docs):
    view = {field: rule.get(field) for field in RULE_FIELDS}
    view["status"] = status_on(rule, as_of)
    sources = rule.get("sources") or [{"doc_id": rule.get("source_doc_id"), "url": rule.get("source_url"),
                                       "retrieved": rule.get("retrieved"), "quoted_span": rule.get("quoted_span")}]
    view["sources"] = [{"doc_id": s.get("doc_id"), "url": s.get("url"), "retrieved": s.get("retrieved"),
                        "quoted_span": s.get("quoted_span"),
                        "origin": (docs.get(s.get("doc_id")) or {}).get("origin")} for s in sources]
    view["fact_corrections"] = rule.get("overrides_applied") or []
    view["coverage_sources"] = rule.get("coverage_sources", [])
    rid = rule["team_rule_id"]
    view["yields_to"] = [{"team_rule_id": p, "citation": eng.by_id[p]["citation"], "basis": entry["basis"]}
                         for (y, p), entry in sorted(eng.edges.items()) if y == rid]
    view["prevails_over"] = [{"team_rule_id": y, "citation": eng.by_id[y]["citation"], "basis": entry["basis"]}
                             for (y, p), entry in sorted(eng.edges.items()) if p == rid]
    return view


def api_meta(_query):
    addresses = read_json(ROOT / "work" / "addresses_resolved.json")
    return {"disclaimer": DISCLAIMER, "default_date": DEFAULT_DATE, "categories": CATEGORY_ORDER,
            "addresses": [{field: a.get(field) for field in ADDRESS_FIELDS} for _, a in sorted(addresses.items())]}


def api_lookup(query):
    address_id = query.get("address_id", [""])[0]
    as_of = query.get("as_of", [DEFAULT_DATE])[0]
    query_date(as_of)
    rules = load_rules()
    addresses = read_json(ROOT / "work" / "addresses_resolved.json")
    if address_id not in addresses:
        raise NotFound("Unknown address id: %s" % address_id)
    address = dict(addresses[address_id])
    entered = {}
    for field in ("year_built", "units"):
        value = query.get(field, [""])[0]
        if value:
            if not re.fullmatch(r"\d{1,4}", value):
                raise ValueError("%s must be a whole number" % field)
            entered[field] = address[field] = int(value)
    started = time.perf_counter()
    eng = LookupEngine(rules, {address_id: address})
    results, audit = eng.evaluate(address_id, as_of)
    elapsed = round((time.perf_counter() - started) * 1000, 1)
    docs = documents()
    traces = {trace["team_rule_id"]: trace for trace in audit["rules"]}
    rows, left_out = [], []
    for row in results:
        trace = traces[row["team_rule_id"]]
        rows.append(dict(row, rule=rule_view(eng.by_id[row["team_rule_id"]], as_of, eng, docs),
                         steps=trace["steps"], missing_facts=trace.get("missing_facts", [])))
    for rid, trace in sorted(traces.items()):
        # Step 1 is the jurisdiction test; rules of other places are not part of this address's record.
        if trace.get("result") or trace["stopped_at_step"] == 1:
            continue
        left_out.append({"rule": rule_view(eng.by_id[rid], as_of, eng, docs), "steps": trace["steps"],
                         "stopped_at_step": trace["stopped_at_step"]})
    return {"as_of": as_of, "computed_ms": elapsed, "address": address, "entered_facts": entered,
            "results": rows, "left_out": left_out, "conflict_pairs": audit["conflict_pairs"],
            "extraction": extraction_progress(), "disclaimer": DISCLAIMER}


def api_rules(query):
    as_of = query.get("as_of", [DEFAULT_DATE])[0]
    query_date(as_of)
    eng, docs = engine(), documents()
    return {"as_of": as_of, "disclaimer": DISCLAIMER, "extraction": extraction_progress(),
            "rules": [rule_view(rule, as_of, eng, docs) for rule in eng.rules]}


def api_changes(_query):
    eng = engine()
    tracker = ChangeTracker(eng)
    output, audit = tracker.run()
    cities = Counter(a.get("legal_city") or "city not resolved" for a in eng.addresses.values())
    tests = []
    for case in tracker.tests:
        test_id = case["test_id"]
        detail = audit["tests"][test_id]
        transitions = Counter()
        for evidence in detail["evidence"].values():
            if isinstance(evidence, dict):
                for rid in sorted(set(evidence["before"]) | set(evidence["after"])):
                    transitions[(rid, (evidence["before"].get(rid) or [None])[0], (evidence["after"].get(rid) or [None])[0])] += 1
            else:
                for row in evidence:
                    transitions[(row["team_rule_id"], None, row["result"])] += 1
        by_city = Counter(eng.addresses[aid].get("legal_city") or "city not resolved" for aid in output[test_id]["affected_address_ids"])
        flagged = Counter(eng.addresses[aid].get("legal_city") or "city not resolved" for aid in output[test_id]["conflict_flag_address_ids"])
        # A zero matters as much as a count: "neither in Newark" is part of the boundary case.
        states = set(case.get("states") or [])
        if not states:
            states = {state_of(eng.by_id[rid]) for ids in detail["rule_mapping"].values() for rid in ids}
            states |= {eng.addresses[aid]["state"] for aid in output[test_id]["affected_address_ids"]}
        scope = [{"city": city, "total": total, "affected": by_city.get(city, 0), "flagged": flagged.get(city, 0)}
                 for city, total in sorted(cities.items()) if city.rsplit(", ", 1)[-1] in states]
        tests.append({"test": case, "output": output[test_id], "query_dates": detail["query_dates"],
                      "missing_rules": detail["missing_rules"],
                      "rule_mapping": {external: [{"team_rule_id": rid, "citation": eng.by_id[rid]["citation"], "title": eng.by_id[rid].get("title")} for rid in ids]
                                       for external, ids in detail["rule_mapping"].items()},
                      "transitions": [{"team_rule_id": rid, "citation": eng.by_id[rid]["citation"], "before": before, "after": after, "addresses": count}
                                      for (rid, before, after), count in sorted(transitions.items(), key=lambda item: (item[0][0], str(item[0][1]), str(item[0][2])))],
                      "cities": scope})
    return {"tests": tests, "addresses_by_city": dict(sorted(cities.items())), "extraction": extraction_progress(),
            "disclaimer": DISCLAIMER}


def api_pipeline(_query):
    eng, docs = engine(), documents()
    audit = read_json(ROOT / "work" / "audit.json")
    with open(PACK / "corpus" / "corpus_manifest.csv", newline="", encoding="utf-8") as handle:
        manifest = list(csv.DictReader(handle))
    per_doc = Counter()
    for rule in eng.rules:
        for doc_id in {s.get("doc_id") for s in rule.get("sources") or [{"doc_id": rule.get("source_doc_id")}]}:
            per_doc[doc_id] += 1
    lookups, _ = eng.all(DEFAULT_DATE)
    return {"as_of": DEFAULT_DATE, "disclaimer": DISCLAIMER,
            "extraction": dict(audit["counts"], ran_at=audit["ran_at"], pipeline_version=audit["pipeline_version"]),
            "corpus": {"manifest_documents": len(manifest), "manifest_with_text": sum(1 for row in manifest if row["text_file"]),
                       "indexed_documents": len(docs), "indexed_with_text": sum(1 for d in docs.values() if not d.get("no_text")),
                       "added_documents": sum(1 for d in docs.values() if d.get("origin") != "starter")},
            "rules": {"total": len(eng.rules), "by_status": dict(Counter(status_on(rule, DEFAULT_DATE) for rule in eng.rules)),
                      "precedence_links": len(eng.edges)},
            "addresses": {"total": len(eng.addresses), "resolved_by": dict(Counter(a.get("resolved_by") for a in eng.addresses.values()))},
            "lookups": dict(Counter(row["result"] for rows in lookups["lookups"].values() for row in rows)),
            "documents": [{"doc_id": doc_id, "jurisdictions": d.get("jurisdictions"), "url": d.get("url"), "source_type": d.get("source_type"),
                           "origin": d.get("origin"), "no_text": bool(d.get("no_text")), "packets": len(d.get("packets") or []),
                           "rules": per_doc.get(doc_id, 0)} for doc_id, d in sorted(docs.items())]}


def api_source(query):
    """Locate one quoted span inside the saved source text, so a reader can check it against the original."""
    doc_id = query.get("doc_id", [""])[0]
    quote = query.get("quote", [""])[0]
    if not re.fullmatch(r"[A-Z]\d{3}", doc_id):
        raise ValueError("doc_id must look like D024")
    doc = documents().get(doc_id)
    if doc is None:
        raise NotFound("Unknown document: %s" % doc_id)
    starter = doc.get("origin") == "starter"
    path = (PACK / "corpus" if starter else ROOT / "corpus_extra") / "text" / (doc_id + ".txt")
    if not path.exists():
        raise NotFound("No saved text for %s" % doc_id)
    text = path.read_text(encoding="utf-8")
    header = dict(line.split(": ", 1) for line in text.splitlines()[:2] if ": " in line)
    payload = {"doc_id": doc_id, "origin": doc.get("origin"), "url": header.get("SOURCE") or doc.get("url"),
               "retrieved": header.get("RETRIEVED"), "jurisdictions": doc.get("jurisdictions"),
               "characters": len(text), "found": False}
    tokens = quote.split()
    if tokens:
        # The saved pages wrap lines differently from the quote; only whitespace is allowed to differ.
        match = re.search(r"\s+".join(re.escape(token) for token in tokens), text)
        if match:
            payload.update(found=True, offset=match.start(), before=text[max(0, match.start() - CONTEXT):match.start()],
                           match=match.group(0), after=text[match.end():match.end() + CONTEXT])
    return payload


ROUTES = {"/api/meta": api_meta, "/api/lookup": api_lookup, "/api/rules": api_rules,
          "/api/changes": api_changes, "/api/pipeline": api_pipeline, "/api/source": api_source}


class Handler(BaseHTTPRequestHandler):
    server_version = "HousingLawNavigator/0.1"

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status, value):
        self._send(status, json.dumps(value, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in ROUTES:
            try:
                self._json(200, ROUTES[url.path](parse_qs(url.query)))
            except NotFound as error:
                self._json(404, {"error": str(error), "disclaimer": DISCLAIMER})
            except ValueError as error:
                self._json(400, {"error": str(error), "disclaimer": DISCLAIMER})
            return
        name = "index.html" if url.path == "/" else url.path.lstrip("/")
        target = (STATIC / name).resolve()
        if STATIC.resolve() not in target.parents or not target.is_file():
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        self._send(200, target.read_bytes(), (mimetypes.guess_type(target.name)[0] or "application/octet-stream") + "; charset=utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="地址查询网页；" + DISCLAIMER)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print("网页已启动：http://%s:%s  （按 Ctrl+C 停止）%s" % (args.host, args.port, DISCLAIMER), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0
