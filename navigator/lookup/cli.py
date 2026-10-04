"""Independent stage B/C entry point; leaves stage A implementation untouched."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from .addresses import CensusResolver, load_addresses
from .common import DEFAULT_DATE, DISCLAIMER, PACK, ROOT, read_json, sha256, write_json
from .engine import LookupEngine, load_rules


def requests_report(engine, audit, changes_audit, supplements=None):
    grouped = defaultdict(set)
    explanations = {}
    for aid, address in audit["addresses"].items():
        for trace in address["rules"]:
            if trace.get("result") != "unknown":
                continue
            for missing in trace.get("missing_facts", []):
                key = (trace["team_rule_id"], missing["field"])
                grouped[key].add(aid)
                explanations[key] = missing["explanation"]
    lines = ["# 第二、三阶段对事实的需求", "", "本文件由查询结果生成，不修改第一阶段的程序。", "",
             "缺规则或缺适用条件时，请补原文和可判断的事实；缺房东、入住证、租约等地址事实时，应补公开地址数据，不能由第一阶段猜测。", "", "## 缺失的变更规则", ""]
    for test_id, case in changes_audit["tests"].items():
        if case["missing_rules"]:
            lines.append("- %s：%s。需补原文、引用、通过状态、生效日期、适用条件和州/市关系。" % (test_id, "、".join(case["missing_rules"])))
    if (ROOT / "corpus_extra" / "text" / "D034.txt").exists():
        lines.append("- Hoboken 的 D034 原文已经出现在 corpus_extra/text/D034.txt；若规则对照仍为空，需要第一阶段完成提取，而不是继续报原文不存在。第二、三阶段不会手工编造这条规则。")
    lines += ["", "## 每条规则缺少的判断事实", ""]
    for (rid, field), aids in sorted(grouped.items()):
        rule = engine.by_id[rid]
        lines += ["### %s — %s — %s" % (rid, rule["jurisdiction"], rule["citation"]),
                  "- 字段：`%s`；缺口：%s。" % (field, explanations[(rid, field)]),
                  "- 因此不确定的地址（%s个）：%s" % (len(aids), ", ".join(sorted(aids))), ""]
    # Under-specified input should request facts, rather than being silently treated as universal.
    lines += ["## 需要第一阶段核对的输入条件", ""]
    for rule in engine.rules:
        a = rule.get("applicability") or {}
        if rule.get("exemptions") and not any(a.get(k) for k in ("owner_dependent", "other", "built_on_or_before", "built_after", "exempt_if_newer_than_years", "covered_if_newer_than_years", "min_units", "max_units", "deferred", "alternatives")):
            matching = sorted(aid for aid, address in engine.addresses.items() if address["state"] == (rule["jurisdiction"] if rule["level"] == "state" else rule["jurisdiction"].rsplit(", ", 1)[-1]) and (rule["level"] == "state" or address.get("legal_city") == rule["jurisdiction"]))
            lines.append("- %s（%s）：有豁免文字，但没有对应结构条件。请确认是建筑覆盖条件还是行为/义务条件，不要把豁免条件反写成适用条件。可能相关地址：%s。原文摘录：%s" % (rule["team_rule_id"], rule["citation"], ", ".join(matching) or "样本暂无", rule["exemptions"]))
    if supplements is not None:
        lines += ["", "## 人工补充条目（lookup/coverage_facts.json）的核对", ""]
        unused = supplements.get("unused") or []
        lines.append("- 没有命中任何规则的条目（规则改名或合并后，这条补充已经不起作用，需要改匹配条件或删除）：%s" % (", ".join(unused) or "无"))
        for d in supplements.get("differs") or []:
            lines.append("- %s 覆盖了提取结果：%s（%s）的 `%s`，提取是 %r，补充是 %r" % (d["supplement"], d["rule"], d["citation"], d["field"], d["extracted"], d["supplement_value"]))
        if not supplements.get("differs"):
            lines.append("- 没有补充条目改写提取出的值。")
    lines += ["", "## 第一阶段重新生成的情况", ""]
    rejected = ROOT / "work" / "rejected.jsonl"
    if rejected.exists():
        records = [json.loads(line) for line in rejected.read_text(encoding="utf-8").splitlines() if line.strip()]
        current = [r for r in records if r.get("open")]
        lines.append("- 当前重新生成有%s条尚未通过第一阶段检查的记录。应在第一阶段核对原文，不由第二、三阶段绕过其检查。详见 work/rejected.jsonl 与 work/report.md。" % len(current))
    lines += ["", DISCLAIMER, ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="地址查询和变更追踪；" + DISCLAIMER)
    parser.add_argument("command", choices=["resolve", "build", "lookup", "changes", "review"])
    parser.add_argument("--as-of", default=DEFAULT_DATE)
    parser.add_argument("--address-id")
    parser.add_argument("--addresses", type=Path, default=PACK / "data" / "sample_addresses.csv")
    parser.add_argument("--resolved", type=Path, default=ROOT / "work" / "addresses_resolved.json")
    parser.add_argument("--rules", type=Path, default=ROOT / "work" / "rules_enriched.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    parser.add_argument("--work-dir", type=Path, default=ROOT / "work")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "work" / "geocode_cache")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--geocode-mode", choices=["single", "batch"], default="single")
    parser.add_argument("--date-overrides", type=Path, help="按题号配置查询日期的 JSON 文件")
    args = parser.parse_args(argv)
    try:
        if args.command == "resolve":
            previous = [-1]
            def progress(done, total):
                if done // 25 != previous[0] or done == total:
                    print("Census 地址和城市边界查询 %s/%s" % (done, total), flush=True)
                    previous[0] = done // 25
            resolved = CensusResolver(args.cache_dir, args.offline, args.refresh, mode=args.geocode_mode).resolve(load_addresses(args.addresses), progress=progress)
            write_json(args.resolved, resolved)
            print("已保存%s个地址；解析方式：%s。%s" % (len(resolved), dict(Counter(x["resolved_by"] for x in resolved.values())), DISCLAIMER))
            return 0
        addresses = read_json(args.resolved)
        raw_addresses = load_addresses(args.addresses)
        expected = set(raw_addresses)
        if set(addresses) != expected:
            raise ValueError("已解析地址与地址表编号不一致，请重新 resolve")
        for aid, raw in raw_addresses.items():
            if any(addresses[aid].get(field) != value for field, value in raw.items()):
                raise ValueError("%s的地址或建筑事实已改变，请重新 resolve，避免使用旧解析资料" % aid)
        supplement_report = {}
        engine = LookupEngine(load_rules(args.rules, report=supplement_report), addresses)
        if supplement_report.get("unused"):
            print("注意：补充条目没有命中任何规则：%s" % ", ".join(supplement_report["unused"]))
        if args.command == "review":
            from .review import render
            target = args.work_dir / "conditions_review.md"
            target.write_text(render(engine, args.as_of), encoding="utf-8")
            print("条件核对表：%s" % target)
            return 0
        if args.command == "lookup":
            if not args.address_id:
                raise ValueError("单地址查询需要 --address-id")
            print(json.dumps({"as_of": args.as_of, "address_id": args.address_id, "results": engine.lookup(args.address_id, args.as_of), "disclaimer": DISCLAIMER}, ensure_ascii=False, indent=2))
            return 0
        from changes import ChangeTracker
        overrides = read_json(args.date_overrides) if args.date_overrides else None
        changes, change_audit = ChangeTracker(engine).run(overrides)
        if args.command == "changes":
            write_json(args.output_dir / "changes.json", changes)
            write_json(args.work_dir / "changes_audit.json", change_audit)
        else:
            lookups, audit = engine.all(args.as_of)
            rules = engine.exported_rules(args.as_of, lookups)
            # All computation/validation completes before replacing submission files.
            write_json(args.output_dir / "rules.json", {"rules": rules})
            write_json(args.output_dir / "lookups.json", lookups)
            write_json(args.output_dir / "changes.json", changes)
            write_json(args.work_dir / "lookup_audit.json", audit)
            write_json(args.work_dir / "changes_audit.json", change_audit)
            args.work_dir.mkdir(parents=True, exist_ok=True)
            (args.work_dir / "stage1_requests.md").write_text(requests_report(engine, audit, change_audit, supplement_report), encoding="utf-8")
            inputs = [args.addresses, args.resolved, args.rules, Path(__file__).with_name("precedence.json"),
                      Path(__file__).with_name("coverage_facts.json"), Path(__file__).with_name("postal_cities.json"),
                      ROOT / "changes" / "test_rule_map.json", PACK / "dev" / "change_tests.json"]
            inputs += sorted((ROOT / "lookup").glob("*.py")) + sorted((ROOT / "changes").glob("*.py"))
            inputs += [p for p in [ROOT/"work"/"rejected.jsonl", ROOT/"corpus_extra"/"text"/"D034.txt"] if p.exists()]
            if args.date_overrides:
                inputs.append(args.date_overrides)
            manifest = {"as_of": args.as_of, "disclaimer": DISCLAIMER,
                        "inputs": {str(p.resolve().relative_to(ROOT.parent)) if p.resolve().is_relative_to(ROOT.parent) else str(p.resolve()): sha256(p) for p in inputs},
                        "outputs": {name: sha256(args.output_dir / name) for name in ("rules.json", "lookups.json", "changes.json")},
                        "audit_outputs": {name: sha256(args.work_dir / name) for name in ("lookup_audit.json", "changes_audit.json", "stage1_requests.md")},
                        "address_count": len(addresses), "rule_count": len(rules),
                        "geocode_methods": dict(sorted(Counter(x["resolved_by"] for x in addresses.values()).items())),
                        "results": dict(sorted(Counter(row["result"] for rows in lookups["lookups"].values() for row in rows).items()))}
            write_json(args.work_dir / "stage23_audit.json", manifest)
            print("已导出%s个地址、%s条规则及五道变更题；输入和输出指纹在 stage23_audit.json" % (len(addresses), len(rules)))
        for test_id, answer in changes.items():
            print("%s：受影响%s个，需复核%s个" % (test_id, len(answer["affected_address_ids"]), len(answer["conflict_flag_address_ids"])))
        print(DISCLAIMER)
        return 0
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, "第二、三阶段停止：%s\n" % error)


if __name__ == "__main__":
    raise SystemExit(main())
