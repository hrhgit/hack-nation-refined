#!/usr/bin/env python3
"""Run the packets of the conditions answer key through the real API path and keep the raw answers (traces).

  python3 eval/conditions_run.py --variant now --reps 2 --dry-run          # what would run, spends nothing
  python3 eval/conditions_run.py --variant now --reps 2                    # live prompt files
  python3 eval/conditions_run.py --variant cand --prompt-file my_prompt.md  # a candidate prompt, same placeholders

Answers go to <flow>/<variant>/traces/<packet>_rep<k>.json, one row per call to <flow>/<variant>/calls.jsonl, failures to
errors.jsonl. A second run skips what exists. Grade them with `python3 eval/conditions_check.py --variant now`.
This is an exploration tool: it never writes into eval/extraction/ and touches no harness file.
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
from common import ROOT, load_ctx  # noqa: E402
from cond_labels import COND_LABELS  # noqa: E402
from cost import cost_usd  # noqa: E402
from nav.api import ApiError, ChatClient, _answer, load_api_config  # noqa: E402
from nav.config import KNOWN_JURISDICTIONS  # noqa: E402

DEFAULT_FLOW = HERE / "explore" / "conditions"


def render(prompt_file: Path, primer_file: Path, as_of: str) -> str:
    raw = prompt_file.read_text(encoding="utf-8")
    if "{{PRIMER}}" in raw:
        raw = raw.replace("{{PRIMER}}", primer_file.read_text(encoding="utf-8").strip())
    return (raw.replace("{{AS_OF}}", as_of).replace("{{JURISDICTIONS}}", ", ".join('"%s"' % j for j in KNOWN_JURISDICTIONS)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--flow", default=str(DEFAULT_FLOW))
    ap.add_argument("--variant", required=True)
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--packets", help="comma-separated packet ids (default: every packet in the answer key)")
    ap.add_argument("--prompt-file", default=str(ROOT / "prompts" / "extract_prompt.md"))
    ap.add_argument("--primer-file", default=str(ROOT / "prompts" / "primer.md"))
    ap.add_argument("--model")
    ap.add_argument("--env-file")
    ap.add_argument("--concurrency", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    flow = Path(args.flow)
    if flow.resolve() == (HERE / "extraction").resolve():
        print("this tool may not write into eval/extraction/", file=sys.stderr)
        return 1
    ctx = load_ctx()
    ids = [x.strip() for x in args.packets.split(",")] if args.packets else sorted({l["packet"] for l in COND_LABELS})
    missing = [p for p in ids if p not in ctx.index["packets"]]
    if missing:
        print("unknown packets (run `python3 run.py prepare` first): %s" % ", ".join(missing), file=sys.stderr)
        return 1
    vdir = flow / args.variant
    todo = [(pid, k) for pid in ids for k in range(args.reps) if not (vdir / "traces" / ("%s_rep%d.json" % (pid, k))).exists()]
    prompt = render(Path(args.prompt_file), Path(args.primer_file), ctx.as_of)
    config = load_api_config(Path(args.env_file) if args.env_file else None, args.model, None, require_key=not args.dry_run)
    est_in = sum((len(prompt) + ctx.index["packets"][p]["chars"]) / 4 for p, _ in todo)
    print("%d packets x %d tries on %s = %d calls to run (%d already done) | prompt %d chars | ~%.0fk input tokens" % (
        len(ids), args.reps, config.model, len(todo), len(ids) * args.reps - len(todo), len(prompt), est_in / 1000))
    if args.dry_run or not todo:
        return 0
    (vdir / "traces").mkdir(parents=True, exist_ok=True)
    client, lock, spend = ChatClient(config), threading.Lock(), [0.0]

    def log(name: str, row: dict) -> None:
        with lock:
            with (vdir / name).open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    def one(item) -> None:
        pid, rep = item
        packet = ctx.packet_file(pid).read_text(encoding="utf-8")
        t0 = time.time()
        try:
            body = client.complete(prompt, packet)
            text, reason = _answer(body)
        except ApiError as e:
            log("errors.jsonl", {"prompt_id": pid, "rep": rep, "error": str(e)[:300]})
            return
        except Exception as e:  # one failed call must not take the others down
            log("errors.jsonl", {"prompt_id": pid, "rep": rep, "error": "%s: %s" % (type(e).__name__, e)})
            return
        usage = body.get("usage") or {}
        u = {"input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"),
             "cache_read_input_tokens": usage.get("prompt_cache_hit_tokens"), "cache_miss_input_tokens": usage.get("prompt_cache_miss_tokens")}
        cost = cost_usd(str(body.get("model") or config.model), u, dt.datetime.now(dt.timezone.utc))
        trace = [{"role": "system", "content": prompt}, {"role": "user", "content": packet}, {"role": "assistant", "content": text}]
        (vdir / "traces" / ("%s_rep%d.json" % (pid, rep))).write_text(json.dumps(trace, ensure_ascii=False, indent=1), encoding="utf-8")
        log("calls.jsonl", {"prompt_id": pid, "rep": rep, "finish": reason, "usage": u, "cost_usd": round(cost, 6), "latency_s": round(time.time() - t0, 1)})
        with lock:
            spend[0] += cost
            print("  %s try %d done (%s, %.0fs)" % (pid, rep, reason, time.time() - t0), flush=True)

    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        list(pool.map(one, todo))
    print("spend this run about $%.3f" % spend[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
