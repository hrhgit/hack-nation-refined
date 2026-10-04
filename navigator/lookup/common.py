"""Small standard-library helpers shared by stages B and C."""
from __future__ import annotations

import calendar
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT.parent / "starter-pack" / "participant-final-no-hour16 3"
DEFAULT_DATE = "2026-10-01"
DISCLAIMER = "Not legal advice. Based only on the cited sources and the listed address facts."
CATEGORIES = {
    "rent_increase_limits", "just_cause_eviction", "security_deposits",
    "application_screening_fees", "screening_restrictions", "algorithmic_rent_setting",
}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def query_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("查询日期必须是 YYYY-MM-DD")
    return dt.date.fromisoformat(value)


def date_interval(value):
    """Preserve partial dates; never invent a day for a month/year-only source."""
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", value):
        raise ValueError("规则日期格式错误: %r" % value)
    parts = [int(x) for x in value.split("-")]
    if len(parts) == 3:
        day = dt.date(*parts)
        return day, day
    if len(parts) == 2:
        year, month = parts
        return dt.date(year, month, 1), dt.date(year, month, calendar.monthrange(year, month)[1])
    return dt.date(parts[0], 1, 1), dt.date(parts[0], 12, 31)


def matches(rule, selector):
    """Selectors describe laws by geography/category/citation, never by team IDs."""
    for key, expected in selector.items():
        if key.endswith("_contains"):
            actual = str(rule.get(key[:-9]) or "")
            if str(expected).casefold() not in actual.casefold():
                return False
        elif key == "citation_regex":
            if not re.search(expected, rule.get("citation", ""), re.I):
                return False
        elif rule.get(key) != expected:
            return False
    return True
