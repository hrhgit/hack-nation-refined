"""JSON protocol around the frozen Python implementation; used only by tests.

There is deliberately no model request here. All mutations target the invented
corpus in a temporary directory. The real project is only read.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

def normalize(value):
    if dataclasses.is_dataclass(value):
        value = dataclasses.asdict(value)
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value

def digest(value):
    raw = json.dumps(normalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def execute(case):
    from nav import conditions, facts, parse, schema, textutil, chapters
    from nav.spans import DocIndex
    from lookup.common import date_interval, query_date, matches
    from lookup.addresses import unit_lower_bound, integer, parse_batch, load_addresses
    from lookup.engine import LookupEngine, load_rules
    from changes.engine import ChangeTracker
    op, a = case["op"], case.get("args", {})
    if op == "parse":
        return parse.extract_json_objects(a["text"])
    if op == "clean":
        return textutil.clean_text(a["text"])
    if op == "blocks":
        blocks = textutil.split_blocks(a["text"])
        return {"blocks": [dataclasses.asdict(b) for b in blocks], "keep": textutil.select_blocks(blocks, a["budget"])}
    if op == "span":
        return DocIndex(a["body"]).locate(a["span"])
    if op == "schema":
        return schema.check(a["value"], a["schema"])
    if op == "facts":
        name = a["name"]
        if name == "normalize_jurisdiction":
            from nav.config import KNOWN_JURISDICTIONS, STATE_NAMES
            return facts.normalize_jurisdiction(a["value"], KNOWN_JURISDICTIONS, STATE_NAMES)
        if name == "act_dates":
            result = facts.act_dates(a["value"])
            return vars(result) if result else None
        return getattr(facts, name)(a["value"])
    if op == "date_interval":
        return [d.isoformat() for d in date_interval(a["value"])]
    if op == "query_date":
        return query_date(a["value"]).isoformat()
    if op == "chapter":
        return chapters.chapter_of(a["value"])
    if op == "api_endpoint":
        from nav.api import ApiConfig
        return ApiConfig("test-key", base_url=a["value"]).endpoint
    if op == "api_answer":
        from nav.api import _answer
        return _answer(a["value"])
    if op == "chat_complete":
        from nav.api import ApiConfig, ChatClient
        return ChatClient(ApiConfig("test-secret", base_url=a["base_url"])).complete("test prompt", "test packet")
    if op == "api_select":
        from nav.api import _select
        return _select(a["pending"], a["index"], a["only"])
    if op == "check_final":
        from nav.agent import check_final
        check_final(a["text"], "D100-01")
        return True
    if op == "cards":
        from nav.agent import load_cards, render_core, tool_specs
        from nav.packets import render_prompt
        return {"cards": load_cards(), "core": render_core("2026-10-01"), "tools": tool_specs(),
                "prompt": render_prompt("2026-10-01")}
    if op == "conditions":
        warns = []
        locate = (lambda q: (DocIndex(a["body"]).locate(q).text if DocIndex(a["body"]).locate(q) else None)) if "body" in a else None
        result = conditions.parse(a["value"], warns, set(a["dates"]) if "dates" in a else None,
                                  set(a["nums"]) if "nums" in a else None, locate)
        return {"value": result, "warnings": warns}
    if op == "relations":
        warns = []
        idx = DocIndex(a["body"])
        def locate(q):
            hit = idx.locate(q)
            return hit.text if hit else None
        return {"value": conditions.parse_relations(a["value"], warns, locate), "warnings": warns}
    if op == "integer":
        return integer(a["value"], "units")
    if op == "unit_lower_bound":
        return unit_lower_bound(a["value"])
    if op == "parse_batch":
        return parse_batch(a["text"], set(a["ids"]))
    if op == "engine":
        engine = LookupEngine(a["rules"], a["addresses"], a.get("precedence", []), a.get("review", []))
        output = engine.all(a.get("as_of", "2026-10-01"))
        return {"all": output, "exported": engine.exported_rules(a.get("as_of", "2026-10-01"), output[0])} if a.get("export") else output
    if op == "changes":
        engine = LookupEngine(a["rules"], a["addresses"], a.get("precedence", []), a.get("review", []))
        return ChangeTracker(engine, a["tests"], a["rule_map"]).run(a.get("date_overrides"))
    if op == "real_all":
        engine = LookupEngine.from_files()
        value = engine.all(a["as_of"])
        return {"addresses": len(engine.addresses), "rules": len(engine.rules), "sha256": digest(value)}
    if op == "real_changes":
        return ChangeTracker(LookupEngine.from_files()).run()
    if op == "real_rules":
        return LookupEngine.from_files().exported_rules()
    if op == "real_review":
        from lookup.review import render
        return render(LookupEngine.from_files())
    if op == "real_requests":
        from lookup.cli import requests_report
        report = {}
        engine = LookupEngine(load_rules(report=report), __import__("lookup.common", fromlist=["read_json"]).read_json(ROOT / "work" / "addresses_resolved.json"))
        return requests_report(engine, engine.all()[1], ChangeTracker(engine).run()[1], report)
    if op == "real_census":
        from lookup.addresses import CensusResolver
        return CensusResolver(offline=True).resolve(load_addresses())
    if op == "census":
        from lookup.addresses import CensusResolver
        return CensusResolver(a["cache_dir"], offline=a.get("offline", False), refresh=a.get("refresh", False),
                              mode=a.get("mode", "single"), base_url=a["base_url"]).resolve(a["addresses"], a.get("aliases", {}))
    if op == "real_packets":
        from nav.config import default_paths
        from nav.corpus import load_corpus
        from nav.packets import build_doc_packets, render_packet
        values = {}
        for did, doc in load_corpus(default_paths()).items():
            packets, stats = build_doc_packets(doc)
            values[did] = {"stats": stats, "packets": [render_packet(p, doc, "2026-10-01") for p in packets]}
        return {"documents": len(values), "sha256": digest(values)}
    if op == "real_ingest":
        from nav.config import default_paths
        from nav.ingest import run_ingest, pending_packets
        res = run_ingest(default_paths(), persist_ids=False)
        return {"rules": res.rules, "counts": res.counts, "states": res.states, "pending": pending_packets(res),
                "rejected": res.rejected, "problems": res.problems, "parse_problems": res.parse_problems}
    if op == "web":
        from web.server import ROUTES
        value = ROUTES["/api/" + a["route"]](a.get("query", {}))
        value.pop("computed_ms", None)
        return value
    if op in {"pipeline", "api_run", "agent_run", "tool_check"}:
        import test_pipeline as fixture
        from nav.ingest import run_ingest, pending_packets, write_outputs
        f = fixture.PipelineTest()
        f.setUp()
        try:
            if op == "tool_check":
                import threading
                from nav.agent import check_record
                from nav.ingest import Validator
                from nav.corpus import load_corpus
                from nav.config import load_schema
                return check_record(Validator(load_corpus(f.paths), f.index, load_schema(f.paths), "2026-10-01"), threading.Lock(), a["text"])
            for name, text in a.get("answers", {}).items():
                (f.paths.inbox_dir / name).write_text(text, encoding="utf-8")
            if "overrides" in a:
                (f.paths.work_dir / "overrides.json").write_text(json.dumps(a["overrides"]))
            run = {}
            if op in {"api_run", "agent_run"}:
                from nav.api import ApiConfig, ApiError, run_api
                from nav.agent import run_agent_api
                queue, calls, messages = list(a.get("replies", [])), [], []
                def post(msgs, specs=None):
                    calls.append({"messages": json.loads(json.dumps(msgs)), "tools": specs})
                    nxt = queue.pop(0)
                    if "error" in nxt:
                        raise ApiError(nxt["error"])
                    return nxt
                class Client:
                    def complete(self, prompt, packet):
                        return post([{"role": "system", "content": prompt}, {"role": "user", "content": packet}])
                try:
                    options = {"only": a.get("only", ["D100-01"]), "once": a.get("once", False), "dry_run": a.get("dry_run", False), "emit": messages.append}
                    config = ApiConfig("test-key")
                    code = run_api(f.paths, config, client=Client(), **options) if op == "api_run" else run_agent_api(f.paths, config, post=post, workers=a.get("workers", 1), **options)
                    run["code"] = code
                except ApiError as error:
                    import re
                    run["error"] = re.sub(r"(?:API|AGENT)_D\d+-\d+_[\w-]+\.json", "<ATTEMPT>.json",
                                          str(error).replace(str(f.tmp), "<TEMP>"))
                run["calls"] = calls
                # Attempt names and directory locations differ across runs. Check their
                # content and counts, never random IDs or wall-clock timestamps.
                run["answer_count"] = len(list(f.paths.inbox_dir.glob("*.jsonl")))
                run["archive_count"] = len(list((f.paths.work_dir / "api").glob("*.json")))
            res = run_ingest(f.paths, persist_ids=False)
            value = {"rules": res.rules, "counts": res.counts, "states": res.states, "pending": pending_packets(res),
                     "rejected": res.rejected, "problems": res.problems, "parse_problems": res.parse_problems}
            if run:
                run["state"] = {k: {kk: vv for kk, vv in v.items() if kk != "file"} for k, v in res.states.items()}
                run["rules"] = [{k: v for k, v in r.items() if not k.startswith("_")} for r in res.rules]
                return run
            return value
        finally:
            f.tearDown()
    raise ValueError("Unknown migration operation: " + op)

def invoke(case):
    try:
        return {"value": normalize(execute(case))}
    except (ValueError, KeyError, OSError, SystemExit) as error:
        return {"error": str(error)}
    except Exception as error:
        from web.server import NotFound
        from nav.api import ApiError
        if isinstance(error, (NotFound, ApiError)):
            return {"error": str(error)}
        raise

if __name__ == "__main__":
    for line in sys.stdin:
        print(json.dumps(invoke(json.loads(line)), ensure_ascii=False), flush=True)
