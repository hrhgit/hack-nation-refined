"""Prepare source packets, then extract via model API or saved subscription-model answers."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import DEFAULT_AS_OF, Paths, default_paths
from .corpus import add_extra_doc
from .ingest import pending_packets, run_ingest, write_outputs
from .packets import DEFAULT_BUDGET, DEFAULT_MAX_CHARS, DEFAULT_PASTE_CHARS, load_index, make_batches, prepare


def _paths(args) -> Paths:
    p = default_paths()
    if getattr(args, "data_dir", None):
        p.data_dir = Path(args.data_dir).expanduser().resolve()
    return p


def cmd_prepare(args) -> int:
    paths = _paths(args)
    only = [x.strip() for x in args.only.split(",")] if args.only else None
    index = prepare(paths, args.as_of, args.max_chars, args.budget, only)
    docs, pk = index["docs"], index["packets"]
    no_text = [d for d, v in docs.items() if v.get("no_text")]
    chars = sum(v["chars"] for v in pk.values())
    print("as of %s | %d documents (%d without text) | %d packets | %s characters" %
          (index["as_of"], len(docs), len(no_text), len(pk), format(chars, ",")))
    dropped = {d: len(v["dropped_blocks"]) for d, v in docs.items() if v.get("dropped_blocks")}
    if dropped:
        print("long documents trimmed (lowest-relevance blocks left out): " +
              ", ".join("%s (%d blocks)" % kv for kv in dropped.items()))
    print("packets: %s\nprompt:  %s\ngaps:    %s" % (paths.packets_dir, paths.work_dir / "PROMPT.md",
                                                     paths.work_dir / "COVERAGE_GAPS.md"))
    print("next: python run.py bundle")
    return 0


def cmd_bundle(args) -> int:
    paths = _paths(args)
    res = run_ingest(paths)
    pend = pending_packets(res)
    if args.only:
        wanted = {x.strip() for x in args.only.split(",")}
        pend = {k: v for k, v in pend.items() if k.split("-")[0] in wanted or k in wanted}
    if not pend:
        print("Nothing pending: every packet has a complete, clean answer. Run: python run.py ingest")
        return 0
    names = make_batches(paths, pend, args.paste_chars)
    print("%d pending packet(s) -> %d paste file(s) in %s" % (len(pend), len(names), paths.paste_dir))
    for n in names:
        print("  " + n)
    print("Hand a file to the model. Each one names its own answer file under %s and, if the model can run\n"
          "commands, tells it to run ingest itself. (Whole job in one go: give the model RUN_EXTRACTION.md.)"
          % paths.inbox_dir)
    return 0


def cmd_ingest(args) -> int:
    paths = _paths(args)
    res = run_ingest(paths, args.as_of)
    out = write_outputs(paths, res, args.rules_format)
    c = res.counts
    print("answer files: %d | records: %d | accepted: %d | rejected (open): %d | rules: %d | packets done: %d/%d" %
          (c["files"], c["records_parsed"], c["accepted"], c["rejected"], c["rules"], c["packets_done"], c["packets_total"]))
    print("rules:  %s\nreport: %s" % (out["rules"], out["report"]))
    if c["packets_done"] < c["packets_total"]:
        print("open packets remain: python run.py bundle")
    return 0


def cmd_status(args) -> int:
    paths = _paths(args)
    res = run_ingest(paths)
    from collections import Counter
    by = Counter(s["state"] for s in res.states.values())
    print(", ".join("%s %d" % (k, v) for k, v in sorted(by.items())) or "no packets")
    for pid, s in res.states.items():
        if s["state"] != "done" or args.all:
            print("  %-10s %-11s %s" % (pid, s["state"], s["detail"]))
    return 0


def cmd_add_doc(args) -> int:
    paths = _paths(args)
    text = Path(args.file).expanduser().read_text(encoding="utf-8", errors="replace")
    doc_id = add_extra_doc(paths, text, args.jurisdiction, args.url, args.doc_id or "", args.source_type, args.retrieved or "")
    print("added %s; now run: python run.py prepare --only %s && python run.py bundle" % (doc_id, doc_id))
    return 0


def cmd_api(args) -> int:
    from .api import ApiError, load_api_config, run_api
    try:
        paths = _paths(args)
        if not paths.index_file.exists():
            raise ApiError("尚未准备原文，请先运行 python3 run.py prepare。")
        config = load_api_config(Path(args.env_file).expanduser() if args.env_file else None,
                                 args.model, args.base_url, require_key=not args.dry_run)
        only = [x.strip() for x in args.only.split(",") if x.strip()] if args.only else None
        if args.agent:
            from .agent import run_agent_api
            return run_agent_api(paths, config, only, args.once, args.dry_run, args.rules_format, args.workers)
        return run_api(paths, config, only, args.once, args.dry_run, args.rules_format)
    except (ApiError, OSError, ValueError) as e:
        print("API 流程停止：%s" % e, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n已停止。已保存的回答仍在，下次运行会继续处理未完成分包。", file=sys.stderr)
        return 130


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="run.py", description=__doc__)
    ap.add_argument("--data-dir", help="starter-pack folder that contains corpus/ (default: auto-detect)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare", help="clean the corpus and cut it into packets")
    p.add_argument("--as-of", default=DEFAULT_AS_OF)
    p.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS, help="largest packet")
    p.add_argument("--budget", type=int, default=DEFAULT_BUDGET, help="documents above this lose their least relevant blocks")
    p.add_argument("--only", help="comma-separated doc_ids to (re)prepare, keeping the rest")
    p.set_defaults(fn=cmd_prepare)

    p = sub.add_parser("bundle", help="make paste-ready files for the packets that still need an answer")
    p.add_argument("--paste-chars", type=int, default=DEFAULT_PASTE_CHARS, help="target size of one paste file")
    p.add_argument("--only", help="comma-separated doc_ids or packet_ids")
    p.set_defaults(fn=cmd_bundle)

    p = sub.add_parser("api", help="extract pending packets directly through DeepSeek/model API")
    p.add_argument("--model", help="override NAV_API_MODEL (default: deepseek-flash)")
    p.add_argument("--base-url", help="override NAV_API_BASE_URL (default: https://api.deepseek.com)")
    p.add_argument("--env-file", help="configuration file (default: navigator/.env)")
    p.add_argument("--only", help="comma-separated doc_ids or packet_ids; completed packets are skipped")
    p.add_argument("--once", action="store_true", help="one pass, leaving validation failures for a later run")
    p.add_argument("--dry-run", action="store_true", help="show pending inputs without calling the API or requiring a key")
    p.add_argument("--rules-format", choices=["wrapped", "list"], default="wrapped")
    p.add_argument("--agent", action="store_true", help="step-by-step mode: the model reads reference cards when it needs them and checks its own records (prompts/agent/)")
    p.add_argument("--workers", type=int, default=1, help="packets worked on at the same time in --agent mode")
    p.set_defaults(fn=cmd_api)

    p = sub.add_parser("ingest", help="validate saved answers and write outputs/rules.json")
    p.add_argument("--as-of", default=None)
    p.add_argument("--rules-format", choices=["wrapped", "list"], default="wrapped",
                   help="wrapped = {'rules': [...]} like the template; list = bare list like the README")
    p.set_defaults(fn=cmd_ingest)

    p = sub.add_parser("status", help="which packets are done")
    p.add_argument("--all", action="store_true")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("add-doc", help="register a document you obtained yourself (e.g. the hour-16 ordinance)")
    p.add_argument("--file", required=True)
    p.add_argument("--jurisdiction", required=True, help='e.g. "Cambridge, MA"')
    p.add_argument("--url", required=True)
    p.add_argument("--doc-id", default="")
    p.add_argument("--source-type", default="official")
    p.add_argument("--retrieved", default="")
    p.set_defaults(fn=cmd_add_doc)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
