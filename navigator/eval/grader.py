"""Deterministic grader for one model answer to one packet. No model is involved in grading.

It reuses the pipeline's own validator, so "accepted" here means exactly what it means in production, then adds
the checks the first full run showed to matter: one record per law, clean citations, dates, and the expected laws
from labels.py.

Every metric is in [0, 1]; a metric that does not apply to a packet is left out of the dict (None).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from common import Ctx, classify, extract_json_objects, facts, load_silver
from labels import LABELS
from nav.ingest import PacketResp, _enforce_single_record

DATE_WARNINGS = ("does not appear in", "differs from")
CODE_PATTERN = re.compile(
    r"(?:§§?|\bSec(?:tion|\.)\s*(?!8\b)|\bBMC|\bLAMC|\bSDMC|N\.J\.S\.A\.|G\.L\.|P\.L\.|\bChapter|\bch\.)\s*\d", re.I)
SCORE_PARTS = ("clean", "one_per_law", "cite_clean", "cite_num", "date_ok", "numbers_ok", "recall", "fields", "nonempty")

_SILVER: Optional[Dict[str, Any]] = None


def _silver() -> Dict[str, Any]:
    global _SILVER
    if _SILVER is None:
        _SILVER = load_silver()
    return _SILVER


def _mean(xs: List[float]) -> Optional[float]:
    return sum(xs) / len(xs) if xs else None


def _find(label: Dict[str, Any], rules: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    rx = re.compile(label["cite_re"], re.I)
    hits = [r for r in rules if r["jurisdiction"] == label["jurisdiction"] and r["category"] == label["category"]
            and rx.search((r["citation"] or "") + " " + (r["title"] or ""))]
    return hits[0] if hits else None


def _label_checks(label: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, bool]:
    checks: Dict[str, bool] = {}
    if label.get("status"):
        checks["status"] = rule["status"] == label["status"]
    if label.get("effective_date"):
        checks["effective_date"] = (rule["effective_date"] or "").startswith(label["effective_date"])
    if label.get("key_numbers"):
        have = facts.numbers_in(rule["key_value"] or "")
        checks["key_value"] = all(n in have for n in label["key_numbers"])
    return checks


def grade(ctx: Ctx, pid: str, text: str, finish_reason: str = "stop") -> Dict[str, Any]:
    doc_id = ctx.index["packets"][pid]["doc_id"]
    doc = ctx.docs[doc_id]
    if finish_reason != "stop":
        return {"status": "truncated", "grade": {}, "explanation": {}, "records": 0, "accepted": [], "rejected": []}

    objs, problems = extract_json_objects(text)
    records = [o for o in objs if classify(o) == "record"]
    receipts = [o for o in objs if classify(o) == "receipt"]
    foreign = [o for o in records + receipts if o.get("packet_id") != pid]

    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    for o in records:
        if o.get("packet_id") != pid:
            rejected.append({"record": o, "reasons": ["record carries another packet id"]})
            continue
        rule, errs, _ = ctx.validator.check(o)
        if errs:
            rejected.append({"record": o, "reasons": errs})
        else:
            rule["_raw"] = o
            accepted.append(rule)
    valid = list(accepted)  # passed the validator, before the one-record-per-law enforcement
    bucket = PacketResp(records=records, rules=accepted, receipt=receipts[0] if len(receipts) == 1 else None, file="eval")
    split_off: List[Dict[str, Any]] = []
    _enforce_single_record(bucket, pid, "eval", ctx.pos, split_off)
    accepted = bucket.rules
    rejected += split_off

    n = len(records)
    receipt_ok = len(receipts) == 1 and receipts[0].get("packet_id") == pid and receipts[0].get("n_rules") == n
    g: Dict[str, float] = {}
    why: Dict[str, str] = {}

    g["clean"] = 1.0 if (receipt_ok and not problems and not rejected and not foreign) else 0.0
    if g["clean"] == 0.0:
        bits = []
        if not receipt_ok:
            bits.append("receipt missing or its count is wrong")
        bits += problems[:2]
        for rj in rejected[:3]:
            bits.append("%s: %s" % (str(rj["record"].get("citation"))[:40], rj["reasons"][0][:90]))
        why["clean"] = "; ".join(bits)

    # One record per law and category. A model can dodge a check on identical citations by varying the citation,
    # so count crowding per (jurisdiction, category) cell: more records than distinct numbered citations (at least one).
    cells: Dict[tuple, List[Dict[str, Any]]] = {}
    for r in valid:
        cells.setdefault((r["jurisdiction"], r["category"]), []).append(r)
    excess = 0
    crowded = []
    for cell, rs in cells.items():
        numbered = {facts.citation_key(r["citation"]) for r in rs if r["citation_kind"] == "numbered"}
        extra = max(0, len(rs) - max(1, len(numbered)))
        excess += extra
        if extra:
            crowded.append("%s/%s: %d records, %d distinct numbered laws" % (cell[0], cell[1], len(rs), len(numbered)))
    g["one_per_law"] = 1.0 - (excess / len(valid)) if valid else 1.0
    if crowded:
        why["one_per_law"] = "; ".join(crowded[:3])

    if accepted:
        loose = [r for r in accepted if r.get("aspect")]
        g["cite_clean"] = 1.0 - len(loose) / len(accepted)
        if loose:
            why["cite_clean"] = "descriptor in citation: " + " | ".join(str(r["_raw"].get("citation"))[:60] for r in loose[:3])
        if CODE_PATTERN.search(doc.body):
            numbered = [r for r in accepted if r["citation_kind"] == "numbered"]
            g["cite_num"] = len(numbered) / len(accepted)
            if len(numbered) < len(accepted):
                why["cite_num"] = "no section/chapter/bill number: " + " | ".join(
                    r["citation"][:60] for r in accepted if r["citation_kind"] != "numbered")[:200]

    enacted = [r for r in accepted if r["lifecycle"] == "enacted"]
    if enacted:
        act = ctx.validator.act(doc_id)
        oks = []
        for r in enacted:
            bad = any(k in w for w in r["warnings"] for k in DATE_WARNINGS)
            missed = any("worked out" in note for note in r["notes"])
            oks.append(0.0 if (bad or missed) else 1.0)
        g["date_ok"] = _mean(oks)
        if g["date_ok"] < 1.0:
            why["date_ok"] = "date missing or unsupported" + (" (the act spells it out: %s)" % act.effective if act else "")

    if accepted:
        invented = [r for r in accepted if any("key_value numbers not found" in w for w in r["warnings"])]
        g["numbers_ok"] = 1.0 - len(invented) / len(accepted)
        if invented:
            why["numbers_ok"] = "numbers not in the text: " + " | ".join(str(r["key_value"])[:50] for r in invented[:3])

    labels = [l for l in LABELS if l["packet"] == pid]
    if labels:
        found, field_checks, missing, wrong = 0, [], [], []
        for l in labels:
            r = _find(l, accepted)
            if r is None:
                missing.append(l["id"])
                continue
            found += 1
            for name, ok in _label_checks(l, r).items():
                field_checks.append(1.0 if ok else 0.0)
                if not ok:
                    wrong.append("%s.%s" % (l["id"], name))
        g["recall"] = found / len(labels)
        if missing:
            why["recall"] = "expected law not found: " + ", ".join(missing)
        if field_checks:
            g["fields"] = _mean(field_checks)
            if wrong:
                why["fields"] = "wrong: " + ", ".join(wrong)

    silver = _silver().get(pid, {"n_records": 0, "cells": []})
    # Only a missing answer is punished. A packet that is one part of a longer document may legitimately hold a rule
    # that the earlier extraction recorded from another part, and each packet is answered on its own.
    g["nonempty"] = 0.0 if (silver["n_records"] > 0 and n == 0) else 1.0
    if g["nonempty"] == 0.0:
        why["nonempty"] = "wrote nothing; the earlier extraction wrote %d record(s)" % silver["n_records"]
    pred_cells = {(r["jurisdiction"], r["category"]) for r in accepted}
    ref_cells = {tuple(c) for c in silver["cells"]}
    if pred_cells or ref_cells:
        inter = len(pred_cells & ref_cells)
        p = inter / len(pred_cells) if pred_cells else 0.0
        rcl = inter / len(ref_cells) if ref_cells else 0.0
        g["silver_f1"] = 2 * p * rcl / (p + rcl) if (p + rcl) else 0.0
    else:
        g["silver_f1"] = 1.0

    if silver["n_records"] > 0 and n == 0:
        # Writing nothing is not "compliant": it must not earn credit for rules it never wrote.
        g["clean"], g["one_per_law"] = 0.0, 0.0
        why["clean"] = "no record at all, but the earlier extraction found %d" % silver["n_records"]

    parts = [g[k] for k in SCORE_PARTS if k in g]
    g["score"] = sum(parts) / len(parts)
    g["rec_ok"] = len([1 for _ in accepted]) / n if n else 1.0

    def brief(r: Dict[str, Any]) -> Dict[str, Any]:
        return {k: r.get(k) for k in ("jurisdiction", "category", "citation", "aspect", "title", "status",
                                      "effective_date", "key_value", "confidence")}
    return {"status": "ok", "grade": {k: round(v, 4) for k, v in g.items()}, "explanation": why, "records": n,
            "accepted": [brief(r) for r in accepted],
            "rejected": [{"citation": rj["record"].get("citation"), "reasons": rj["reasons"]} for rj in rejected]}
