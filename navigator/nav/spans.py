"""Locate a model's quoted span in the raw source and snap it to the exact source text.

Models paraphrase quotes, swap curly quotes, drop line breaks or add ellipses. The citation score needs
the span to exist verbatim in the corpus, so instead of trusting the model's copy we find where it came
from and replace it with the source's own characters.
"""
from __future__ import annotations

import difflib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

_TOK = re.compile(r"\w+", re.U)
_ELLIPSIS = re.compile(r"\[?\s*(?:\.\.\.|…)\s*\]?")
MIN_TOKENS = 3
FUZZY_MIN_RATIO = 0.85


def tokens(text: str) -> List[str]:
    return [m.group().lower() for m in _TOK.finditer(text)]


@dataclass
class Match:
    start: int
    end: int
    method: str   # exact | ellipsis | fuzzy
    score: float
    text: str


class DocIndex:
    def __init__(self, body: str):
        self.body = body
        self.toks: List[str] = []
        self.starts: List[int] = []
        self.ends: List[int] = []
        self.first: Dict[str, List[int]] = defaultdict(list)
        for m in _TOK.finditer(body):
            self.first[m.group().lower()].append(len(self.toks))
            self.toks.append(m.group().lower())
            self.starts.append(m.start())
            self.ends.append(m.end())
        self._tri: Optional[Dict[Tuple[str, str, str], List[int]]] = None

    # -- helpers
    def _find_exact(self, t: List[str], start_from: int = 0) -> Optional[Tuple[int, int]]:
        n = len(t)
        for p in self.first.get(t[0], ()):
            if p >= start_from and self.toks[p:p + n] == t:
                return p, p + n - 1
        return None

    def _trigrams(self):
        if self._tri is None:
            self._tri = defaultdict(list)
            for i in range(len(self.toks) - 2):
                self._tri[(self.toks[i], self.toks[i + 1], self.toks[i + 2])].append(i)
        return self._tri

    def _make(self, a: int, b: int, span: str, method: str, score: float) -> Match:
        s, e = self.starts[a], self.ends[b]
        sp = span.strip()
        # keep punctuation the model included at either end when the source has it too
        lead = {c for c in sp[: len(sp) - len(sp.lstrip("\"'“‘([§"))]} if sp else set()
        k = len(sp)
        while k > 0 and not sp[k - 1].isalnum():
            k -= 1
        trail = set(sp[k:])
        n = 0
        while e < len(self.body) and self.body[e] in trail and n < len(sp) - k:
            e += 1
            n += 1
        n = 0
        while s > 0 and self.body[s - 1] in lead and n < len(lead):
            s -= 1
            n += 1
        return Match(s, e, method, score, self.body[s:e].strip())

    # -- public
    def locate(self, span: str) -> Optional[Match]:
        t = tokens(span)
        if len(t) < MIN_TOKENS:
            return None
        hit = self._find_exact(t)
        if hit:
            return self._make(hit[0], hit[1], span, "exact", 1.0)

        parts = [p for p in _ELLIPSIS.split(span) if len(tokens(p)) >= MIN_TOKENS]
        if len(parts) >= 2:
            pos, first, last, ok = 0, None, None, True
            for part in parts:
                r = self._find_exact(tokens(part), pos)
                if r is None:
                    ok = False
                    break
                first = r[0] if first is None else first
                last = r[1]
                pos = r[1] + 1
            if ok and first is not None and last is not None:
                return self._make(first, last, span, "ellipsis", 1.0)

        return self._fuzzy(t, span)

    def _fuzzy(self, t: List[str], span: str) -> Optional[Match]:
        n = len(t)
        if n < 6:
            return None
        tri = self._trigrams()
        votes: Counter = Counter()
        for i in range(n - 2):
            for p in tri.get((t[i], t[i + 1], t[i + 2]), ()):
                votes[p - i] += 1
        if not votes:
            return None
        best = None
        for cand, _ in votes.most_common(5):
            lo, hi = max(0, cand - 3), min(len(self.toks), cand + n + 3)
            sm = difflib.SequenceMatcher(None, self.toks[lo:hi], t, autojunk=False)
            blocks = [b for b in sm.get_matching_blocks() if b.size]
            if not blocks:
                continue
            ratio = sum(b.size for b in blocks) / float(n)
            a, b = lo + blocks[0].a, lo + blocks[-1].a + blocks[-1].size - 1
            if b - a + 1 > 2 * n + 10:
                continue
            if best is None or ratio > best[0]:
                best = (ratio, a, b)
        if best and best[0] >= FUZZY_MIN_RATIO:
            return self._make(best[1], best[2], span, "fuzzy", round(best[0], 3))
        return None
