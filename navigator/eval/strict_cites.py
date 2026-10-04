#!/usr/bin/env python3
"""Does an answer cite the exact provision the challenge brief names for its own example rules?

  python3 eval/strict_cites.py                      # every variant in eval/extraction, tries 0-1
  python3 eval/strict_cites.py --variants v3 v4
  python3 eval/strict_cites.py --flow eval/explore/d067_check --variants v3 v4 --tries 8

Why it exists. The labels in labels.py accept any citation that names the right law (for example "46:8-19" or "46:8-21" for the
New Jersey deposit rule), because they were written to find the law, not to check the citation form. The brief says rules are
matched to the hidden key "by jurisdiction, category and citation" and names the provision it has in mind, for example
N.J.S.A. 46:8-21.2 for the 1.5-month deposit cap. This check uses the provision the brief itself names. It reads stored rows only
and touches no harness file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import FLOW  # noqa: E402
from labels import LABELS  # noqa: E402

# label id -> pattern for the provision the brief names (file.pdf, "Rule categories, with real examples from the corpus")
BRIEF = {
    "NJ-SDA": r"46:8-21\.2",
    "NJ-AEA": r"2A:18-61\.1(?!\d)",
    "NJ-405": r"c\.\s?0*405|405",
    "CA-1947.12": r"1947\.12", "CA-1946.2": r"1946\.2", "CA-1950.5": r"1950\.5", "CA-1950.6": r"1950\.6",
    "MA-15B-deposit": r"15B", "MA-15B-fees": r"15B", "MA-87DDD": r"87DDD", "MA-40P": r"40P",
    "SF-37.10C": r"37\.10C", "SF-rent": r"ch(apter|\.)?\s*37|37\b", "SD-algo": r"98\.11", "BK-13.63": r"13\.63",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--flow", default=str(FLOW))
    ap.add_argument("--variants", nargs="*")
    ap.add_argument("--tries", type=int, default=2, help="use tries 0..N-1 of every case")
    args = ap.parse_args()
    flow = Path(args.flow)
    names = args.variants or sorted((p.name for p in flow.iterdir() if (p / "results.jsonl").exists()), key=lambda n: (n != "baseline", n))
    state = json.loads((FLOW / "_state.json").read_text(encoding="utf-8"))
    train = set(state["train_ids"])
    labs = {l["id"]: l for l in LABELS}
    rows = {v: [json.loads(x) for x in (flow / v / "results.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()] for v in names}
    print("%-16s %-8s %-6s %s" % ("label", "page", "split", "   ".join("%-8s" % v for v in names)))
    total = {v: [0, 0] for v in names}
    for lid, rx in BRIEF.items():
        l = labs[lid]
        cells = []
        for v in names:
            rs = [r for r in rows[v] if r["prompt_id"] == l["packet"] and r["rep"] < args.tries and r["status"] == "ok"]
            if not rs:
                cells.append("-")
                continue
            hit = sum(1 for r in rs if any(a["jurisdiction"] == l["jurisdiction"] and a["category"] == l["category"]
                                           and re.search(rx, a["citation"] or "", re.I) for a in r["meta"]["accepted"]))
            total[v][0] += hit
            total[v][1] += len(rs)
            cells.append("%d/%d" % (hit, len(rs)))
        if all(c == "-" for c in cells):
            continue
        print("%-16s %-8s %-6s %s" % (lid, l["packet"], "train" if l["packet"] in train else "test", "   ".join("%-8s" % c for c in cells)))
    print("%-16s %-8s %-6s %s" % ("ALL", "", "", "   ".join("%-8s" % ("%d/%d" % tuple(total[v]) if total[v][1] else "-") for v in names)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
