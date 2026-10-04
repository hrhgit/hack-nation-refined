#!/usr/bin/env python3
"""Step-by-step extraction ("agent" run) over the answer-key packets, kept as traces for grading. Uses nav/agent.py, the same code as
`python3 run.py api --agent`, so what is measured here is what the pipeline runs.

  python3 eval/agent_run.py --variant agent --reps 2 --dry-run
  python3 eval/agent_run.py --variant agent --reps 2
  python3 eval/agent_run.py --variant agent_nocheck --tools cards    # only the cards (ablation)
  python3 eval/agent_run.py --variant agent_nocards --tools check    # only the self-check (ablation)
  python3 eval/conditions_check.py --variant agent --intrinsic       # grade it exactly like the single-shot variants

Each trace is [system, user, final answer, agent_log]; the grader reads element 2, so these grade like single-shot answers.
Records the steps, cards read, self-checks, cost and time of every run in calls.jsonl. No cap on the number of steps.
Exploration tool: writes under eval/explore/ only and touches no harness file.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import load_ctx  # noqa: E402
from cond_labels import COND_LABELS  # noqa: E402
from cost import cost_usd  # noqa: E402
from nav.agent import card_names, converse, load_cards, make_post, render_core  # noqa: E402
from nav.api import ApiError, load_api_config  # noqa: E402

DEFAULT_FLOW = HERE / "explore" / "conditions"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--flow", default=str(DEFAULT_FLOW))
    ap.add_argument("--variant", required=True)
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--packets")
    ap.add_argument("--tools", default="cards,check", help="comma list from: cards, check")
    ap.add_argument("--model")
    ap.add_argument("--env-file")
    ap.add_argument("--concurrency", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    tools = tuple(t.strip() for t in args.tools.split(",") if t.strip())
    flow = Path(args.flow)
    if flow.resolve() == (HERE / "extraction").resolve():
        print("this tool may not write into eval/extraction/", file=sys.stderr)
        return 1
    ctx = load_ctx()
    ids = [x.strip() for x in args.packets.split(",")] if args.packets else sorted({l["packet"] for l in COND_LABELS})
    vdir = flow / args.variant
    todo = [(p, k) for p in ids for k in range(args.reps) if not (vdir / "traces" / ("%s_rep%d.json" % (p, k))).exists()]
    system = render_core(ctx.as_of)
    config = load_api_config(Path(args.env_file) if args.env_file else None, args.model, None, require_key=not args.dry_run)
    print("%d packets x %d tries on %s = %d runs (%d done) | core prompt %d chars | tools: %s | cards: %s" % (
        len(ids), args.reps, config.model, len(todo), len(ids) * args.reps - len(todo), len(system), ",".join(tools), ", ".join(card_names())))
    if args.dry_run or not todo:
        return 0
    (vdir / "traces").mkdir(parents=True, exist_ok=True)
    post, cards = make_post(config), load_cards()
    check_lock, io_lock, spend = threading.Lock(), threading.Lock(), [0.0]

    def log(name, row):
        with io_lock:
            with (vdir / name).open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    def one(item):
        pid, rep = item
        packet = ctx.packet_file(pid).read_text(encoding="utf-8")
        t0 = time.time()
        try:
            final, info = converse(post, system, packet, cards, ctx.validator, check_lock, tools)
        except (ApiError, OSError) as e:
            log("errors.jsonl", {"prompt_id": pid, "rep": rep, "error": str(e)[:200]})
            return
        cost = sum(cost_usd(config.model, {"input_tokens": u.get("prompt_tokens"), "output_tokens": u.get("completion_tokens"),
                                           "cache_read_input_tokens": u.get("prompt_cache_hit_tokens"),
                                           "cache_miss_input_tokens": u.get("prompt_cache_miss_tokens")}, dt.datetime.now(dt.timezone.utc))
                   for u in info["usage"])
        trace = [{"role": "system", "content": system}, {"role": "user", "content": packet}, {"role": "assistant", "content": final},
                 {"role": "agent_log", "steps": info["steps"], "cards_read": info["cards_read"], "checks": info["checks"], "messages": info["messages"]}]
        (vdir / "traces" / ("%s_rep%d.json" % (pid, rep))).write_text(json.dumps(trace, ensure_ascii=False, indent=1), encoding="utf-8")
        log("calls.jsonl", {"prompt_id": pid, "rep": rep, "steps": info["steps"], "cards_read": info["cards_read"], "checks": info["checks"],
                            "cost_usd": round(cost, 6), "latency_s": round(time.time() - t0, 1)})
        with io_lock:
            spend[0] += cost
            print("  %s try %d done: %d steps, cards %s, %d checks (%.0fs, $%.3f)" % (
                pid, rep, info["steps"], info["cards_read"] or "-", info["checks"], time.time() - t0, cost), flush=True)

    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        list(pool.map(one, todo))
    print("spend this run about $%.3f" % spend[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
