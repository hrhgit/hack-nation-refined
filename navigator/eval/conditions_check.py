#!/usr/bin/env python3
"""Do the conditions the extraction wrote give the right answer for made-up addresses?

  python3 eval/conditions_check.py --variant now                    # eval/explore/conditions/now
  python3 eval/conditions_check.py --flow eval/explore/contract_v2 --variant new_prompt
  python3 eval/conditions_check.py --variant now --verbose          # every failed check

Reads stored answers only (no API call). Each answer is validated with the CURRENT ingest code, the law named by a label
is found in it, and the label's probes (eval/cond_labels.py) are run through the real lookup engine. Checks per label:
the law exists, its status / dates / relations when the label gives them, and one check per probe.
Wrong exclusion = a probe where the law was left out although the answer key says it covers the address.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import load_ctx  # noqa: E402
from cond_labels import COND_LABELS  # noqa: E402
from lookup.engine import LookupEngine  # noqa: E402
from nav.parse import classify, extract_json_objects  # noqa: E402

DEFAULT_FLOW = HERE / "explore" / "conditions"
CITY_FOR_STATE = {"CA": "Los Angeles, CA", "NJ": "Newark, NJ", "MA": "Boston, MA"}


def records(ctx, text):
    """Rules the current ingest accepts from one stored answer, with the reasons for the ones it does not."""
    objs, _ = extract_json_objects(text)
    rules, rejected = [], []
    for raw in objs:
        if classify(raw) != "record":
            continue
        rule, errors, _ = ctx.validator.check(raw)
        if rule is None:
            rejected.append({"citation": raw.get("citation"), "errors": errors})
        else:
            rules.append(rule)
    return rules, rejected


def find(label, rules):
    rx = re.compile(label["cite_re"], re.I)
    hits = [r for r in rules if r["jurisdiction"] == label["jurisdiction"] and r["category"] == label["category"]
            and rx.search((r["citation"] or "") + " " + (r["title"] or ""))]
    return hits[0] if hits else None


def outcome(rule, facts, as_of):
    state = rule["jurisdiction"] if rule["level"] == "state" else rule["jurisdiction"].rsplit(", ", 1)[-1]
    city = rule["jurisdiction"] if rule["level"] == "city" else CITY_FOR_STATE[state]
    address = {"state": state, "legal_city": city, "resolved_by": "geocoder", **facts}
    probe_rule = dict(rule, team_rule_id="probe")
    rows = LookupEngine([probe_rule], {"P": address}, precedence=[], review=[]).lookup("P", as_of)
    return rows[0]["result"] if rows else "excluded"


def check_label(ctx, label, text):
    """Returns (checks, wrong_exclusions): checks is a list of (name, passed, detail)."""
    rules, rejected = records(ctx, text)
    rule = find(label, rules)
    if rule is None:
        why = "no matching record" + ("; rejected: %s" % json.dumps(rejected, ensure_ascii=False)[:200] if rejected else "")
        return ([("found", False, why)] + [("probe: " + p["why"], False, "law missing") for p in label["probes"]]
                + [("exact: " + p["why"], False, "law missing") for p in label["probes"] if p["exact"] is not None]), sum("excluded" not in p["ok"] for p in label["probes"])
    checks = [("found", True, rule["citation"])]
    for key in ("lifecycle", "effective_date", "valid_through"):
        if key in label:
            checks.append((key, rule.get(key) == label[key], "wanted %s, got %s" % (label[key], rule.get(key))))
    if "relations" in label:
        got = {r["type"] for r in rule.get("relations") or []}
        want = label["relations"]
        for t in want["require"]:
            checks.append(("relation " + t, t in got, "got %s" % sorted(got)))
        for t in want["forbid"]:
            checks.append(("no relation " + t, t not in got, "got %s" % sorted(got)))
    wrong = 0
    for p in label["probes"]:
        got = outcome(rule, p["facts"], p["as_of"])
        ok = got in p["ok"]
        if not ok and got == "excluded":
            wrong += 1
        shown = {k: v for k, v in p["facts"].items() if v is not None}
        checks.append(("probe: " + p["why"], ok, "facts %s, acceptable %s, got %s" % (shown, "/".join(sorted(p["ok"])), got)))
        if p["exact"] is not None:
            checks.append(("exact: " + p["why"], got == p["exact"], "facts %s, best answer %s (%s), got %s" % (shown, p["exact"], p["basis"][:90], got)))
    return checks, wrong


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--flow", default=str(DEFAULT_FLOW))
    ap.add_argument("--variant", required=True)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--tries", type=int, default=None, help="use tries 0..N-1 (default: every stored try)")
    ap.add_argument("--intrinsic", action="store_true",
                    help="also grade every stored answer with the climb's grader parts that need no answer key (works for new documents too)")
    args = ap.parse_args()
    vdir = Path(args.flow) / args.variant
    ctx = load_ctx()
    total = passed = wrong_total = exact_total = exact_passed = 0
    per_label, failures = [], []
    missing_rules = 0
    for label in COND_LABELS:
        files = sorted((vdir / "traces").glob("%s_rep*.json" % label["packet"]))
        if args.tries is not None:
            files = [f for f in files if int(re.search(r"_rep(\d+)", f.name).group(1)) < args.tries]
        if not files:
            per_label.append((label["id"], None))
            continue
        lp = lt = ep = et = 0
        for f in files:
            text = json.loads(f.read_text(encoding="utf-8"))[2]["content"]
            checks, wrong = check_label(ctx, label, text)
            wrong_total += wrong
            missing_rules += any(name == "found" and not ok for name, ok, _ in checks)
            for name, ok, detail in checks:
                if name.startswith("exact:"):
                    et += 1
                    ep += ok
                else:
                    lt += 1
                    lp += ok
                if not ok:
                    failures.append((label["id"], f.name.split("_rep")[1][:1], name, detail))
        per_label.append((label["id"], (lp, lt, len(files), ep, et)))
        total += lt
        passed += lp
        exact_total += et
        exact_passed += ep
    print("%-14s %s" % ("label", "safe checks (no law hidden) | exact answers"))
    for lid, r in per_label:
        print("%-14s %s" % (lid, "not run" if r is None else "%d of %d (%d tries) | %s" % (r[0], r[1], r[2], "%d of %d" % (r[3], r[4]) if r[4] else "-")))
    print("%-14s safe %d of %d = %.3f | exact %d of %d = %.3f | wrong exclusions %d" % (
        "ALL", passed, total, passed / max(total, 1), exact_passed, exact_total, exact_passed / max(exact_total, 1), wrong_total))
    print("missing rule answers: %d (included in wrong exclusions when the law should remain visible)" % missing_rules)
    if args.verbose or failures:
        print("\nfailed checks:")
        for lid, rep, name, detail in failures:
            print("  %-12s try %s  %s -> %s" % (lid, rep, name, detail[:200]))
    if args.intrinsic:
        from grader import grade
        parts = ("clean", "one_per_law", "cite_clean", "cite_num", "date_ok", "numbers_ok")
        sums = {k: [] for k in parts}
        weak = []
        for f in sorted((vdir / "traces").glob("*_rep*.json")):
            pid = f.name.split("_rep")[0]
            res = grade(ctx, pid, json.loads(f.read_text(encoding="utf-8"))[2]["content"], "stop")
            for k in parts:
                if res["grade"].get(k) is not None:
                    sums[k].append(res["grade"][k])
            low = {k: v for k, v in res["explanation"].items() if k in parts}
            if low:
                weak.append((f.name[:-5], low))
        print("\nparts that need no answer key, over %d stored answers:" % len(list((vdir / "traces").glob("*_rep*.json"))))
        for k in parts:
            print("  %-12s %s" % (k, "%.3f (n=%d)" % (sum(sums[k]) / len(sums[k]), len(sums[k])) if sums[k] else "-"))
        for name, low in weak:
            print("  weak: %-14s %s" % (name, json.dumps(low, ensure_ascii=False)[:230]))
    summary = {"scoring_version": "conditions-v2-missing-counted", "missing_rules": missing_rules, "variant": args.variant, "passed": passed, "total": total, "score": passed / max(total, 1),
               "exact_passed": exact_passed, "exact_total": exact_total, "wrong_exclusions": wrong_total,
               "labels": {lid: (None if r is None else {"passed": r[0], "total": r[1], "tries": r[2], "exact_passed": r[3], "exact_total": r[4]}) for lid, r in per_label}}
    (vdir / "conditions_summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
