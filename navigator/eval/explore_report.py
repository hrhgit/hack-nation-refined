#!/usr/bin/env python3
"""Where is the model strong and weak? Aggregates one exploration run by kind, failure class, size, citation habit.

  python3 eval/explore_report.py eval/explore/train
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

from common import load_cases, load_silver

PARTS = ["score", "clean", "one_per_law", "cite_clean", "cite_num", "date_ok", "recall", "fields", "nonempty", "silver_f1"]
CLASSES = [("one record per law", "over-split (same law written again)"), ("not found in", "quote not found in the source"),
           ("must be text or null", "wrong field type"), ("is not one of", "category not allowed"),
           ("effective_date", "bad effective_date"), ("jurisdiction", "bad jurisdiction"), ("missing", "missing field"),
           ("lifecycle", "bad lifecycle"), ("another packet", "other packet id")]


def classify(reason: str) -> str:
    for needle, name in CLASSES:
        if needle in reason:
            return name
    return "other: " + reason[:50]


def m(xs):
    xs = [x for x in xs if x is not None]
    return "%.2f" % statistics.mean(xs) if xs else "-"


def main() -> int:
    flow = Path(sys.argv[1])
    rows = [json.loads(x) for x in (flow / "baseline" / "results.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    errs = [json.loads(x) for x in (flow / "baseline" / "errors.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()] \
        if (flow / "baseline" / "errors.jsonl").exists() else []
    cases = {c["id"]: c for c in load_cases()}
    silver = load_silver()
    ok = [r for r in rows if r["status"] == "ok"]
    print("rows: %d ok, %d truncated, %d failed attempts\n" % (len(ok), len(rows) - len(ok), len(errs)))

    print("== score parts, all / by document kind / labeled")
    print("%-12s %6s | %s | %s" % ("part", "all", "  ".join("%-9s" % k for k in ("statute", "ordinance", "web_page", "guide")), "labeled  unlabeled"))
    for p in PARTS:
        by = lambda f: m([r["grade"].get(p) for r in ok if f(cases[r["prompt_id"]])])
        print("%-12s %6s | %s | %s   %s" % (p, by(lambda c: True), "  ".join("%-9s" % by(lambda c, k=k: c["kind"] == k) for k in ("statute", "ordinance", "web_page", "guide")),
                                          by(lambda c: c["labeled"]), by(lambda c: not c["labeled"])))
    print("   n:", {k: sum(1 for r in ok if cases[r["prompt_id"]]["kind"] == k) for k in ("statute", "ordinance", "web_page", "guide")})

    print("\n== why records were sent back (count of records)")
    why = Counter()
    for r in ok:
        for rj in r["meta"]["rejected"]:
            why[classify(rj["reasons"][0])] += 1
    for k, v in why.most_common():
        print("  %3d  %s" % (v, k))
    print("  packets with at least one rejection: %d of %d" % (sum(1 for r in ok if r["meta"]["rejected"]), len(ok)))

    print("\n== volume: records written vs the earlier extraction")
    over, under, same = 0, 0, 0
    for r in ok:
        n, s = r["meta"]["records"], silver[r["prompt_id"]]["n_records"]
        over += n > s * 1.5 + 1
        under += n < s * 0.5
        same += not (n > s * 1.5 + 1) and not (n < s * 0.5)
    tot_n = sum(r["meta"]["records"] for r in ok)
    tot_s = sum(silver[r["prompt_id"]]["n_records"] for r in ok)
    print("  deepseek wrote %d records, the earlier extraction %d (ratio %.2f). Packets far above: %d, far below: %d, about equal: %d" % (tot_n, tot_s, tot_n / max(tot_s, 1), over, under, same))
    big = sorted(ok, key=lambda r: -r["meta"]["records"])[:6]
    print("  most records:", ", ".join("%s=%d (earlier %d)" % (r["prompt_id"], r["meta"]["records"], silver[r["prompt_id"]]["n_records"]) for r in big))

    print("\n== citations")
    acc = [a for r in ok for a in r["meta"]["accepted"]]
    numbered = sum(1 for a in acc if re.search(r"\d", a["citation"] or ""))
    print("  accepted records: %d | with a number: %d | with a topic after the citation: %d" % (len(acc), numbered, sum(1 for a in acc if a.get("aspect"))))
    desc = Counter(a["citation"] for a in acc if not re.search(r"\d", a["citation"] or ""))
    print("  citations without a number:", dict(desc.most_common(8)))

    print("\n== dates and status (accepted records)")
    print("  enacted with no date: %d of %d enacted | statuses: %s" % (
        sum(1 for a in acc if a["status"] == "in_force" and not a["effective_date"]), sum(1 for a in acc if a["status"] != "pending"),
        dict(Counter(a["status"] for a in acc))))

    print("\n== expected laws (labels): found / wrong fields")
    for r in ok:
        e = r["explanation"]
        if "recall" in e or "fields" in e:
            print("  %-8s %s %s" % (r["prompt_id"], e.get("recall", ""), e.get("fields", "")))
    print("  labeled packets: %d | recall mean %s | fields mean %s" % (sum(1 for r in ok if "recall" in r["grade"]), m([r["grade"].get("recall") for r in ok]), m([r["grade"].get("fields") for r in ok])))

    print("\n== cost and time")
    chars = [cases[r["prompt_id"]]["chars"] for r in ok]
    out = [r["usage"]["output_tokens"] for r in ok]
    think = [r["usage"]["reasoning_tokens"] for r in ok]
    print("  per call: $%.4f mean ($%.4f max) | %.0fs mean (%.0fs max) | output %d tokens mean, thinking %d (%.0f%%)" % (
        statistics.mean(r["cost_usd"] for r in ok), max(r["cost_usd"] for r in ok), statistics.mean(r["latency_s"] for r in ok),
        max(r["latency_s"] for r in ok), statistics.mean(out), statistics.mean(think), 100 * sum(think) / max(sum(out), 1)))
    print("  total $%.3f | cache hit tokens %d of %d input" % (sum(r["cost_usd"] for r in rows), sum(r["usage"]["cache_read_input_tokens"] for r in ok), sum(r["usage"]["input_tokens"] for r in ok)))
    pairs = sorted(zip(chars, out))
    half = len(pairs) // 2
    print("  smaller half of packets: %d out tokens mean | larger half: %d" % (statistics.mean(o for _, o in pairs[:half]), statistics.mean(o for _, o in pairs[half:])))

    print("\n== lowest scoring packets")
    for r in sorted(ok, key=lambda r: r["grade"]["score"])[:8]:
        c = cases[r["prompt_id"]]
        print("  %-8s %.2f %-9s records %d (earlier %d)  %s" % (r["prompt_id"], r["grade"]["score"], c["kind"], r["meta"]["records"], silver[r["prompt_id"]]["n_records"],
                                                              json.dumps({k: v[:70] for k, v in r["explanation"].items() if k != "clean"}, ensure_ascii=False)[:150]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
