#!/usr/bin/env python3
"""Run the extraction eval: every case x rep goes through the real API path (nav.api.ChatClient + the live
prompt files) and is graded by grader.py. Rows are written as each case completes; a restart skips what is done.

  python3 eval/run_eval.py --variant baseline --reps 2
  python3 eval/run_eval.py --variant v1 --split all
  python3 eval/run_eval.py --variant baseline --dry-run

No wall-clock ceiling and no in-process retries (the repo's AGENTS.md asks for none): an attempt that fails goes to
errors.jsonl with a failure class and is retried by simply running the same command again.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import FLOW, HERE, ROOT, load_cases, load_ctx
from cost import cost_usd
from grader import grade
from nav.api import ApiError, ChatClient, _answer, load_api_config
from nav.packets import render_prompt

DEFAULT_HARNESS = [
    "eval/common.py", "eval/grader.py", "eval/labels.py", "eval/run_eval.py", "eval/cost.py", "eval/cases.json",
    "eval/silver.json", "nav/ingest.py", "nav/facts.py", "nav/spans.py", "nav/parse.py", "nav/schema.py",
    "nav/keywords.py", "nav/api.py", "work/index.json", "eval/rehearsal/manifest.csv", "eval/rehearsal/oracle.jsonl",
    "eval/rehearsal/text/R001.txt", "eval/rehearsal/text/R002.txt", "eval/rehearsal/text/R003.txt", "eval/rehearsal/text/R004.txt",
    "eval/rehearsal/packets/R001-01.md", "eval/rehearsal/packets/R002-01.md", "eval/rehearsal/packets/R003-01.md",
    "eval/rehearsal/packets/R004-01.md",
]


def eprint(*a: Any) -> None:
    print(*a, file=sys.stderr)


def harness_sha(state: Dict[str, Any]) -> str:
    h = hashlib.sha256()
    for rel in sorted(set(state.get("harness_paths") or DEFAULT_HARNESS)):
        p = ROOT / rel
        h.update(rel.encode() + b"\0" + (hashlib.sha256(p.read_bytes()).digest() if p.exists() else b"missing") + b"\n")
    return h.hexdigest()


def gate(flow: Path, approve: bool) -> None:
    sf = flow / "_state.json"
    state = json.loads(sf.read_text(encoding="utf-8"))
    sha = harness_sha(state)
    if state.get("harness_sha") == sha:
        return
    if approve:
        state["harness_sha"] = sha
        sf.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        print("harness recorded:", sha[:12])
        return
    if state.get("harness_sha") is None:
        eprint("The eval harness has not been approved yet. Review eval/*.py and the validator it reuses, then run once with --approve-harness.")
    else:
        eprint("The harness changed since it was approved (%s -> %s). Review the diff, then re-run with --approve-harness." % (
            str(state["harness_sha"])[:12], sha[:12]))
    sys.exit(2)


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def usage_of(body: Dict[str, Any]) -> Dict[str, Any]:
    u = body.get("usage") or {}
    details = u.get("completion_tokens_details") or {}
    return {"input_tokens": u.get("prompt_tokens", 0), "output_tokens": u.get("completion_tokens", 0),
            "cache_read_input_tokens": u.get("prompt_cache_hit_tokens", 0),
            "cache_miss_input_tokens": u.get("prompt_cache_miss_tokens"),
            "reasoning_tokens": details.get("reasoning_tokens", 0)}


def ci_half(xs: List[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    m = sum(xs) / len(xs)
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))
    return 1.96 * sd / math.sqrt(len(xs))


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--flow", default=str(FLOW))
    ap.add_argument("--variant", required=True)
    ap.add_argument("--reps", type=int)
    ap.add_argument("--split", choices=["all", "train", "test"], default="all")
    ap.add_argument("--cases", help="comma-separated packet ids")
    ap.add_argument("--model")
    ap.add_argument("--base-url")
    ap.add_argument("--env-file")
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--approve-harness", action="store_true", help="record the harness hash (a person runs this, never an unattended round)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--system-prompt-file", help="control runs only: use this text instead of the live prompt files")
    ap.add_argument("--explore", action="store_true",
                    help="attended exploration: skips the harness gate, and may not write into the climb's own folder")
    args = ap.parse_args(argv)

    flow = Path(args.flow)
    if args.explore:
        if flow.resolve() == FLOW.resolve():
            eprint("--explore may not write into %s; give it its own --flow folder." % FLOW)
            return 1
        flow.mkdir(parents=True, exist_ok=True)
        if not (flow / "_state.json").exists():
            st = json.loads((FLOW / "_state.json").read_text(encoding="utf-8"))
            st.update({"harness_sha": None, "explore": True})
            (flow / "_state.json").write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
    elif args.approve_harness:
        gate(flow, True)
        return 0
    elif not args.dry_run:    # a dry run spends nothing, so it needs no approval
        gate(flow, False)
    state = json.loads((flow / "_state.json").read_text(encoding="utf-8"))
    reps = args.reps or state.get("reps") or 2
    ctx = load_ctx()
    cases = load_cases()
    if args.cases:
        want = {x.strip() for x in args.cases.split(",")}
        cases = [c for c in cases if c["id"] in want]
    elif args.split != "all":
        cases = [c for c in cases if c["split"] == args.split]
    vdir = flow / args.variant
    results_path, errors_path = vdir / "results.jsonl", vdir / "errors.jsonl"
    done = {(r["prompt_id"], r["rep"]) for r in read_jsonl(results_path)}
    todo = [(c, k) for c in cases for k in range(reps) if (c["id"], k) not in done]

    config = load_api_config(Path(args.env_file) if args.env_file else None, args.model, args.base_url, require_key=not args.dry_run)
    prompt = Path(args.system_prompt_file).read_text(encoding="utf-8") if args.system_prompt_file else render_prompt(ctx.as_of)
    est_in = sum((len(prompt) + ctx.index["packets"][c["id"]]["chars"]) / 4 for c, _ in todo)
    print("resolved: %d cases x %d reps on %s = %d calls to run (%d already done) | system prompt %d chars | ~%.0fk input tokens" % (
        len(cases), reps, config.model, len(todo), len(done), len(prompt), est_in / 1000))
    if args.dry_run or not todo:
        return 0

    (vdir / "traces").mkdir(parents=True, exist_ok=True)   # only a real run creates folders
    client = ChatClient(config)
    lock = threading.Lock()
    counter = {"done": 0, "errors": 0}
    t_start = time.time()

    def record_error(c: Dict[str, Any], rep: int, klass: str, msg: str, body: Optional[Dict[str, Any]] = None) -> None:
        row = {"prompt_id": c["id"], "rep": rep, "class": klass, "error": msg[:400], "ts": dt.datetime.now(dt.timezone.utc).isoformat()}
        if body:
            row["model"], row["usage"] = body.get("model"), usage_of(body)
        with lock:
            with errors_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            counter["errors"] += 1

    def one(item) -> None:
        c, rep = item
        packet_text = ctx.packet_file(c["id"]).read_text(encoding="utf-8")
        t0 = time.time()
        try:
            body = client.complete(prompt, packet_text)
        except ApiError as e:
            record_error(c, rep, "harness_or_serving_error", str(e))
            return
        except Exception as e:  # a worker must never take the whole run down
            record_error(c, rep, "harness_or_serving_error", "%s: %s" % (type(e).__name__, e))
            return
        latency = time.time() - t0
        try:
            text, reason = _answer(body)
        except ApiError as e:
            record_error(c, rep, "harness_or_serving_error", str(e), body)
            return
        served = str(body.get("model") or "")
        want = config.model.split("-")[-1]
        if want not in served:
            record_error(c, rep, "served_model_mismatch", "asked for %s, served by %s" % (config.model, served), body)
            return
        with lock:
            res = grade(ctx, c["id"], text, reason)
        ts = dt.datetime.now(dt.timezone.utc)
        usage = usage_of(body)
        message = (body.get("choices") or [{}])[0].get("message") or {}
        assistant = {"role": "assistant", "content": text}
        if message.get("reasoning_content"):
            assistant["thinking"] = message["reasoning_content"]
        trace = [{"role": "system", "content": prompt}, {"role": "user", "content": packet_text}, assistant]
        (vdir / "traces" / ("%s_rep%d.json" % (c["id"], rep))).write_text(json.dumps(trace, ensure_ascii=False, indent=1), encoding="utf-8")
        row = {"prompt_id": c["id"], "rep": rep, "prompt": packet_text, "tags": c["tags"], "grade": res["grade"],
               "explanation": res["explanation"], "model": served, "latency_s": round(latency, 2), "usage": usage,
               "cost_usd": round(cost_usd(served, usage, ts), 6), "stop_reason": reason, "status": res["status"],
               "meta": {"records": res["records"], "accepted": res["accepted"], "rejected": res["rejected"],
                        "ts": ts.isoformat(), "split": c["split"]}}
        with lock:
            with results_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            counter["done"] += 1

    stop = threading.Event()

    def ticker() -> None:
        while not stop.wait(30):
            k = counter["done"] + counter["errors"]
            left = (time.time() - t_start) / max(k, 1) * (len(todo) - k)
            line = "%d/%d done (%d errors) ~%ds left" % (k, len(todo), counter["errors"], left)
            print(line, flush=True)
            (vdir / "progress.txt").write_text(line + "\n")

    th = threading.Thread(target=ticker, daemon=True)
    th.start()
    try:
        with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
            list(pool.map(one, todo))
    finally:
        stop.set()

    rows = read_jsonl(results_path)
    ok = [r for r in rows if r["status"] == "ok"]
    summary = {"description": ("control prompt from %s" % args.system_prompt_file) if args.system_prompt_file
               else ("baseline" if args.variant == "baseline" else "see change.md"),
               "target": "system_prompt", "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "model": config.model}
    old = vdir / "summary.json"
    if old.exists():
        prev = json.loads(old.read_text(encoding="utf-8"))
        summary = {**summary, **{k: v for k, v in prev.items() if k in ("description", "target", "label", "suspicious")}}
    old.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    by_case: Dict[str, List[float]] = {}
    for r in ok:
        by_case.setdefault(r["prompt_id"], []).append(r["grade"]["score"])
    means = [sum(v) / len(v) for v in by_case.values()]
    spend = sum(r.get("cost_usd", 0) for r in rows)
    print("%s: %d rows ok, %d errors this run | mean score %.3f +/- %.3f over %d cases | spend so far $%.3f" % (
        args.variant, len(ok), counter["errors"], sum(means) / max(len(means), 1), ci_half(means), len(means), spend))
    return 3 if counter["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
