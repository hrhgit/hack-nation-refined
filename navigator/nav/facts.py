"""Deterministic fact handling: dates, numbers, citations and rule status.

The model reports facts (lifecycle, effective_date). Everything derived from them (status) is computed
here so that date arithmetic never depends on a model.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Dict, List, Optional, Set

MONTHS = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3, "april": 4, "apr": 4,
    "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7, "august": 8, "aug": 8,
    "september": 9, "sept": 9, "sep": 9, "october": 10, "oct": 10, "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}
_MON = r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
RX_MDY = re.compile(r"\b%s\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b" % _MON, re.I)
RX_DMY = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+%s\.?,?\s+(\d{4})\b" % _MON, re.I)
RX_SLASH = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})\b")
RX_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
RX_MY = re.compile(r"\b%s\.?,?\s+(\d{4})\b" % _MON, re.I)
RX_YEAR = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")

ISO_FULL = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_ANY = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def _iso(y: int, m: int, d: int) -> Optional[str]:
    try:
        return dt.date(y, m, d).isoformat()
    except ValueError:
        return None


def _mon(name: str) -> int:
    return MONTHS[name.lower().rstrip(".")]


def normalize_date(raw: Optional[str]) -> Optional[str]:
    """Return YYYY / YYYY-MM / YYYY-MM-DD, or None if it cannot be understood."""
    if raw is None:
        return None
    s = str(raw).strip()
    if ISO_ANY.match(s):
        if ISO_FULL.match(s) and not _iso(int(s[:4]), int(s[5:7]), int(s[8:10])):
            return None
        return s
    m = RX_MDY.search(s)
    if m:
        return _iso(int(m.group(3)), _mon(m.group(1)), int(m.group(2)))
    m = RX_DMY.search(s)
    if m:
        return _iso(int(m.group(3)), _mon(m.group(2)), int(m.group(1)))
    m = RX_SLASH.fullmatch(s)
    if m:
        y = int(m.group(3))
        y = y + 2000 if y < 100 else y
        return _iso(y, int(m.group(1)), int(m.group(2)))
    m = RX_MY.fullmatch(s)
    if m:
        return "%04d-%02d" % (int(m.group(2)), _mon(m.group(1)))
    return None


def date_start(s: str) -> dt.date:
    """Earliest day a possibly partial date can mean."""
    parts = [int(x) for x in s.split("-")]
    return dt.date(parts[0], parts[1] if len(parts) > 1 else 1, parts[2] if len(parts) > 2 else 1)


def doc_dates(text: str) -> Set[str]:
    """Every date the text mentions, as YYYY-MM-DD, YYYY-MM and YYYY strings."""
    out: Set[str] = set()

    def add(iso: Optional[str]):
        if iso:
            out.add(iso)
            out.add(iso[:7])
            out.add(iso[:4])

    for m in RX_MDY.finditer(text):
        add(_iso(int(m.group(3)), _mon(m.group(1)), int(m.group(2))))
    for m in RX_DMY.finditer(text):
        add(_iso(int(m.group(3)), _mon(m.group(2)), int(m.group(1))))
    for m in RX_SLASH.finditer(text):
        y = int(m.group(3))
        y = y + 2000 if y < 100 else y
        add(_iso(y, int(m.group(1)), int(m.group(2))))
    for m in RX_ISO.finditer(text):
        add(_iso(int(m.group(1)), int(m.group(2)), int(m.group(3))))
    for m in RX_MY.finditer(text):
        ym = "%04d-%02d" % (int(m.group(2)), _mon(m.group(1)))
        out.add(ym)
        out.add(ym[:4])
    for m in RX_YEAR.finditer(text):
        out.add(m.group(1))
    return out


def date_supported(eff: str, dates: Set[str]) -> bool:
    return eff in dates


def derive_status(lifecycle: str, effective_date: Optional[str], as_of: str) -> str:
    if lifecycle == "pending_bill":
        return "pending"
    if lifecycle == "failed":
        return "failed"
    if effective_date and date_start(effective_date) > date_start(as_of):
        return "not_yet_effective"
    return "in_force"


# ---------------------------------------------------------------- numbers

_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
    "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
}
_FRACTIONS = [
    (re.compile(r"\b(\w+) and (?:one[- ]half|a half)\b", re.I), 0.5),
    (re.compile(r"\bone[- ]half\b|\ba half\b", re.I), 0.5),
]
RX_NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")


def _canon(x: float) -> str:
    return ("%g" % x)


def numbers_in(text: str) -> Set[str]:
    """Numeric tokens in text, digits and spelled-out, canonicalised ('1,500' -> '1500', 'five' -> '5')."""
    out: Set[str] = set()
    for m in RX_NUM.finditer(text):
        tok = m.group().replace(",", "")
        try:
            out.add(_canon(float(tok)))
        except ValueError:
            pass
    low = text.lower()
    for rx, frac in _FRACTIONS:
        for m in rx.finditer(low):
            if m.lastindex:
                base = _WORDS.get(m.group(1))
                if base is not None:
                    out.add(_canon(base + frac))
            else:
                out.add(_canon(frac))
    for w in re.findall(r"[a-z]+", low):
        if w in _WORDS:
            out.add(_canon(_WORDS[w]))
    return out


def unsupported_numbers(value: str, doc_numbers: Set[str]) -> List[str]:
    """Numbers in a key_value that appear nowhere in the source document."""
    toks = []
    for m in RX_NUM.finditer(value.replace("%", " ")):
        try:
            toks.append(_canon(float(m.group().replace(",", ""))))
        except ValueError:
            pass
    return sorted({t for t in toks if t not in doc_numbers})


def numeric_signature(value: Optional[str]) -> frozenset:
    return frozenset(numbers_in(value or ""))


# ---------------------------------------------------------------- citations

_SUBDIV = re.compile(r"(?<=[0-9A-Za-z])(?:\s*\((?:[a-z]|[0-9]{1,2}|[ivx]{1,4}|[A-Z])\))+")
_SUBD_WORDS = re.compile(r",?\s*(?:subd\.|subdivision|subsection|subsec\.|para\.|paragraph)\s*\(?[\w.]+\)?", re.I)


def normalize_citation(c: str) -> str:
    s = re.sub(r"\s+", " ", c or "").strip()
    s = re.sub(r"\b(?:Section|Sec\.)\s+(?=\d)", "§ ", s, flags=re.I)
    s = re.sub(r"§\s*(?=\S)", "§ ", s)
    s = re.sub(r"§§\s*", "§§ ", s).replace("§ §", "§§")
    s = _SUBD_WORDS.sub("", s)
    s = _SUBDIV.sub("", s)
    return s.strip(" ,;")


def citation_key(c: str) -> str:
    """Identity of a legal provision: its digit-bearing tokens (section/chapter/bill numbers)."""
    base = re.sub(r"\([^)]*\)", " ", c or "")
    toks = re.findall(r"[0-9][0-9A-Za-z.:\-]*", base)
    toks = sorted({t.strip(".:-").lower() for t in toks if t.strip(".:-")})
    if toks:
        return "|".join(toks)
    return re.sub(r"[^a-z0-9]+", " ", (c or "").lower()).strip()


def key_tokens(key: str) -> Set[str]:
    return set(key.split("|")) if key else set()


# ---------------------------------------------------------------- jurisdictions

def normalize_jurisdiction(raw: str, known: List[str], state_names: Dict[str, str]) -> Optional[str]:
    s = re.sub(r"\s+", " ", (raw or "")).strip()
    if not s:
        return None
    low = s.lower()
    if low in state_names:
        return state_names[low]
    if re.fullmatch(r"[A-Za-z]{2}", s):
        return s.upper()
    s2 = re.sub(r"^(?:the )?city (?:and county )?of ", "", s, flags=re.I)
    s2 = re.sub(r"\s*,\s*", ", ", s2)
    m = re.fullmatch(r"(.+), ([A-Za-z]{2})", s2)
    if not m:
        m2 = re.fullmatch(r"(.+), (California|New Jersey|Massachusetts)", s2, flags=re.I)
        if not m2:
            return None
        s2 = "%s, %s" % (m2.group(1), state_names[m2.group(2).lower()])
        m = re.fullmatch(r"(.+), ([A-Za-z]{2})", s2)
    s2 = "%s, %s" % (m.group(1).strip(), m.group(2).upper())
    for k in known:
        if k.lower() == s2.lower():
            return k
    return s2


def level_of(jurisdiction: str) -> str:
    return "state" if re.fullmatch(r"[A-Z]{2}", jurisdiction) else "city"


def state_of(jurisdiction: str) -> str:
    return jurisdiction[-2:].upper() if jurisdiction else ""
