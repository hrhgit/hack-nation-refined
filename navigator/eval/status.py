#!/usr/bin/env python3
"""Status table for the climb, recomputed from the raw rows (never from a summary the runner wrote).

  python3 eval/status.py                 # every variant under eval/extraction
  python3 eval/status.py --flow eval/pilot
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from common import FLOW, load_cases
from cost import cost_usd

PARTS = ["clean", "one_per_law", "cite_clean", "cite_num", "date_ok", "recall", "fields", "nonempty", "silver_f1"]


MAX_REP = 2


def read_all(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []


def read(path: Path) -> List[Dict[str, Any]]:
    return [r for r in read_all(path) if r.get("rep", 0) < MAX_REP]


def mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def half(xs: List[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    m = mean(xs)
    return 1.96 * math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) / math.sqrt(len(xs))


def case_means(rows: List[Dict[str, Any]], metric: str) -> Dict[str, float]:
    acc: Dict[str, List[float]] = {}
    for r in rows:
        if r.get("status") == "ok" and metric in r["grade"]:
            acc.setdefault(r["prompt_id"], []).append(r["grade"][metric])
    return {k: mean(v) for k, v in acc.items()}


def variants(flow: Path) -> List[str]:
    names = [p.name for p in flow.iterdir() if p.is_dir() and re.fullmatch(r"baseline|v\d+", p.name)]
    return sorted(names, key=lambda n: -1 if n == "baseline" else int(n[1:]))


def fmt(m: float, h: float) -> str:
    return "n/a" if math.isnan(m) else ("%.3f" % m if math.isnan(h) else "%.3f ±%.3f" % (m, h))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", default=str(FLOW))
    ap.add_argument("--reps", type=int, default=2, help="use tries 0..N-1 of every case (keeps variants comparable)")
    args = ap.parse_args(argv)
    global MAX_REP
    MAX_REP = args.reps
    flow = Path(args.flow)
    split = {c["id"]: c["split"] for c in load_cases()}
    names = variants(flow)
    if not names:
        print("no variants yet")
        return 0
    base_rows = read(flow / "baseline" / "results.jsonl")
    base_case = case_means(base_rows, "score")
    total_spend = 0.0
    print("| variant | test score | train score | test vs baseline | clean | one/law | cite_clean | cite_num | date_ok | recall | fields | out toks | s/call | $/pass | spend | err |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for n in names:
        everything = read_all(flow / n / "results.jsonl")      # spend counts every row, extra tries included
        rows = [r for r in everything if r.get("rep", 0) < MAX_REP]
        errs = read_all(flow / n / "errors.jsonl")
        ok = [r for r in rows if r.get("status") == "ok"]
        cm = case_means(rows, "score")
        te = [v for k, v in cm.items() if split.get(k) == "test"]
        tr = [v for k, v in cm.items() if split.get(k) == "train"]
        delta = "-"
        if n != "baseline":
            d = [cm[k] - base_case[k] for k in cm if k in base_case and split.get(k) == "test"]
            delta = "%+.3f ±%.3f (n=%d)" % (mean(d), half(d), len(d)) if d else "n/a"
        cols = []
        for part in ("clean", "one_per_law", "cite_clean", "cite_num", "date_ok", "recall", "fields"):
            v = list(case_means(rows, part).values())
            cols.append("%.2f" % mean(v) if v else "-")
        reps = (max([r["rep"] for r in rows]) + 1) if rows else 1
        one_pass = sum(r.get("cost_usd", 0.0) for r in rows) / reps
        spend = sum(r.get("cost_usd", 0.0) for r in everything) + sum(
            cost_usd(e.get("model") or "", e.get("usage") or {}, __import__("datetime").datetime.now(__import__("datetime").timezone.utc)) for e in errs if e.get("usage"))
        total_spend += spend
        print("| %s | %s | %s | %s | %s | %.0f | %.1f | $%.3f | $%.2f | %d |" % (
            n, fmt(mean(te), half(te)), fmt(mean(tr), half(tr)), delta, " | ".join(cols),
            mean([r["usage"]["output_tokens"] for r in ok]) if ok else 0, mean([r["latency_s"] for r in ok]) if ok else 0,
            one_pass, total_spend, len(errs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
