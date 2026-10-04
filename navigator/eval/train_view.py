#!/usr/bin/env python3
"""The only way I look at transcripts while choosing a change: training packets only.

  python3 eval/train_view.py scores --variant baseline        # train rows: score and parts per case
  python3 eval/train_view.py show D025-01 --variant baseline  # one train transcript (records + a slice of the thinking)
Any packet that is not in the training split is refused, so held-out text cannot leak into a proposed change.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from common import FLOW

PARTS = ["score", "clean", "one_per_law", "cite_clean", "cite_num", "date_ok", "numbers_ok", "recall", "fields", "nonempty"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["scores", "show"])
    ap.add_argument("pid", nargs="?")
    ap.add_argument("--variant", default="baseline")
    ap.add_argument("--rep", type=int, default=0)
    ap.add_argument("--think", type=int, default=1500, help="characters of the model's reasoning to print (0 = none)")
    args = ap.parse_args()
    state = json.loads((FLOW / "_state.json").read_text(encoding="utf-8"))
    train = set(state["train_ids"])
    vdir = FLOW / args.variant
    if args.what == "scores":
        rows = [json.loads(x) for x in (vdir / "results.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        print("%-9s %s  %s" % ("packet", "rep", "  ".join("%-6s" % p[:6] for p in PARTS)))
        for r in sorted(rows, key=lambda r: (r["prompt_id"], r["rep"])):
            if r["prompt_id"] in train and r["status"] == "ok":
                print("%-9s %d    %s" % (r["prompt_id"], r["rep"], "  ".join("%-6s" % ("%.2f" % r["grade"][p] if p in r["grade"] else "-") for p in PARTS)))
        return 0
    if args.pid not in train:
        print("refused: %s is not a training packet" % args.pid, file=sys.stderr)
        return 1
    t = json.loads((vdir / "traces" / ("%s_rep%d.json" % (args.pid, args.rep))).read_text(encoding="utf-8"))
    ans, think = t[2]["content"], t[2].get("thinking", "")
    for line in ans.splitlines():
        if line.strip().startswith("{"):
            o = json.loads(line)
            if "category" in o:
                print("RECORD %-24s | %-40s | kv=%-26s | eff=%-10s | %s" % (o["category"][:24], str(o["citation"])[:40], str(o.get("key_value"))[:26], o.get("effective_date"), str(o["title"])[:60]))
            else:
                print("RECEIPT", o)
    if args.think:
        print("--- reasoning (%d chars), first %d:" % (len(think), args.think))
        print(re.sub(r"\n{2,}", "\n", think)[: args.think])
    return 0


if __name__ == "__main__":
    sys.exit(main())
