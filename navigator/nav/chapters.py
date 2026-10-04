"""Which chapter of a municipal code a citation belongs to.

Ordinances are often quoted section by section (Hoboken 155-4, 155-13, 155-14 ...), but the sections of one chapter are the parts of one
law: its cap, exemptions, registration and procedures. Consolidation merges them, so one rent-control chapter becomes one rule.
Only city-level citations in a code style are merged; ordinance numbers ("Ord. 2026-31"), council files, bills and public laws are not.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

NOT_A_CODE = re.compile(r"\bOrd(?:inance)?\b\.?\s*(?:No\.?)?\s*[\dA-Z]|C\.F\.|Council File|\bMotion\b|\bBill\b|\b[HS]\.\s?\d|\bP\.L\.|\bAB\s?\d|\bSB\s?\d", re.I)
SECTION = re.compile(r"(§§?\s*|\bch(?:apter)?\.?\s*|\barticle\s+|\bart\.\s*)?(\d+(?:[:.]\d+)*(?:-\d+[0-9A-Za-z.]*)?)", re.I)


def chapter_of(citation: str) -> Optional[str]:
    """The chapter token of a code citation, or None when it is not (or not clearly) a section of a chapter."""
    if not citation or NOT_A_CODE.search(citation):
        return None
    m = SECTION.search(re.sub(r"\([^)]*\)", " ", citation))
    if not m:
        return None
    marker, token = (m.group(1) or "").lower(), m.group(2)
    if marker.startswith(("ch", "art")):
        return token.split("-")[0]                       # "ch. 155", "ch. 13.76", "article 24"
    if ":" in token:
        return token.split("-")[0]                       # 19:2-18 -> 19:2
    if "-" in token:
        head = token.split("-")[0]
        return head if head.isdigit() else None          # 155-14 -> 155
    parts = token.split(".")
    if len(parts) >= 3:
        return ".".join(parts[:2])                       # 13.76.110 -> 13.76
    return None


def chapter_citation(citation: str, chapter: str) -> str:
    """The same citation with its section replaced by the chapter: 'Hoboken Mun. Code §155-14' -> 'Hoboken Mun. Code ch. 155'."""
    m = SECTION.search(citation)
    if not m:
        return citation
    return (citation[:m.start()] + "ch. " + chapter + citation[m.end():]).replace("  ", " ").strip()
