"""A table for a person: what each extracted rule's conditions did to the 500 addresses.

The conditions come from a model, so a person should look at them. The costliest mistake is a wrong exemption:
the rule then disappears for addresses where it applies, and nothing in the output says so. This table counts, for each
rule, the addresses it reaches and what happened to them, and quotes the text the conditions rest on.
"""
from __future__ import annotations

from collections import Counter

from .common import DEFAULT_DATE


def _conditions(rule):
    a = rule.get("applicability") or {}
    parts = []
    labels = [("built_on_or_before", "covered if built on or before %s"), ("built_before", "covered if built before %s"),
              ("built_after", "covered if built after %s"), ("built_on_or_after", "covered if built on or after %s"),
              ("min_units", "at least %s units"), ("max_units", "at most %s units"),
              ("exempt_if_newer_than_years", "exempt if newer than %s years"),
              ("owner_exempt_if_units_at_most", "owner exemption up to %s units")]
    for key, text in labels:
        if a.get(key) is not None:
            parts.append(text % a[key])
    if a.get("owner_dependent") and a.get("owner_exempt_if_units_at_most") is None:
        parts.append("owner-dependent, no size limit (unknown for every address)")
    if a.get("date_basis") and any(a.get(k) for k in ("built_on_or_before", "built_before", "built_after", "built_on_or_after", "exempt_if_newer_than_years")):
        parts.append("date basis: %s" % a["date_basis"])
    for item in a.get("deferred") or []:
        parts.append("exemption only if the owner filed (open question inside its reach): %s" % item["note"])
    if a.get("other"):
        parts.append("UNRESOLVED: %s" % a["other"])
    if a.get("per_tenancy"):
        parts.append("note: %s" % a["per_tenancy"])
    return parts


def collect(engine, as_of=DEFAULT_DATE):
    """Per rule: how many addresses it was tested on and how each ended."""
    stats = {r["team_rule_id"]: Counter() for r in engine.rules}
    for aid in sorted(engine.addresses):
        results, audit = engine.evaluate(aid, as_of)
        final = {row["team_rule_id"]: row["result"] for row in results}
        for trace in audit["rules"]:
            rid = trace["team_rule_id"]
            if trace.get("stopped_at_step") == 1 and not final.get(rid):
                continue                      # another state or city: not in scope for this address
            if rid in final:
                stats[rid][final[rid]] += 1
            else:
                stats[rid]["omitted: " + ("failed measure" if trace.get("stopped_at_step") == 2 else
                                           "a condition excludes it" if trace.get("stopped_at_step") == 6 else
                                           "outside its valid period" if trace.get("stopped_at_step") == 4 else "other")] += 1
    return stats


def render(engine, as_of=DEFAULT_DATE):
    stats = collect(engine, as_of)
    out = ["# 条件核对表（第一阶段提取的条件对 %s 个地址的影响）" % len(engine.addresses), "",
           "条件由模型从原文读出，请抽查。最贵的错误是**误判豁免**：规则会在本该适用的地址上悄悄消失。",
           "下面先列需要优先看的规则，再列全部规则。查询日期 %s。" % as_of, ""]
    flagged, rows = [], []
    for rule in sorted(engine.rules, key=lambda r: (r["jurisdiction"], r["category"], r["citation"])):
        rid = rule["team_rule_id"]
        c = stats[rid]
        scope = sum(c.values())
        omitted = sum(v for k, v in c.items() if k.startswith("omitted: a condition"))
        unknown = c.get("unknown", 0)
        why = []
        if omitted:
            why.append("条件使它在 %d 个地址上消失" % omitted)
        if scope and unknown == scope:
            why.append("所有 %d 个地址都是不确定" % scope)
        if (rule.get("applicability") or {}).get("built_on_or_before") is None and any(
                (rule.get("applicability") or {}).get(k) for k in ("built_before", "built_after", "built_on_or_after")):
            why.append("只有单侧日期条件，请核对方向")
        row = (rid, rule, c, scope, why)
        rows.append(row)
        if why:
            flagged.append(row)

    def block(row):
        rid, rule, c, scope, why = row
        lines = ["### %s — %s — %s — %s" % (rid, rule["jurisdiction"], rule["category"], rule["citation"]),
                 "- 状态：%s；生效日期：%s；有效期至：%s" % (rule.get("lifecycle"), rule.get("effective_date") or "原文未载明", rule.get("valid_through") or "—"),
                 "- 条件：%s" % ("；".join(_conditions(rule)) or "无"),
                 "- 地址结果（共 %d 个在范围内）：%s" % (scope, "，".join("%s %d" % (k, v) for k, v in sorted(c.items())) or "—")]
        if why:
            lines.append("- **注意：%s**" % "；".join(why))
        for q in (rule.get("applicability") or {}).get("coverage_quotes") or []:
            lines.append("- 原文：> %s" % " ".join(q.split())[:420])
        for r in rule.get("relations") or []:
            lines.append("- 关系 `%s`：> %s" % (r["type"], " ".join(r["quote"].split())[:300]))
        lines.append("")
        return lines

    out += ["## 优先核对（%d 条）" % len(flagged), ""]
    for row in flagged:
        out += block(row)
    out += ["## 全部规则（%d 条）" % len(rows), ""]
    for row in rows:
        out += block(row)
    return "\n".join(out) + "\n"
