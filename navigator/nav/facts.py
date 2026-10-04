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
RX_HYPHEN = re.compile(r"(?<![\d:.-])(\d{1,2})-(\d{1,2})-(\d{4})(?![\d-])")  # 3-28-2024, as ordinance history notes print it
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
    for m in RX_HYPHEN.finditer(text):
        add(_iso(int(m.group(3)), int(m.group(1)), int(m.group(2))))
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


def unspace_numbers(text: str) -> str:
    """Close gaps that scanned pages put inside numbers: '$ 1, 000' -> '$1,000', '( 30)' -> '(30)'."""
    text = re.sub(r"(?<=\d)\s*,\s*(?=\d{3}\b)", ",", text)
    text = re.sub(r"\$\s+(?=\d)", "$", text)
    return re.sub(r"\(\s+(?=\d)|(?<=\d)\s+\)", lambda m: "(" if m.group().startswith("(") else ")", text)


def numbers_in(text: str) -> Set[str]:
    """Numeric tokens in text, digits and spelled-out, canonicalised ('1,500' -> '1500', 'five' -> '5')."""
    out: Set[str] = set()
    text = unspace_numbers(text)
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
    """Whitespace, section sign and subdivision cleanup. Spelling follows the challenge brief: '§1947.12'."""
    s = re.sub(r"\s+", " ", c or "").strip()
    s = re.sub(r"\b(?:Section|Sec\.)\s+(?=\d)", "§", s, flags=re.I)
    s = re.sub(r"§\s+§", "§§", s)
    s = re.sub(r"§§?\s+", lambda m: m.group().rstrip(), s)
    s = _SUBD_WORDS.sub("", s)
    s = _SUBDIV.sub("", s)
    return s.strip(" ,;")


_ASPECT_COLON = re.compile(r":\s+(?=[A-Za-z])")
_CITE_CONTINUES = re.compile(r"^(?:§|ch\.|c\.|art\.|sec\.|section|subd\.|div\.|no\.|#|\d)", re.I)


def split_citation(c: str):
    """Split 'Cal. Civ. Code §1950.5: service member rules' into ('Cal. Civ. Code §1950.5', 'service member rules').

    A citation names a law; what one record says about it belongs in the title, not in the citation.
    The earliest delimiter wins: a colon followed by words, or a comma followed by words that are not
    part of the citation itself (another section, chapter or number).
    """
    s = re.sub(r"\s+", " ", c or "").strip()
    cut = None
    m = _ASPECT_COLON.search(s)
    if m and m.start() >= 4:
        cut = (m.start(), m.end())
    for mm in re.finditer(r",\s+", s):
        if cut is not None and mm.start() >= cut[0]:
            break
        before, after = s[:mm.start()], s[mm.end():]
        if not after or _CITE_CONTINUES.match(after):
            continue
        if re.search(r"\d", before) or after[0].islower():
            cut = (mm.start(), mm.end())
            break
    if cut is None:
        return s, None
    return s[:cut[0]].strip(" ,;"), s[cut[1]:].strip()


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


# ---------------------------------------------------------------- effective dates written as a rule

_ORDINALS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8,
    "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14,
    "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18, "nineteenth": 19,
    "twentieth": 20, "twenty-first": 21, "twenty-second": 22, "twenty-third": 23, "twenty-fourth": 24,
    "thirtieth": 30, "sixtieth": 60, "ninetieth": 90,
}
_COUNT = r"(?P<n>\d{1,3}(?:st|nd|rd|th)?|[a-z]+(?:[- ][a-z]+)?)"
_EVENT = r"(?:final\s+)?(?:passage|adoption|enactment|approval)"
RX_NTH_MONTH = re.compile(
    r"\btakes?\s+effect\s+on\s+the\s+first\s+day\s+of\s+the\s+(?P<n>\d{1,2}(?:st|nd|rd|th)|[a-z]+(?:-[a-z]+)?)"
    r"\s+month\s+next\s+following\s+(?:the\s+date\s+of\s+)?(?:its\s+)?" + _EVENT, re.I)
RX_IMMEDIATE = re.compile(r"\btakes?\s+effect\s+immediately\b", re.I)
# "on the thirtieth day after final passage", "90 days after enactment", "ninety (90) days after its final passage"
RX_DAYS_AFTER = re.compile(
    r"\b(?:takes?\s+effect|(?:shall\s+(?:be|become)\s+|is\s+|becomes?\s+)?effective)\s+(?:on\s+the\s+)?(?:" + _COUNT + r"\s*(?:\(\s*(?P<d>\d{1,3})\s*\)\s*)?)days?\s+(?:next\s+)?"
    r"(?:after|following)\s+(?:the\s+date\s+of\s+)?(?:its\s+)?" + _EVENT, re.I)
RX_APPROVED = re.compile(
    r"\b(?:approved|passed(?:\s+to\s+be\s+ordained)?|adopted|enacted|signed)(?:\s+by\s+(?:the\s+)?[a-z .]{3,40}?)?"
    r"\s+(?:on\s+)?%s\.?\s+(\d{1,2}),?\s+(\d{4})" % _MON, re.I)


def _count(word: str) -> Optional[int]:
    w = word.strip().lower()
    m = re.fullmatch(r"(\d{1,3})(?:st|nd|rd|th)?", w)
    if m:
        return int(m.group(1))
    if w in _ORDINALS:
        return _ORDINALS[w]
    w = w.replace(" ", "-")
    if w in _ORDINALS:
        return _ORDINALS[w]
    parts = w.split("-")
    if len(parts) == 1 and w in _WORDS:
        return _WORDS[w]
    if len(parts) == 2 and parts[0] in _WORDS and parts[1] in _WORDS and _WORDS[parts[0]] >= 20:
        return _WORDS[parts[0]] + _WORDS[parts[1]]
    return None


def add_months_first_day(iso: str, n: int) -> str:
    """First day of the n-th month after the month containing `iso` ('first day of the 4th month next following')."""
    y, m = int(iso[:4]), int(iso[5:7])
    idx = y * 12 + (m - 1) + n
    return "%04d-%02d-01" % (idx // 12, idx % 12 + 1)


class ActDates(object):
    def __init__(self, approved: str, effective: str, clause: str, method: str):
        self.approved, self.effective, self.clause, self.method = approved, effective, clause, method


RX_ADOPTED_DAY_OF = re.compile(
    r"\b(?:approved|passed|adopted|enacted|signed)\s+this\s+(\d{1,2})(?:st|nd|rd|th)?\s+day\s+of\s+%s,?\s+(\d{4})" % _MON, re.I)


def act_dates(text: str) -> Optional[ActDates]:
    """Effective date of a whole act when it is written as a rule ('first day of the twelfth month next following
    the date of enactment') together with the act's approval date. None unless the text has exactly one such
    clause and exactly one approval date, so a multi-act page is never guessed at."""
    clauses = []
    for kind, rx in (("nth_month", RX_NTH_MONTH), ("immediate", RX_IMMEDIATE), ("days_after", RX_DAYS_AFTER)):
        for m in rx.finditer(text):
            clauses.append((kind, m))
    if len(clauses) != 1:
        return None
    approved = sorted({_iso(int(m.group(3)), _mon(m.group(1)), int(m.group(2))) for m in RX_APPROVED.finditer(text)} - {None})
    approved = sorted(set(approved) | ({_iso(int(m.group(3)), _mon(m.group(2)), int(m.group(1))) for m in RX_ADOPTED_DAY_OF.finditer(text)} - {None}))
    if len(approved) != 1:
        return None
    kind, m = clauses[0]
    ap = approved[0]
    if kind == "nth_month":
        n = _count(m.group("n"))
        if n is None:
            return None
        eff = add_months_first_day(ap, n)
    elif kind == "immediate":
        eff = ap
    else:
        digits = m.groupdict().get("d")
        n = int(digits) if digits else _count(m.group("n") or "")
        if n is None:
            return None
        eff = (dt.date.fromisoformat(ap) + dt.timedelta(days=n)).isoformat()
    return ActDates(ap, eff, re.sub(r"\s+", " ", m.group(0)), kind)
