#!/usr/bin/env python3
"""Write eval/CONDITIONS_LABELS.md: the answer key of cond_labels.py as a table a person can read and mark up.

  python3 eval/cond_sheet.py

The file is generated; the answers live in cond_labels.py. To change one, edit cond_labels.py (or tell whoever maintains it).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cond_labels import COND_LABELS  # noqa: E402

RESULT = {"applies": "适用", "unknown": "不确定", "excluded": "规则被排除（结果里不出现）",
          "not_yet_effective": "尚未生效", "pending": "只是提案"}


def facts(p):
    f, parts = p["facts"], []
    if f.get("year_built") is not None:
        parts.append("%s 年建" % f["year_built"])
    else:
        parts.append("没有建成年份")
    if f.get("units") is not None:
        parts.append("%s 个单元" % f["units"])
    elif f.get("units_at_least") is not None:
        parts.append("用途代码显示至少 %s 个单元（没有准确数）" % f["units_at_least"])
    else:
        parts.append("没有单元数")
    if p["as_of"] != "2026-10-01":
        parts.append("查询日期 %s" % p["as_of"])
    return "，".join(parts)


ORDER = ["applies", "unknown", "excluded", "not_yet_effective", "pending"]


def acceptable(p):
    ok = sorted(p["ok"], key=ORDER.index)
    return "、".join(RESULT[r] for r in ok)


def exact(p):
    return RESULT[p["exact"]] if p["exact"] else "**待定**（key 没有定死）"


def main() -> int:
    out = ["# 条件答案清单（供核对）", "",
           "这份文件由 `eval/cond_sheet.py` 从 `eval/cond_labels.py` 生成，答案本身写在 `cond_labels.py` 里。",
           "每条法律下面是几个**虚构的地址**，和第二阶段应该给出的结果。结果的含义：", ""]
    out += ["- **适用**：规则在这个地址上适用。", "- **不确定**：缺少判断所需的事实（例如不知道房东是谁），结论是“不确定”。",
            "- **规则被排除**：规则对这个地址不适用，结果里不会出现这条规则。**最贵的错误是把本该适用的地址排除掉**，因为输出里看不出来。", "",
            "每个地址有两个答案，分两项检查：", "",
            "1. **不能出错的范围**：只要不把本该展示的规则藏起来就算对。这一项守住“别漏掉规则”。",
            "2. **最准确的答案**：必须选“适用”或“不确定”，并写明依据或缺失的事实。写“待定”的是 key 还没有定死（见下面的政策问题），不计这一项。", "",
            "判断“不确定”的原则（来自第二位审阅者，已采纳）：**只有缺失的事实可能改变结论才判不确定**，即房东身份、法律要求的备案或通知、"
            "横跨截止日期的年份、缺失的户数。不因为资料不全就一律不确定，也不因为没看到豁免就直接判适用。", "",
            "判断的对象是**整栋楼**：本清单判断楼宇层面的覆盖，特定单元仍可能存在例外（例如业主家属居住的某个单元），这类单元层面的例外另行判断，不会把整栋楼标成“不确定”。", "",
            "年份类测试的假设：测试给的是建成年份，而法条看的往往是入住证日期。按参与者指南 §4.1，只在截止年那一年判“不确定”，其他年份用建成年份代替。", "",
            "核对时请看两点：**法律的理解对不对**（“说明”一行），**每个地址该得的结果对不对**。有不同意见直接在这里标出来。", ""]
    for l in COND_LABELS:
        out += ["## %s — %s" % (l["id"], l["jurisdiction"]), "",
                "- 说明：%s" % l.get("zh", ""), "- 来源依据（英文）：%s" % l["source"],
                "- 页面：`%s`%s" % (l["packet"], "（**没参与调提示词的页面**，用作没见过的测试）" if l.get("held_out") else "")]
        extra = []
        for k, name in (("lifecycle", "状态"), ("effective_date", "生效日期"), ("valid_through", "有效期至")):
            if k in l:
                extra.append("%s = %s" % (name, l[k]))
        if "relations" in l:
            if l["relations"]["require"]:
                extra.append("必须有关系 " + "、".join("`%s`" % r for r in l["relations"]["require"]))
            if l["relations"]["forbid"]:
                extra.append("不能有关系 " + "、".join("`%s`" % r for r in l["relations"]["forbid"]))
        if extra:
            out.append("- 还要核对：" + "；".join(extra))
        out.append("")
        if l["probes"]:
            out += ["| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |", "|---|---|---|---|"]
            for p in l["probes"]:
                out.append("| %s | %s | %s | %s |" % (facts(p), acceptable(p), exact(p), p["basis"]))
            out.append("")
    (HERE / "CONDITIONS_LABELS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("wrote eval/CONDITIONS_LABELS.md (%d laws, %d tests)" % (len(COND_LABELS), sum(len(l["probes"]) for l in COND_LABELS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
