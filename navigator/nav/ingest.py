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
from . import conditions
from .packets import load_index
from .parse import classify, extract_json_objects
from .spans import DocIndex

NULLISH = {"", "null", "none", "n/a", "na", "unknown", "not stated", "not specified", "not applicable", "-"}
APPL_KEYS = conditions.APPL_KEYS
DATE_BASES = conditions.DATE_BASES
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

# Which record is the "headline" of a law when a document yields several records for it.
HEADLINE_WORDS = {
    "rent_increase_limits": r"cap|maximum|limit|percent|%|cpi|allowable|annual|rent control|stabiliz|prohibit",
    "just_cause_eviction": r"just cause|good cause|grounds|causes?|eviction|terminat",
    "security_deposits": r"cap|maximum|exceed|limit|deposit",
    "application_screening_fees": r"cap|maximum|fee|limit",
    "screening_restrictions": r"criminal|source of income|credit|screen|background|fair chance|voucher",
    "algorithmic_rent_setting": r"unlawful|prohibit|ban|algorithm|pricing",
}
EXCEPTION_WORDS = (r"exception|exempt|small landlord|service member|qualif|interest|photograph|itemiz|return|"
                   r"nonrefundable|bad faith|retaliat|procedur|notice|filing|coverage|definition|penalt|remed")
OVERRIDE_FIELDS = {"effective_date", "lifecycle", "key_value", "title", "requirement", "conflict_flag", "conflict_note"}


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
        self._act: Dict[str, Any] = {}

    def act(self, doc_id: str):
        """The act's own effective-date rule worked out from its text, when the text allows it."""
        if doc_id not in self._act:
            self._act[doc_id] = facts.act_dates(self.docs[doc_id].body)
        return self._act[doc_id]

    def doc_index(self, doc_id: str) -> DocIndex:
        if doc_id not in self._idx:
            self._idx[doc_id] = DocIndex(self.docs[doc_id].body)
        return self._idx[doc_id]

    def dates(self, doc_id: str):
        if doc_id not in self._dates:
            found = facts.doc_dates(self.docs[doc_id].body)
            a = self.act(doc_id)
            if a:
                found |= {a.effective, a.effective[:7], a.effective[:4]}
            self._dates[doc_id] = found
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
                  "coverage_conditions", "exemptions", "penalty", "interaction", "conflict_note", "valid_through"):
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

        notes: List[str] = []
        eff = g("effective_date")
        act = self.act(pdoc) if lifecycle == "enacted" else None
        date_source = "model" if eff is not None else None
        if eff is not None:
            norm = facts.normalize_date(eff)
            if norm is None:
                errors.append("effective_date %r is not a date (use YYYY-MM-DD, YYYY-MM or YYYY)" % eff)
            else:
                if norm != eff:
                    warns.append("effective_date %r rewritten as %s" % (eff, norm))
                eff = norm
                if act and act.effective.startswith(eff) and eff != act.effective:
                    notes.append("effective_date %s made exact (%s) from the act's own clause" % (eff, act.effective))
                    eff, date_source = act.effective, "act clause"
                elif act and eff != act.effective:
                    warns.append("effective_date %s differs from %s, which the act's own clause gives (%s, approved %s)"
                                 % (eff, act.effective, act.clause, act.approved))
                elif not facts.date_supported(eff, self.dates(pdoc)):
                    warns.append("effective_date %s does not appear in %s: check it" % (eff, pdoc))
        elif act:
            eff, date_source = act.effective, "act clause"
            notes.append("effective_date %s worked out from the act's own clause (%s) and its approval date %s"
                         % (act.effective, act.clause, act.approved))

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

        def locate_quote(q: str) -> Optional[str]:
            if "[[omitted" in q:
                return None
            m = self.doc_index(pdoc).locate(q)
            return m.text if m is not None else None

        valid_through = g("valid_through")
        if valid_through is not None:
            vt = facts.normalize_date(valid_through)
            if vt is None:
                warns.append("valid_through %r is not a date: ignored" % valid_through)
            elif not facts.date_supported(vt, self.dates(pdoc)):
                warns.append("valid_through %s is not printed in %s: check it" % (vt, pdoc))
            valid_through = vt
        applicability = conditions.parse(raw.get("applicability"), warns, self.dates(pdoc), self.nums(pdoc), locate_quote)
        relations = conditions.parse_relations(raw.get("relations"), warns, locate_quote)

        citation, aspect = facts.split_citation(facts.normalize_citation(g("citation") or ""))
        if g("citation") and not citation:
            errors.append("citation is empty after cleanup")
        if aspect:
            notes.append("citation descriptor moved out of the citation: %s" % aspect)

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
        rule["applicability"] = applicability
        rule["exemptions"] = g("exemptions")
        rule["penalty"] = g("penalty")
        rule["overrides"] = []
        rule["interaction"] = g("interaction")
        rule["effective_date"] = eff
        rule["valid_through"] = valid_through
        rule["relations"] = relations
        rule["citation"] = citation
        rule["aspect"] = aspect
        rule["citation_kind"] = "numbered" if re.search(r"\d", citation) else "descriptive"
        rule["source_doc_id"] = pdoc
        rule["source_url"] = doc.url
        rule["retrieved"] = doc.retrieved
        rule["quoted_span"] = span
        rule["confidence"] = conf
        rule["conflict_flag"] = cf
        rule["conflict_note"] = g("conflict_note")
        rule["packet_id"] = pid
        rule["date_source"] = date_source
        rule["warnings"] = warns
        rule["notes"] = notes

        bad = jschema.check(to_schema_record(rule, "r-0000"), self.schema)
        if bad:
            return None, ["schema: " + b for b in bad], warns
        return rule, [], warns

    @staticmethod
    def _applicability(a: Any, warns: List[str]) -> Dict[str, Any]:
        return conditions.parse(a, warns)


def to_schema_record(rule: Dict[str, Any], rule_id: str) -> Dict[str, Any]:
    full = dict(rule)
    full["team_rule_id"] = rule_id
    return OrderedDict((k, full.get(k)) for k in SCHEMA_ORDER)


# ---------------------------------------------------------------- one record per law and category

def _group_key(r: Dict[str, Any]) -> Tuple[str, str, str]:
    return (r["jurisdiction"], r["category"], facts.citation_key(r["citation"]))


class _Positions(object):
    """Where each record's quote sits in its document: the main clause usually comes first."""

    def __init__(self, docs: Dict[str, Doc]):
        self.docs = docs
        self.cache: Dict[Tuple[str, str], int] = {}

    def __call__(self, r: Dict[str, Any]) -> int:
        k = (r["source_doc_id"], r["quoted_span"])
        if k not in self.cache:
            pos = self.docs[r["source_doc_id"]].body.find(r["quoted_span"])
            self.cache[k] = pos if pos >= 0 else 10 ** 9
        return self.cache[k]


def headline_key(r: Dict[str, Any], pos: "_Positions"):
    """Sort key (best first) for choosing which of several records is the main one for a law.

    Heuristic: the main rule says what the category is about (a cap, a ban, the list of causes) and is not an
    exception or a procedure; it carries a headline value and a date; it carries no descriptor in its citation.
    """
    text = " ".join(x for x in (r.get("aspect"), r.get("title"), r.get("key_value")) if x)
    score = 0.0
    if re.search(HEADLINE_WORDS.get(r["category"], "$^"), text, re.I):
        score += 3
    if re.search(EXCEPTION_WORDS, text, re.I):
        score -= 2
    score += 1 if r.get("key_value") else 0
    score += 1 if r.get("effective_date") else 0
    score += 2 if not r.get("aspect") else 0
    score += r.get("confidence") or 0
    return (-score, pos(r))


def _consolidate(group: List[Dict[str, Any]], docs: Dict[str, Doc], pos: "_Positions"):
    """Turn every record for one law+category into one rule.

    Per document the main record is chosen and the others become sub_rules. The documents are then compared:
    only disagreement between different documents is reported as a conflict.
    """
    by_doc: "OrderedDict[str, List[Dict[str, Any]]]" = OrderedDict()
    for r in group:
        by_doc.setdefault(r["source_doc_id"], []).append(r)
    heads: List[Tuple[str, Dict[str, Any]]] = []
    subs: List[Dict[str, Any]] = []
    for did, recs in by_doc.items():
        ranked = sorted(recs, key=lambda r: headline_key(r, pos))
        heads.append((did, ranked[0]))
        subs.extend(ranked[1:])
    heads.sort(key=lambda h: (-source_priority(docs.get(h[0])), -(h[1]["confidence"] or 0), h[0]))
    primary = dict(heads[0][1])
    primary["relations"] = list(primary.get("relations") or [])
    primary["warnings"] = list(primary["warnings"])
    primary["notes"] = list(primary["notes"])
    for did, h in heads[1:]:
        for f in ("key_value", "coverage_conditions", "exemptions", "penalty", "interaction", "effective_date"):
            if primary.get(f) is None and h.get(f) is not None:
                primary[f] = h[f]
                primary["notes"].append("%s filled in from %s" % (f, did))
        primary["applicability"] = dict(primary["applicability"], coverage_quotes=list(primary["applicability"]["coverage_quotes"]))
        conditions.merge(primary, h, did, primary["notes"], primary["warnings"])
        for w in h["warnings"]:
            if w not in primary["warnings"]:
                primary["warnings"].append(w)
    conflicts: List[str] = []
    for did, h in heads[1:]:
        a, b = heads[0][1], h
        if a["effective_date"] and b["effective_date"] and a["effective_date"] != b["effective_date"]:
            conflicts.append("effective_date: %s says %s, %s says %s" % (a["source_doc_id"], a["effective_date"], did, b["effective_date"]))
        sa, sb = facts.numeric_signature(a["key_value"]), facts.numeric_signature(b["key_value"])
        if sa and sb and sa != sb:
            conflicts.append("key_value: %s says %r, %s says %r" % (a["source_doc_id"], a["key_value"], did, b["key_value"]))
        if a["lifecycle"] != b["lifecycle"]:
            conflicts.append("lifecycle: %s says %s, %s says %s" % (a["source_doc_id"], a["lifecycle"], did, b["lifecycle"]))
    conflicts = sorted(set(conflicts))
    if conflicts:
        primary["conflict_flag"] = True
        extra = "Sources disagree: " + "; ".join(conflicts)
        primary["conflict_note"] = (primary["conflict_note"] + " | " + extra) if primary["conflict_note"] else extra
    primary["sources"] = [{"doc_id": did, "url": h["source_url"], "retrieved": h["retrieved"], "quoted_span": h["quoted_span"],
                           "effective_date": h["effective_date"], "key_value": h["key_value"], "lifecycle": h["lifecycle"]}
                          for did, h in heads]
    primary["sub_rules"] = [{"doc_id": x["source_doc_id"], "aspect": x.get("aspect"), "title": x["title"],
                             "key_value": x["key_value"], "effective_date": x["effective_date"],
                             "quoted_span": x["quoted_span"]} for x in subs]
    primary["merged_from"] = len(group)
    return primary, conflicts


def _enforce_single_record(bucket: "PacketResp", pid: str, fname: str, pos: "_Positions",
                           rejected: List[Dict[str, Any]]) -> None:
    """One answer must hold one record per law and category. The best one stays; the others are sent back."""
    groups: "OrderedDict[Tuple[str, str, str], List[Dict[str, Any]]]" = OrderedDict()
    for r in bucket.rules:
        groups.setdefault(_group_key(r), []).append(r)
    for grp in groups.values():
        if len(grp) < 2:
            continue
        ranked = sorted(grp, key=lambda r: headline_key(r, pos))
        keep = ranked[0]
        for x in ranked[1:]:
            bucket.rules.remove(x)
            bucket.rejected += 1
            rejected.append({"file": fname, "packet_id": pid, "record": x["_raw"], "reasons": [
                "one record per law and category: you also wrote '%s' for %s (%s). Merge this record into it: "
                "put the extra details in requirement, exemptions or penalty and keep a single headline "
                "key_value and effective_date" % (keep["title"][:60], keep["citation"], keep["category"])]})


# ---------------------------------------------------------------- human overrides

def load_overrides(paths: Paths) -> List[Dict[str, Any]]:
    f = paths.work_dir / "overrides.json"
    if not f.exists():
        return []
    data = json.loads(f.read_text(encoding="utf-8"))
    items = data["overrides"] if isinstance(data, dict) else data
    for ov in items:
        for k in ("id", "match", "set", "reason", "source"):
            if k not in ov:
                raise ValueError("overrides.json: entry %r is missing %r" % (ov.get("id"), k))
        bad = set(ov["set"]) - OVERRIDE_FIELDS
        if bad:
            raise ValueError("overrides.json: %s may not set %s" % (ov["id"], ", ".join(sorted(bad))))
    return items


def apply_overrides(rules: List[Dict[str, Any]], overrides: List[Dict[str, Any]], as_of: str):
    """A person's correction, always with a stated reason and source, recorded on the rule and in the report."""
    applied: List[Dict[str, Any]] = []
    unused: List[str] = []
    for ov in overrides:
        m = ov["match"]
        hits = [r for r in rules
                if (not m.get("jurisdiction") or r["jurisdiction"] == m["jurisdiction"])
                and (not m.get("category") or r["category"] == m["category"])
                and (not m.get("source_doc_id") or r["source_doc_id"] == m["source_doc_id"])
                and (not m.get("citation_contains") or m["citation_contains"].lower() in r["citation"].lower())]
        if not hits:
            unused.append(ov["id"])
            continue
        for r in hits:
            before = {k: r.get(k) for k in ov["set"]}
            r.update(ov["set"])
            r["status"] = facts.derive_status(r["lifecycle"], r["effective_date"], as_of)
            if "effective_date" in ov["set"]:
                r["date_source"] = "override " + ov["id"]
            r["notes"] = list(r.get("notes", [])) + ["override %s: %s" % (ov["id"], ov["reason"])]
            rec = {"id": ov["id"], "rule": "%s | %s | %s" % (r["jurisdiction"], r["category"], r["citation"]),
                   "before": before, "after": dict(ov["set"]), "reason": ov["reason"], "source": ov["source"]}
            r["overrides_applied"] = list(r.get("overrides_applied", [])) + [rec]
            applied.append(rec)
    return applied, unused


# ---------------------------------------------------------------- results

@dataclass
class PacketResp:
    records: List[Dict[str, Any]] = field(default_factory=list)
    rules: List[Dict[str, Any]] = field(default_factory=list)
    receipt: Optional[Dict[str, Any]] = None
    rejected: int = 0
    file: str = ""

    @property
    def accepted(self) -> int:
        return len(self.rules)

    @property
    def clean(self) -> bool:
        return self.receipt is not None and self.receipt.get("n_rules") == len(self.records) and not self.rejected


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
    dropped: List[Tuple[str, str, str]] = field(default_factory=list)
    overrides_applied: List[Dict[str, Any]] = field(default_factory=list)
    overrides_unused: List[str] = field(default_factory=list)


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
    pos = _Positions(docs)
    docs_packets: Dict[str, List[str]] = defaultdict(list)
    for pid, meta in index["packets"].items():
        docs_packets[meta["doc_id"]].append(pid)

    files_meta: List[Dict[str, Any]] = []
    parse_problems: List[Tuple[str, str]] = []
    rejected: List[Dict[str, Any]] = []
    responses: Dict[str, List[PacketResp]] = defaultdict(list)  # packet -> its answers, oldest first
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
                rule["_file"] = f.name
                rule["_raw"] = obj
                bucket.rules.append(rule)
        for pid, r in resp.items():
            if pid in index["packets"]:
                _enforce_single_record(r, pid, f.name, pos, rejected)
                responses[pid].append(r)

    latest = {pid: rs[-1] for pid, rs in responses.items()}
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

    # The rules of a packet are its newest clean answer. While the newest answer is still being fixed,
    # everything accepted so far stays in use, so nothing disappears in the meantime.
    pool: List[Dict[str, Any]] = []
    dropped: List[Tuple[str, str, str]] = []
    for pid, rs in responses.items():
        if rs[-1].clean:
            pool += rs[-1].rules
            kept = {_group_key(x) for x in rs[-1].rules}
            seen = set()
            for old in rs[:-1]:
                for x in old.rules:
                    k = _group_key(x)
                    if k not in kept and k not in seen:
                        seen.add(k)
                        dropped.append((pid, "%s | %s" % (x["jurisdiction"], x["category"]), x["citation"]))
        else:
            for r in rs:
                pool += r.rules

    groups: "OrderedDict[Tuple[str, str, str], List[Dict[str, Any]]]" = OrderedDict()
    for r in pool:
        groups.setdefault(_group_key(r), []).append(r)
    merged: List[Dict[str, Any]] = []
    conflicts: List[Tuple[str, List[str]]] = []
    for key, grp in groups.items():
        m, notes = _consolidate(grp, docs, pos)
        merged.append(m)
        if notes:
            conflicts.append((" / ".join(key[:2]) + " " + m["citation"], notes))

    applied, unused = apply_overrides(merged, load_overrides(paths), as_of)

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

    _assign_ids(paths, merged, persist_ids)
    counts = {
        "files": len(files_meta), "records_parsed": n_records, "accepted": len(pool),
        "rejected": sum(1 for r in rejected if r["open"]), "rejected_fixed": sum(1 for r in rejected if not r["open"]),
        "rules": len(merged),
        "packets_total": len(index["packets"]),
        "packets_done": sum(1 for s in states.values() if s["state"] == "done"),
    }
    return IngestResult(as_of, files_meta, parse_problems, merged, rejected, states, conflicts, near, counts, problems,
                        matrix_extra=[], dropped=dropped, overrides_applied=applied, overrides_unused=unused)


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
        for k in ("lifecycle", "applicability", "penalty", "retrieved", "packet_id", "aspect", "citation_kind", "date_source",
                  "warnings", "notes", "sources", "sub_rules", "merged_from", "overrides_applied", "valid_through", "relations"):
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
