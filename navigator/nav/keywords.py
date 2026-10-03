"""Fixed keyword rules: used to hint categories and to drop irrelevant blocks of long documents.

These never decide what a rule says; they only decide what text is worth showing to the model
and give the validator a cheap sanity check ("does this document mention the category at all?").
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple


def _c(items: List[Tuple[str, int]]):
    return [(re.compile(p, re.I), w) for p, w in items]


CATEGORY_PATTERNS = {
    "rent_increase_limits": _c([
        (r"rent[- ]control|rent stabili[sz]ation|rent ordinance|rent board|rent adjustment", 2),
        (r"(?:annual|maximum|allowable|general)\s+(?:rent\s+)?(?:adjustment|increase)", 2),
        (r"(?:rent|rental rate)s?\s+increase|increase\s+(?:in\s+)?(?:the\s+)?(?:gross\s+)?(?:rent|rental)", 2),
        (r"consumer price index|\bCPI\b|cost of living", 1),
        (r"rent (?:cap|ceiling)|maximum (?:lawful |allowable )?rent|banking", 1),
        (r"preempt|local(?:ly)? (?:rent|regulat)", 1),
    ]),
    "just_cause_eviction": _c([
        (r"just cause|good cause|anti-eviction|cause for (?:eviction|termination)|grounds for (?:eviction|termination)", 2),
        (r"\bevict", 1),
        (r"relocation (?:assistance|payment|benefit|fee)", 2),
        (r"notice (?:of|to) (?:terminat|quit|vacate)|terminat\w+ (?:of )?(?:a )?tenanc", 1),
        (r"owner move-in|substantial rehabilitation|ellis act|withdraw\w* .{0,40}rental market", 1),
    ]),
    "security_deposits": _c([
        (r"security deposit", 2),
        (r"deposit.{0,60}month|month.{0,40}deposit", 1),
        (r"(?:first|last) month'?s rent", 1),
        (r"interest on (?:the |a )?(?:security )?deposit|deposit.{0,40}(?:escrow|interest)", 1),
        (r"return(?:ed)? (?:of )?(?:the |a )?(?:security )?deposit", 1),
    ]),
    "application_screening_fees": _c([
        (r"application fee|screening fee|screening charge|application charge|tenant screening", 2),
        (r"credit check.{0,30}fee|fee.{0,30}credit check", 2),
        (r"broker'?s? fee|finder'?s fee|\bbroker\b", 2),
        (r"holding deposit|lock fee|key fee|up-?front|advance payment|first and last month", 1),
    ]),
    "screening_restrictions": _c([
        (r"criminal (?:history|record|background|offender)|conviction|\barrest|\bCORI\b|fair chance|ban the box", 2),
        (r"source of income|lawful source|section 8|housing choice voucher|rental assistance|public assistance|voucher", 2),
        (r"credit (?:history|score|report)|background check|income requirement|eviction (?:history|record)", 1),
        (r"protected (?:class|characteristic)|discriminat", 1),
    ]),
    "algorithmic_rent_setting": _c([
        (r"algorithm", 3),
        (r"pricing (?:software|device)|revenue management|non-?public (?:competitor )?(?:rental )?data|coordinated pricing|price[- ]fixing", 2),
        (r"realpage|yieldstar|common pricing|occupancy levels", 2),
        (r"antitrust|cartwright|sherman act", 1),
    ]),
}


def score_text(text: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for cat, pats in CATEGORY_PATTERNS.items():
        s = 0
        for rx, w in pats:
            s += w * min(len(rx.findall(text)), 5)
        out[cat] = s
    return out


def is_relevant(scores: Dict[str, int]) -> bool:
    return max(scores.values() or [0]) >= 2 or sum(scores.values()) >= 3


def merge_scores(parts: List[Dict[str, int]]) -> Dict[str, int]:
    total: Dict[str, int] = {}
    for p in parts:
        for k, v in p.items():
            total[k] = total.get(k, 0) + v
    return total
