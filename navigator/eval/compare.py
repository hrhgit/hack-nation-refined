#!/usr/bin/env python3
"""Every comparison number of the climb, recomputed from the stored rows (nothing is read from a summary).

  python3 eval/compare.py                          # levels, paired change baseline -> last variant, every part, cost
  python3 eval/compare.py --a v2 --b v3            # compare two other variants
  python3 eval/compare.py --tries 2                # which tries count (default: tries 0 and 1, the ones every variant has)

How the numbers are made
  * a case's value is the mean of its tries; a variant's value is the mean over cases;
  * "+/-" is the 95% half-width over cases (1.96 x standard deviation / square root of the number of cases);
  * a paired change compares the same case under two variants, so case difficulty cancels out;
  * "p" is a sign-flip test on those paired differences (is a change this large likely by luck?);
  * a part that does not apply to a packet (for example recall on an unlabeled packet) is left out for that packet.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import math
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cost import cost_usd  # noqa: E402

FLOW = HERE / "extraction"
PARTS = ["score", "clean", "one_per_law", "cite_clean", "cite_num", "date_ok", "numbers_ok", "recall", "fields", "nonempty", "silver_f1"]


def read(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []


def variant_names():
    names = [p.name for p in FLOW.iterdir() if (p / "results.jsonl").exists()]
    return sorted(names, key=lambda n: (n != "baseline", int(n[1:]) if n[1:].isdigit() else 99))


def case_means(rows, part):
    d = collections.defaultdict(list)
    for r in rows:
        if part in r["grade"]:
            d[r["prompt_id"]].append(r["grade"][part])
    return {k: statistics.mean(v) for k, v in d.items()}


def half(xs):
    return 1.96 * statistics.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else float("nan")


def sign_flip_p(diffs, n=40000, seed=7):
    nz = [d for d in diffs if d != 0]
    if not nz:
        return 1.0
    rng, obs, hit = random.Random(seed), abs(sum(nz)), 0
    for _ in range(n):
        if abs(sum(d if rng.random() < 0.5 else -d for d in nz)) >= obs - 1e-12:
            hit += 1
    return hit / n


def main() -> int:
    names = variant_names()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", default="baseline")
    ap.add_argument("--b", default=names[-1])
    ap.add_argument("--tries", type=int, default=2)
    args = ap.parse_args()
    state = json.loads((FLOW / "_state.json").read_text(encoding="utf-8"))
    train, test = set(state["train_ids"]), set(state["test_ids"])
    every = train | test
    allrows = {v: read(FLOW / v / "results.jsonl") for v in names}
    rows = {v: [r for r in allrows[v] if r["rep"] < args.tries and r["status"] == "ok"] for v in names}
    for v in names:
        have = {r["prompt_id"] for r in rows[v]}
        if have != every:
            print("note: %s has no scored rows for %d case(s)" % (v, len(every - have)))

    print("LEVEL of the score, tries 0-%d (mean of case means, +/- 95%% half-width over cases)" % (args.tries - 1))
    print("%-9s %-17s %-17s %-17s" % ("variant", "test (%d)" % len(test), "train (%d)" % len(train), "all (%d)" % len(every)))
    for v in names:
        s = case_means(rows[v], "score")
        cells = []
        for ids in (test, train, every):
            vals = [s[k] for k in ids if k in s]
            cells.append("%.3f +/- %.3f" % (statistics.mean(vals), half(vals)))
        print("%-9s %-17s %-17s %-17s" % (v, *cells))

    print("\nPAIRED CHANGE of the score, %s -> %s: mean +/- half-width | cases up / down / same | sign-flip p" % (args.a, args.b))
    sa, sb = case_means(rows[args.a], "score"), case_means(rows[args.b], "score")
    for name, ids in (("test", test), ("train", train), ("all", every)):
        d = [sb[k] - sa[k] for k in sorted(ids) if k in sa and k in sb]
        up, dn = sum(x > 1e-9 for x in d), sum(x < -1e-9 for x in d)
        print("  %-5s %+.3f +/- %.3f | %2d up / %2d down / %2d same | p=%.3f" % (name, statistics.mean(d), half(d), up, dn, len(d) - up - dn, sign_flip_p(d)))

    print("\nEVERY PART, %s -> %s (level, then paired change +/- half-width; * = larger than its own half-width)" % (args.a, args.b))
    print("%-12s %-7s %-7s %-24s %-24s %s" % ("part", args.a[:7], args.b[:7], "change on test", "change on train", "change on all"))
    for part in PARTS:
        a, b = case_means(rows[args.a], part), case_means(rows[args.b], part)

        def change(ids):
            d = [b[k] - a[k] for k in ids if k in a and k in b]
            if len(d) < 2:
                return "n/a"
            m, h = statistics.mean(d), half(d)
            return "%+.3f +/- %.3f%s (n=%d)" % (m, h, "*" if abs(m) > h else " ", len(d))

        print("%-12s %.3f   %.3f   %-24s %-24s %s" % (part, statistics.mean(a.values()), statistics.mean(b.values()), change(test), change(train), change(every)))

    print("\nPERF and COST per variant (one full pass = every case at the tries above; spend = every row and failed attempt in the variant folder)")
    running = 0.0
    for v in names:
        lat = statistics.mean(r["latency_s"] for r in rows[v])
        out = statistics.mean(r["usage"]["output_tokens"] for r in rows[v])
        one_pass = sum(r["cost_usd"] for r in rows[v])
        errors = read(FLOW / v / "errors.jsonl")
        failed = sum(cost_usd(e["model"], e["usage"], dt.datetime.fromisoformat(e["ts"])) for e in errors if e.get("usage") and e.get("model"))
        spent = sum(r.get("cost_usd", 0) for r in allrows[v]) + failed
        running += spent
        t0 = [r for r in rows[v] if r["rep"] == 0]
        t1 = [r for r in rows[v] if r["rep"] == 1]
        if t0 and t1:
            m0, m1 = case_means(t0, "score"), case_means(t1, "score")
            agree = statistics.mean(1.0 if abs(m0[k] - m1[k]) <= 0.1 else 0.0 for k in m0 if k in m1)
            agree_txt = "%.0f%%" % (100 * agree)
        else:
            agree_txt = "n/a"
        print("  %-9s %.1f s/call | %.0f output tokens/call | $%.3f per pass | spend $%.3f (running %.3f) | %d failed attempts | tries agree within 0.10 on %s of cases" % (
            v, lat, out, one_pass, spent, running, len(errors), agree_txt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
