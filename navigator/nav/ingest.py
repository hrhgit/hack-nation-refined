"""Parse model answers, validate every record against the source, merge, and write the outputs.

Everything here is deterministic: the same files in work/out/ always give the same rules.json.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import facts, schema as jschema
from .config import KNOWN_JURISDICTIONS, LIFECYCLES, PIPELINE_VERSION, STATE_NAMES, Paths, categories, load_schema
from .corpus import Doc, load_corpus
from .keywords import score_text
from .packets import load_index
from .parse import classify, extract_json_objects
from .spans import DocIndex

NULLISH = {"", "null", "none", "n/a", "na", "unknown", "not stated", "not specified", "not applicable", "-"}
APPL_KEYS = ["built_on_or_before", "built_after", "date_basis", "min_units", "max_units", "owner_dependent", "other"]
DATE_BASES = {"certificate_of_occupancy", "construction_date", "unspecified"}
LIFECYCLE_ALIASES = {
    "in_force": "enacted", "in force": "enacted", "effective": "enacted", "law": "enacted", "adopted": "enacted",
    "pending": "pending_bill", "bill": "pending_bill", "proposed": "pending_bill",
    "struck": "failed", "defeated": "failed", "vetoed": "failed", "withdrawn": "failed",
}
SCHEMA_ORDER = [
    "team_rule_id", "jurisdiction", "level", "category", "status", "title", "requirement", "key_value",
    "coverage_conditions", "exemptions", "overrides", "interaction", "effective_date", "citation",
    "source_doc_id", "source_url", "quoted_span", "confidence", "conflict_flag", "conflict_note",
]
MAX_SPAN_CHARS = 1200


def _val(v: Any) -> Any:
    if isinstance(v, str):
        v = v.strip()
        return None if v.lower() in NULLISH else v
    return v


def _to_bool(v: Any) -> Optional[bool]:
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.strip().lower() in ("true", "false"):
        return v.strip().lower() == "true"
    if v is None:
        return False
    return None


def source_priority(doc: Optional[Doc]) -> int:
    st = (doc.source_type if doc else "").lower()
    if "city-linked" in st:
        return 2
    if "official" in st or "code publisher" in st:
        return 3
    return 1


# ---------------------------------------------------------------- record validation

class Validator:
    def __init__(self, docs: Dict[str, Doc], index: Dict, schema: Dict[str, Any], as_of: str):
        self.docs, self.index, self.schema, self.as_of = docs, index, schema, as_of
        self.cats = categories(schema)
        self._idx: Dict[str, DocIndex] = {}
        self._dates: Dict[str, set] = {}
        self._nums: Dict[str, set] = {}
        self._scores: Dict[str, Dict[str, int]] = {}

    def doc_index(self, doc_id: str) -> DocIndex:
        if doc_id not in self._idx:
            self._idx[doc_id] = DocIndex(self.docs[doc_id].body)
        return self._idx[doc_id]

    def dates(self, doc_id: str):
        if doc_id not in self._dates:
            self._dates[doc_id] = facts.doc_dates(self.docs[doc_id].body)
        return self._dates[doc_id]

    def nums(self, doc_id: str):
        if doc_id not in self._nums:
            self._nums[doc_id] = facts.numbers_in(self.docs[doc_id].body)
        return self._nums[doc_id]

    def scores(self, doc_id: str):
        if doc_id not in self._scores:
            self._scores[doc_id] = score_text(self.docs[doc_id].body)
        return self._scores[doc_id]

    def check(self, raw: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], List[str], List[str]]:
        """Return (rule, errors, warnings). rule is None when errors is non-empty."""
        errors: List[str] = []
        warns: List[str] = []
        # API/model JSON is untrusted. Reject wrong field types before string helpers run,
        # so the saved answer can be corrected rather than breaking every later ingest.
        for k in ("packet_id", "doc_id", "jurisdiction", "category", "lifecycle", "title",
                  "requirement", "citation", "quoted_span", "effective_date", "key_value",
                  "coverage_conditions", "exemptions", "penalty", "interaction", "conflict_note"):
            if raw.get(k) is not None and not isinstance(raw[k], str):
                errors.append("%s must be text or null" % k)
        if isinstance(raw.get("applicability"), dict):
            for k in ("built_on_or_before", "built_after", "date_basis", "other"):
                v = raw["applicability"].get(k)
                if v is not None and not isinstance(v, str):
                    errors.append("applicability.%s must be text or null" % k)
        if errors:
            return None, errors, warns
        g = lambda k: _val(raw.get(k))

        pid, did = g("packet_id"), g("doc_id")
        if pid not in self.index["packets"]:
            return None, ["unknown packet_id %r" % pid], []
        pdoc = self.index["packets"][pid]["doc_id"]
        if did and did != pdoc:
            errors.append("doc_id %r does not match packet %s (document %s)" % (did, pid, pdoc))
        doc = self.docs.get(pdoc)
        if doc is None or not doc.has_text:
            return None, ["document %s has no text" % pdoc], []

        for k in ("jurisdiction", "category", "lifecycle", "title", "requirement", "citation", "quoted_span"):
            if not g(k):
                errors.append("missing %s" % k)

        category = (g("category") or "").lower().replace("-", "_").replace(" ", "_")
        if category and category not in self.cats:
            errors.append("category %r is not one of %s" % (g("category"), ", ".join(self.cats)))

        lifecycle = (g("lifecycle") or "").lower()
        lifecycle = LIFECYCLE_ALIASES.get(lifecycle, lifecycle)
        if lifecycle and lifecycle not in LIFECYCLES:
            errors.append("lifecycle %r must be enacted, pending_bill or failed" % g("lifecycle"))
        elif lifecycle and g("lifecycle").lower() != lifecycle:
            warns.append("lifecycle %r read as %r" % (g("lifecycle"), lifecycle))

        jur = facts.normalize_jurisdiction(g("jurisdiction") or "", KNOWN_JURISDICTIONS, STATE_NAMES) \
            if g("jurisdiction") else None
        if g("jurisdiction") and not jur:
            errors.append("jurisdiction %r must be a state code or 'City, ST'" % g("jurisdiction"))
        elif jur and jur not in KNOWN_JURISDICTIONS:
            warns.append("jurisdiction %r is outside the challenge scope" % jur)

        eff = g("effective_date")
        if eff is not None:
            norm = facts.normalize_date(eff)
            if norm is None:
                errors.append("effective_date %r is not a date (use YYYY-MM-DD, YYYY-MM or YYYY)" % eff)
            else:
                if norm != eff:
                    warns.append("effective_date %r rewritten as %s" % (eff, norm))
                eff = norm
                if not facts.date_supported(eff, self.dates(pdoc)):
                    warns.append("effective_date %s does not appear in %s: check it" % (eff, pdoc))

        span = None
        span_note = None
        raw_span = g("quoted_span")
        if raw_span and "[[omitted" in raw_span:
            errors.append("quoted_span crosses an omitted section: quote one contiguous passage")
        elif raw_span:
            m = self.doc_index(pdoc).locate(raw_span)
            if m is None:
                errors.append("quoted_span not found in %s (not verbatim): copy the sentence exactly" % pdoc)
            elif len(m.text) < 20:
                errors.append("quoted_span is shorter than 20 characters")
            else:
                span = m.text
                if m.method != "exact":
                    span_note = "quoted_span realigned to the source (%s match, %.2f)" % (m.method, m.score)
                    warns.append(span_note)
                if len(span) > MAX_SPAN_CHARS:
                    warns.append("quoted_span is %d characters long" % len(span))

        citation = facts.normalize_citation(g("citation") or "")
        if g("citation") and not citation:
            errors.append("citation is empty after cleanup")

        conf = raw.get("confidence")
        if conf is None:
            warns.append("no confidence given")
        else:
            try:
                conf = max(0.0, min(1.0, float(conf)))
            except (TypeError, ValueError):
                warns.append("confidence %r is not a number" % conf)
                conf = None

        cf = _to_bool(raw.get("conflict_flag"))
        if cf is None:
            warns.append("conflict_flag %r read as false" % raw.get("conflict_flag"))
            cf = False

        key_value = g("key_value")
        if key_value:
            bad = facts.unsupported_numbers(str(key_value), self.nums(pdoc))
            if bad:
                warns.append("key_value numbers not found in %s: %s" % (pdoc, ", ".join(bad)))
        if category in self.cats and self.scores(pdoc).get(category, 0) == 0:
            warns.append("%s never mentions anything about %s" % (pdoc, category))
        if jur and doc.jurisdictions:
            dj = doc.jurisdictions.strip()
            same_state = facts.state_of(jur) == facts.state_of(dj) and facts.level_of(jur) == "state"
            if jur.lower() != dj.lower() and not same_state:
                warns.append("rule jurisdiction %s differs from document jurisdiction %s" % (jur, dj))
        if raw.get("status") and lifecycle in LIFECYCLES:
            derived = facts.derive_status(lifecycle, eff if eff and facts.ISO_ANY.match(eff) else None, self.as_of)
            if str(raw["status"]).lower() != derived:
                warns.append("model said status %r, derived %r" % (raw["status"], derived))
        if lifecycle == "enacted" and re.fullmatch(r"(?:[SH]\.?\s?\d{3,5}|[AS]B\s?\d+)", citation or "") and not eff:
            warns.append("citation looks like a bill number but lifecycle is enacted: confirm it was signed")

        if errors:
            return None, errors, warns

        rule: Dict[str, Any] = OrderedDict()
        rule["jurisdiction"] = jur
        rule["level"] = facts.level_of(jur)
        rule["category"] = category
        rule["lifecycle"] = lifecycle
        rule["status"] = facts.derive_status(lifecycle, eff, self.as_of)
        rule["title"] = g("title")
        rule["requirement"] = g("requirement")
        rule["key_value"] = key_value
        rule["coverage_conditions"] = g("coverage_conditions")
        rule["applicability"] = self._applicability(raw.get("applicability"), warns)
        rule["exemptions"] = g("exemptions")
        rule["penalty"] = g("penalty")
        rule["overrides"] = []
        rule["interaction"] = g("interaction")
        rule["effective_date"] = eff
        rule["citation"] = citation
        rule["source_doc_id"] = pdoc
        rule["source_url"] = doc.url
        rule["retrieved"] = doc.retrieved
        rule["quoted_span"] = span
        rule["confidence"] = conf
        rule["conflict_flag"] = cf
        rule["conflict_note"] = g("conflict_note")
        rule["packet_id"] = pid
        rule["warnings"] = warns

        bad = jschema.check(to_schema_record(rule, "r-0000"), self.schema)
        if bad:
            return None, ["schema: " + b for b in bad], warns
        return rule, [], warns

    @staticmethod
    def _applicability(a: Any, warns: List[str]) -> Dict[str, Any]:
        out: Dict[str, Any] = {k: None for k in APPL_KEYS}
        out["owner_dependent"] = False
        if a is None:
            return out
        if not isinstance(a, dict):
            warns.append("applicability is not an object: ignored")
            return out
        for k in ("built_on_or_before", "built_after"):
            v = _val(a.get(k))
            if v is not None:
                nd = facts.normalize_date(str(v))
                if nd is None:
                    warns.append("applicability.%s %r is not a date: ignored" % (k, v))
                out[k] = nd
        v = _val(a.get("date_basis"))
        out["date_basis"] = v if v in DATE_BASES else None
        for k in ("min_units", "max_units"):
            v = _val(a.get(k))
            if v is not None:
                try:
                    out[k] = int(v)
                except (TypeError, ValueError):
                    warns.append("applicability.%s %r is not an integer: ignored" % (k, v))
        ob = _to_bool(a.get("owner_dependent"))
        out["owner_dependent"] = bool(ob)
        out["other"] = _val(a.get("other"))
        return out


def to_schema_record(rule: Dict[str, Any], rule_id: str) -> Dict[str, Any]:
    full = dict(rule)
    full["team_rule_id"] = rule_id
    return OrderedDict((k, full.get(k)) for k in SCHEMA_ORDER)


# ---------------------------------------------------------------- merging

def _merge_group(group: List[Dict[str, Any]], docs: Dict[str, Doc]) -> Tuple[Dict[str, Any], List[str]]:
    group = sorted(group, key=lambda r: (-source_priority(docs.get(r["source_doc_id"])),
                                          -(r["confidence"] or 0), -len(r["quoted_span"]), r["source_doc_id"]))
    primary = dict(group[0])
    primary["warnings"] = list(primary["warnings"])
    sources = [{"doc_id": r["source_doc_id"], "url": r["source_url"], "retrieved": r["retrieved"],
                "quoted_span": r["quoted_span"], "effective_date": r["effective_date"],
                "key_value": r["key_value"], "lifecycle": r["lifecycle"]} for r in group]
    notes: List[str] = []
    for r in group[1:]:
        for f in ("key_value", "coverage_conditions", "exemptions", "penalty", "interaction", "effective_date"):
            if primary.get(f) is None and r.get(f) is not None:
                primary[f] = r[f]
        if primary["applicability"] == Validator._applicability(None, []) and r["applicability"] != primary["applicability"]:
            primary["applicability"] = r["applicability"]
        for w in r["warnings"]:
            if w not in primary["warnings"]:
                primary["warnings"].append(w)
    pairs = [(a, b) for i, a in enumerate(group) for b in group[i + 1:]]
    for a, b in pairs:
        if a["effective_date"] and b["effective_date"] and a["effective_date"] != b["effective_date"]:
            notes.append("effective_date: %s says %s, %s says %s" % (a["source_doc_id"], a["effective_date"],
                                                                      b["source_doc_id"], b["effective_date"]))
        sa, sb = facts.numeric_signature(a["key_value"]), facts.numeric_signature(b["key_value"])
        if sa and sb and sa != sb:
            notes.append("key_value: %s says %r, %s says %r" % (a["source_doc_id"], a["key_value"],
                                                                 b["source_doc_id"], b["key_value"]))
        if a["lifecycle"] != b["lifecycle"]:
            notes.append("lifecycle: %s says %s, %s says %s" % (a["source_doc_id"], a["lifecycle"],
                                                                 b["source_doc_id"], b["lifecycle"]))
    notes = sorted(set(notes))
    if notes:
        primary["conflict_flag"] = True
        extra = "Sources disagree: " + "; ".join(notes)
        primary["conflict_note"] = (primary["conflict_note"] + " | " + extra) if primary["conflict_note"] else extra
    primary["sources"] = sources
    primary["merged_from"] = len(group)
    return primary, notes


def _group_key(r: Dict[str, Any]) -> Tuple[str, str, str]:
    return (r["jurisdiction"], r["category"], facts.citation_key(r["citation"]))


# ---------------------------------------------------------------- results

@dataclass
class PacketResp:
    records: List[Dict[str, Any]] = field(default_factory=list)
    receipt: Optional[Dict[str, Any]] = None
    rejected: int = 0
    accepted: int = 0
    file: str = ""


@dataclass
class IngestResult:
    as_of: str
    files: List[Dict[str, Any]]
    parse_problems: List[Tuple[str, str]]
    rules: List[Dict[str, Any]]
    rejected: List[Dict[str, Any]]
    states: "OrderedDict[str, Dict[str, Any]]"
    conflicts: List[Tuple[str, List[str]]]
    near_duplicates: List[Tuple[str, str, str]]
    counts: Dict[str, int]
    problems: Dict[str, List[str]]
    matrix_extra: List[str] = field(default_factory=list)


def list_inbox(paths: Paths) -> List[Path]:
    items = [p for p in paths.inbox_dir.rglob("*")
             if p.is_file() and not p.name.startswith((".", "_")) and p.suffix.lower() in {".txt", ".md", ".json", ".jsonl"}]
    return sorted(items, key=lambda p: (p.stat().st_mtime, p.name))


def run_ingest(paths: Paths, as_of: Optional[str] = None, persist_ids: bool = True) -> IngestResult:
    index = load_index(paths)
    as_of = as_of or index["as_of"]
    docs = load_corpus(paths)
    schema = load_schema(paths)
    val = Validator(docs, index, schema, as_of)
    docs_packets: Dict[str, List[str]] = defaultdict(list)
    for pid, meta in index["packets"].items():
        docs_packets[meta["doc_id"]].append(pid)

    files_meta: List[Dict[str, Any]] = []
    parse_problems: List[Tuple[str, str]] = []
    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    latest: Dict[str, PacketResp] = {}
    n_records = 0

    for f in list_inbox(paths):
        data = f.read_bytes()
        text = data.decode("utf-8", errors="replace")
        objs, problems = extract_json_objects(text)
        files_meta.append({"name": str(f.relative_to(paths.inbox_dir)), "sha256": hashlib.sha256(data).hexdigest(),
                           "bytes": len(data), "objects": len(objs)})
        parse_problems += [(f.name, p) for p in problems]
        resp: Dict[str, PacketResp] = {}
        for obj in objs:
            kind = classify(obj)
            if kind == "other":
                continue
            pid = _val(obj.get("packet_id"))
            if kind == "record" and (not pid) and _val(obj.get("doc_id")) in docs_packets \
                    and len(docs_packets[_val(obj.get("doc_id"))]) == 1:
                pid = docs_packets[_val(obj.get("doc_id"))][0]
                obj["packet_id"] = pid
            bucket = resp.setdefault(pid or "?", PacketResp(file=f.name))
            if kind == "receipt":
                bucket.receipt = obj
                continue
            n_records += 1
            bucket.records.append(obj)
            rule, errs, warns = val.check(obj)
            if errs:
                bucket.rejected += 1
                rejected.append({"file": f.name, "packet_id": pid, "reasons": errs, "record": obj})
            else:
                bucket.accepted += 1
                rule["_file"] = f.name
                accepted.append(rule)
        for pid, r in resp.items():
            if pid in index["packets"]:
                latest[pid] = r

    for rj in rejected:  # a rejection is open only while it belongs to the packet's latest answer
        cur = latest.get(rj["packet_id"])
        rj["open"] = bool(cur and cur.file == rj["file"])

    states: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
    problems: Dict[str, List[str]] = {}
    for pid in index["packets"]:
        r = latest.get(pid)
        if r is None:
            states[pid] = {"state": "pending", "detail": "no answer yet"}
            problems[pid] = []
            continue
        msgs: List[str] = []
        if r.receipt is None:
            st, detail = "incomplete", "no receipt line (answer probably cut off)"
            msgs.append("no receipt line was found; the answer was probably cut off. Re-emit the records and the receipt")
        elif r.receipt.get("n_rules") != len(r.records):
            st = "mismatch"
            detail = "receipt says %s record(s), %d parsed" % (r.receipt.get("n_rules"), len(r.records))
            msgs.append("receipt n_rules=%s but %d records were parsed" % (r.receipt.get("n_rules"), len(r.records)))
        elif r.rejected:
            st, detail = "needs_fix", "%d record(s) rejected" % r.rejected
        else:
            st, detail = "done", "%d rule(s)" % r.accepted
        if r.rejected:
            for rj in rejected:
                if rj["packet_id"] == pid and rj["file"] == r.file:
                    rec = rj["record"]
                    msgs.append("record '%s' (%s): %s" % (str(rec.get("title"))[:60], str(rec.get("citation"))[:50],
                                                          "; ".join(rj["reasons"])))
        states[pid] = {"state": st, "detail": detail, "file": r.file}
        problems[pid] = msgs if st != "done" else []

    # merge accepted records by provision
    groups: "OrderedDict[Tuple[str, str, str], List[Dict[str, Any]]]" = OrderedDict()
    for r in accepted:
        groups.setdefault(_group_key(r), []).append(r)
    merged: List[Dict[str, Any]] = []
    conflicts: List[Tuple[str, List[str]]] = []
    for key, grp in groups.items():
        m, notes = _merge_group(grp, docs)
        merged.append(m)
        if notes:
            conflicts.append((" / ".join(key[:2]) + " " + m["citation"], notes))

    cat_order = categories(schema)
    merged.sort(key=lambda r: (0 if r["level"] == "state" else 1, r["jurisdiction"],
                               cat_order.index(r["category"]) if r["category"] in cat_order else 99, r["citation"]))

    near: List[Tuple[str, str, str]] = []
    for i, a in enumerate(merged):
        for b in merged[i + 1:]:
            if a["jurisdiction"] == b["jurisdiction"] and a["category"] == b["category"]:
                ta, tb = facts.key_tokens(facts.citation_key(a["citation"])), facts.key_tokens(facts.citation_key(b["citation"]))
                if ta and tb and ta & tb and ta != tb:
                    near.append((a["jurisdiction"] + " / " + a["category"], a["citation"], b["citation"]))

    reg = _assign_ids(paths, merged, persist_ids)
    counts = {
        "files": len(files_meta), "records_parsed": n_records, "accepted": len(accepted),
        "rejected": sum(1 for r in rejected if r["open"]), "rejected_fixed": sum(1 for r in rejected if not r["open"]),
        "rules": len(merged),
        "packets_total": len(index["packets"]),
        "packets_done": sum(1 for s in states.values() if s["state"] == "done"),
    }
    return IngestResult(as_of, files_meta, parse_problems, merged, rejected, states, conflicts, near, counts, problems,
                        matrix_extra=[])


def _assign_ids(paths: Paths, rules: List[Dict[str, Any]], persist: bool = True) -> Dict[str, str]:
    """Stable ids: a provision keeps its id across re-runs, so lookups.json never drifts."""
    reg_file = paths.work_dir / "id_registry.json"
    reg = json.loads(reg_file.read_text(encoding="utf-8")) if reg_file.exists() else {"next": 1, "ids": {}}
    for r in rules:
        key = "|".join(_group_key(r))
        if key not in reg["ids"]:
            reg["ids"][key] = "r-%04d" % reg["next"]
            reg["next"] += 1
        r["team_rule_id"] = reg["ids"][key]
    if persist:
        reg_file.write_text(json.dumps(reg, indent=1, ensure_ascii=False), encoding="utf-8")
    return reg["ids"]


# ---------------------------------------------------------------- outputs

def write_outputs(paths: Paths, res: IngestResult, rules_format: str = "wrapped") -> Dict[str, str]:
    from .report import render_report

    paths.out_dir.mkdir(parents=True, exist_ok=True)
    paths.work_dir.mkdir(parents=True, exist_ok=True)
    records = [to_schema_record(r, r["team_rule_id"]) for r in res.rules]
    payload: Any = {"rules": records} if rules_format == "wrapped" else records
    (paths.out_dir / "rules.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    enriched = []
    for r in res.rules:
        e = OrderedDict(to_schema_record(r, r["team_rule_id"]))
        for k in ("lifecycle", "applicability", "penalty", "retrieved", "packet_id", "warnings", "sources", "merged_from"):
            e[k] = r.get(k)
        e["as_of"] = res.as_of
        enriched.append(e)
    (paths.work_dir / "rules_enriched.json").write_text(json.dumps(enriched, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with (paths.work_dir / "rejected.jsonl").open("w", encoding="utf-8") as fh:
        for rj in res.rejected:
            fh.write(json.dumps(rj, ensure_ascii=False) + "\n")
    (paths.work_dir / "problems.json").write_text(json.dumps(res.problems, indent=1, ensure_ascii=False), encoding="utf-8")
    (paths.work_dir / "report.md").write_text(render_report(paths, res), encoding="utf-8")
    audit = {
        "pipeline_version": PIPELINE_VERSION, "as_of": res.as_of,
        "ran_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "inputs": res.files, "counts": res.counts,
        "outputs": {"rules.json": hashlib.sha256((paths.out_dir / "rules.json").read_bytes()).hexdigest()},
    }
    (paths.work_dir / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return {"rules": str(paths.out_dir / "rules.json"), "report": str(paths.work_dir / "report.md")}


def pending_packets(res: IngestResult) -> Dict[str, List[str]]:
    return OrderedDict((pid, res.problems.get(pid, [])) for pid, s in res.states.items() if s["state"] != "done")
