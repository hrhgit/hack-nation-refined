"""Deterministic text cleaning and block splitting.

Cleaning only ever deletes whole lines of obvious navigation junk and normalises whitespace; it never
rewrites characters. Quotes taken from cleaned text therefore still match the raw document.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .keywords import is_relevant, score_text

NAV_RUN_MIN = 8  # consecutive nav-like lines needed before they are treated as junk
NAV_MARKER = "[[omitted: page navigation]]"

_ENUM_RE = re.compile(r"^\(?[A-Za-z]{1,3}[\).]\s")


def _is_navish(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if len(s) > 45 or len(s.split()) > 5:
        return False
    if re.search(r"[.;:!?]$", s):
        return False
    if re.search(r"\d", s):  # tables of rates, section numbers, dates are real content
        return False
    if _ENUM_RE.match(s):
        return False
    return True


LONG_LINE = 1200
WRAP_AT = 1000


def _soft_wrap(line: str) -> List[str]:
    """Break very long lines at spaces: some file readers truncate lines past ~2000 characters.

    Only whitespace changes, and span matching ignores whitespace, so quotes still align.
    """
    if len(line) <= LONG_LINE:
        return [line]
    parts: List[str] = []
    while len(line) > LONG_LINE:
        cut = line.rfind(" ", 0, WRAP_AT)
        if cut < WRAP_AT // 2:
            cut = line.find(" ", WRAP_AT)
            if cut < 0:
                break
        parts.append(line[:cut])
        line = line[cut + 1:]
    parts.append(line)
    return parts


def clean_text(body: str) -> Tuple[str, int, int]:
    """Return (clean_text, removed_lines, removed_chars)."""
    text = (body.replace(" ", " ").replace("​", "").replace("﻿", "")
            .replace("­", "").replace("\f", "\n"))
    lines = [ln.rstrip() for ln in text.split("\n")]
    keep = [True] * len(lines)
    marks: Dict[int, str] = {}  # first line of a removed run -> placeholder, so text never looks contiguous

    i = 0
    while i < len(lines):
        if _is_navish(lines[i]):
            j, count, last = i, 0, i
            while j < len(lines) and (not lines[j].strip() or _is_navish(lines[j])):
                if lines[j].strip():
                    count += 1
                    last = j
                j += 1
            if count >= NAV_RUN_MIN:
                for k in range(i, last + 1):
                    keep[k] = False
                marks[i] = NAV_MARKER
            i = max(j, i + 1)
        else:
            i += 1

    removed_lines = sum(1 for k, ln in zip(keep, lines) if not k and ln.strip())
    removed_chars = sum(len(ln) + 1 for k, ln in zip(keep, lines) if not k)
    out: List[str] = []
    blank = 0
    for pos, (k, ln) in enumerate(zip(keep, lines)):
        if not k:
            if pos in marks:
                out.append(marks[pos])
                blank = 0
            continue
        if not ln.strip():
            blank += 1
            if blank > 1:
                continue
            out.append("")
        else:
            blank = 0
            out.append(ln)
    wrapped: List[str] = []
    for ln in out:
        wrapped.extend(_soft_wrap(ln))
    return "\n".join(wrapped).strip("\n"), removed_lines, removed_chars


HEADING_RE = re.compile(
    r"""^\s*(?:
        §+\s*\d[\w.\-]*
      | Sec(?:tion|\.)\s+\d[\w.\-]*
      | \d{1,3}(?:\.\d{1,4}){1,3}\.?\s+\S
      | \d{4}(?:\.\d+)?\.\s*$
      | (?:CHAPTER|ARTICLE|DIVISION|TITLE|PART|SUBCHAPTER)\s+[\w.\-]+
      | SECTION\s+\d+\.
      | \d{1,3}\.\s+[A-Z][^\n]{3,80}$
      | [A-Z][A-Z0-9 ,&'\-]{8,80}$
    )""",
    re.X,
)

TARGET = 3500
HARD_MAX = 6000
MIN_BLOCK = 700


@dataclass
class Block:
    idx: int
    text: str
    scores: Dict[str, int] = field(default_factory=dict)

    @property
    def relevant(self) -> bool:
        return is_relevant(self.scores)

    @property
    def heading(self) -> str:
        for ln in self.text.split("\n"):
            if ln.strip():
                return ln.strip()[:100]
        return ""


def split_blocks(clean: str) -> List[Block]:
    blocks: List[Block] = []
    cur: List[str] = []
    cur_len = 0

    def flush():
        nonlocal cur, cur_len
        txt = "\n".join(cur).strip("\n")
        if txt.strip():
            blocks.append(Block(idx=len(blocks), text=txt, scores=score_text(txt)))
        cur, cur_len = [], 0

    for line in clean.split("\n"):
        blank = not line.strip()
        if cur and cur_len >= MIN_BLOCK and not blank and HEADING_RE.match(line):
            flush()
        elif cur and cur_len >= TARGET and blank:
            flush()
            continue
        elif cur and cur_len + len(line) + 1 > HARD_MAX:
            flush()
        cur.append(line)
        cur_len += len(line) + 1
    flush()
    return blocks


def select_blocks(blocks: List[Block], budget: int) -> List[bool]:
    """Budgeted selection for very large documents.

    Keywords are a poor hard filter (a key clause can score low), so nothing is dropped unless the
    document exceeds the budget; then the lowest-scoring blocks go first. Dropped blocks are reported.
    """
    total = sum(len(b.text) for b in blocks)
    if total <= budget:
        return [True] * len(blocks)
    keep = [False] * len(blocks)
    used = 0
    order = sorted(range(len(blocks)), key=lambda i: (-sum(blocks[i].scores.values()), i))
    for i in order:
        if sum(blocks[i].scores.values()) <= 0:
            break
        if used + len(blocks[i].text) > budget:
            continue
        keep[i] = True
        used += len(blocks[i].text)
    # spend leftover budget on neighbours of kept blocks (exemptions / dates often sit next door)
    for i in order:
        if keep[i]:
            for j in (i - 1, i + 1):
                if 0 <= j < len(blocks) and not keep[j] and used + len(blocks[j].text) <= budget \
                        and sum(blocks[j].scores.values()) > 0:
                    keep[j] = True
                    used += len(blocks[j].text)
    return keep
