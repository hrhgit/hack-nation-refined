#!/usr/bin/env python3
"""Re-grade stored answers with the current grader (no model call), and show how the grades moved.

  python3 eval/regrade.py --flow eval/explore/current --variant baseline [--write]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import load_ctx
from grader import grade


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", required=True)
    ap.add_argument("--variant", default="baseline")
    ap.add_argument("--write", action="store_true", help="overwrite results.jsonl (the old file is kept as results.before-regrade.jsonl)")
    args = ap.parse_args()
    ctx = load_ctx()
    vdir = Path(args.flow) / args.variant
    rows = [json.loads(x) for x in (vdir / "results.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    out = []
    print("%-9s %-5s %8s %8s   moved" % ("packet", "rep", "before", "after"))
    for r in rows:
        trace = json.loads((vdir / "traces" / ("%s_rep%d.json" % (r["prompt_id"], r["rep"]))).read_text(encoding="utf-8"))
        res = grade(ctx, r["prompt_id"], trace[-1]["content"], r.get("stop_reason", "stop"))
        new = dict(r, grade=res["grade"], explanation=res["explanation"], status=res["status"])
        new["meta"] = dict(r["meta"], records=res["records"], accepted=res["accepted"], rejected=res["rejected"])
        before, after = r["grade"].get("score"), res["grade"].get("score")
        moved = ", ".join("%s %.2f->%.2f" % (k, r["grade"][k], res["grade"][k]) for k in res["grade"]
                          if k in r["grade"] and abs(r["grade"][k] - res["grade"][k]) > 1e-9 and k != "score")
        print("%-9s %-5d %8s %8s   %s" % (r["prompt_id"], r["rep"], "%.3f" % before if before is not None else "-",
                                          "%.3f" % after if after is not None else "-", moved))
        out.append(new)
    if args.write:
        (vdir / "results.before-regrade.jsonl").write_text((vdir / "results.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
        (vdir / "results.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in out) + "\n", encoding="utf-8")
        print("rewritten; the old rows are in results.before-regrade.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
