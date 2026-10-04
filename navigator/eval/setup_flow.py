"""Create eval/extraction/_state.json and metrics.md once. Never overwrites an existing state file."""
from __future__ import annotations

import json
import sys

from common import FLOW, load_cases
from cost import PRICES

METRICS = [
    ("score", "Score", "Mean of the parts below that apply to the packet (the headline)."),
    ("clean", "First pass OK", "1 if the first answer needs no correction: parses, receipt matches, nothing rejected, no law written twice."),
    ("one_per_law", "One per law", "1 minus the share of records that repeat a law already recorded in the same answer."),
    ("cite_clean", "Clean cites", "Share of accepted records whose citation is only the citation (no topic or descriptor after it)."),
    ("cite_num", "Numbered cites", "Share of accepted records whose citation has a section, chapter or bill number, counted only for documents that print such numbers."),
    ("date_ok", "Dates", "Share of enacted records whose date is present, supported by the text, and not one the code had to work out from the act's own clause."),
    ("numbers_ok", "Numbers in text", "Share of accepted records whose key_value numbers all appear in the source text (a guard against invented numbers)."),
    ("recall", "Recall (brief)", "Share of the laws listed in labels.py for this packet that the answer contains. Hand-made from the challenge brief."),
    ("fields", "Field accuracy", "Of the found labelled laws: share of expected status / effective date / key numbers that are right."),
    ("nonempty", "Non-empty", "0 only when the earlier extraction found rules in this packet and the answer has none; writing more than the earlier extraction is never punished."),
    ("silver_f1", "Cells F1", "Diagnostic only, not in the score: F1 of the (jurisdiction, category) cells against the earlier extraction."),
    ("rec_ok", "Accepted", "Diagnostic only, not in the score: accepted records / records written."),
]


def main() -> int:
    FLOW.mkdir(parents=True, exist_ok=True)
    sf = FLOW / "_state.json"
    if sf.exists() and "--force" not in sys.argv:
        print("state exists; left untouched (use --force before the baseline has been run)")
        return 0
    if sf.exists() and any((FLOW / v / "results.jsonl").exists() for v in ("baseline", "v1")):
        print("refusing --force: results exist")
        return 1
    cases = load_cases()
    state = {
        "current_round": 0, "reps": 2, "goal": None, "approve_each_round": False, "best": None,
        "train_ids": [c["id"] for c in cases if c["split"] == "train"],
        "test_ids": [c["id"] for c in cases if c["split"] == "test"],
        "harness_paths": None, "harness_sha": None,
        "metrics": [{"id": i, "kind": "float", "label": l, "scale": 1} for i, l, _ in METRICS],
        "perf_fields": [{"id": "cost_usd", "label": "Cost", "unit": "$"}, {"id": "latency_s", "label": "Latency", "unit": "s"}],
        "prices": {m: {"in": p["in_miss"], "out": p["out"]} for m, p in PRICES.items()},
    }
    from run_eval import DEFAULT_HARNESS
    state["harness_paths"] = DEFAULT_HARNESS
    sf.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    (FLOW / "metrics.md").write_text(
        "# Metrics\n\nEvery metric is in [0, 1], graded by code (eval/grader.py), never by a model.\n\n"
        + "\n".join("- **%s** (`%s`): %s" % (l, i, d) for i, l, d in METRICS)
        + "\n\nThe score is the plain mean of: clean, one_per_law, cite_clean, cite_num, date_ok, numbers_ok, recall, fields, nonempty "
          "(only those that apply to the packet). If the earlier extraction found rules in a packet and the answer has "
          "none, clean and one_per_law are forced to 0, so writing nothing cannot earn credit.\n", encoding="utf-8")
    print("created", sf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
