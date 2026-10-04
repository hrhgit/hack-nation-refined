#!/usr/bin/env python3
"""Bill-page check, computed from the stored rows of any variant (no harness file is touched).

  python3 eval/bill_values.py                       # every variant in eval/extraction
  python3 eval/bill_values.py --variants v3 v4

Two groups of pages where the earlier answer (Claude, or the hand-written gold for R002) has a pending or failed record:
  figure pages      the page states a number the proposal would set  -> key_value should be filled
  status-only pages the page shows a title and a history of actions  -> key_value should stay null
For each variant it counts tries, tries that wrote a record, and records with a non-null key_value (counts only).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FLOW = HERE / "extraction"
FIGURE = ["D076-01", "R002-01"]
STATUS_ONLY = ["D011-01", "D039-01", "D045-01", "D046-01", "D047-01"]


def tally(rows, pages):
    """tries, tries that wrote a record, records, tries with at least one filled key_value, records with a filled key_value"""
    tries = wrote = recs = filled_tries = filled = 0
    for r in rows:
        if r["prompt_id"] in pages and r["status"] == "ok":
            tries += 1
            acc = r["meta"]["accepted"]
            wrote += 1 if acc else 0
            recs += len(acc)
            n = sum(1 for a in acc if a.get("key_value"))
            filled += n
            filled_tries += 1 if n else 0
    return tries, wrote, recs, filled_tries, filled


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", nargs="*")
    args = ap.parse_args()
    names = args.variants or sorted(p.name for p in FLOW.iterdir() if (p / "results.jsonl").exists())
    print("%-9s | figure pages %s: tries, wrote a record, tries with a key_value | status-only pages %s: tries, wrote a record, records, records with a key_value" % ("variant", FIGURE, STATUS_ONLY))
    for v in names:
        rows = [json.loads(x) for x in (FLOW / v / "results.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        f, s = tally(rows, FIGURE), tally(rows, STATUS_ONLY)
        print("%-9s | %2d tries, %2d wrote, %2d tries with a key_value | %2d tries, %2d wrote, %2d records, %2d with a key_value" % (v, f[0], f[1], f[3], s[0], s[1], s[2], s[4]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
