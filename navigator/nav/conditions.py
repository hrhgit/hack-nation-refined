"""Coverage conditions in the stage-1 to stage-2 contract (version 2).

The model copies every condition in the direction the source text states it ("covers only ...", "does not
apply to ...") and never does arithmetic. This module checks each number and date against the source document,
turns the list into the flat fields the address lookup tests, and does the small amount of arithmetic
("fewer than 5 units" is "at most 4"). A condition that cannot be matched to the source is not trusted: it becomes
an unresolved condition, so the lookup answers "unknown" instead of guessing.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Set

from . import facts

CONTRACT_VERSION = 2

APPL_KEYS = ["built_on_or_before", "built_before", "built_after", "built_on_or_after", "date_basis",
             "min_units", "max_units", "exempt_if_newer_than_years", "owner_dependent",
             "owner_exempt_if_units_at_most", "other", "program_notes", "per_tenancy", "coverage_quotes", "deferred", "contract"]
DATE_KEYS = ["built_on_or_before", "built_before", "built_after", "built_on_or_after"]
DATE_BASES = {"certificate_of_occupancy", "construction_date", "unspecified"}
RELATION_TYPES = {"preempts_local", "yields_to_local"}

ROLES = {"covered", "exempt"}
BUILT_OPS = {"on_or_before", "before", "after", "on_or_after"}
UNIT_OPS = {"at_least", "more_than", "at_most", "fewer_than"}
BASIS_NAMES = {"certificate_of_occupancy": "certificate_of_occupancy", "construction": "construction_date",
               "construction_date": "construction_date", "unspecified": "unspecified"}

# (role, op as the text states it) -> the flat key that says who is covered
_COVERED_DATE = {"on_or_before": "built_on_or_before", "before": "built_before",
                 "after": "built_after", "on_or_after": "built_on_or_after"}
_EXEMPT_DATE = {"after": "built_on_or_before", "on_or_after": "built_before",
                "before": "built_on_or_after", "on_or_before": "built_after"}

# An unresolved condition about a KIND of housing the assessor data does not show (affordable, subsidized, public or
# institutional housing, single units held separately, housing already under a local rent cap) is a note for the reader: it
# does not turn the whole building into "unknown". Owner status, filings and missing facts still do.
PROGRAM_NOTE = re.compile(
    r"affordab|subsid|deed|restrict|low.income|moderate.income|very low|public housing|housing authority|government|HUD\b|section ?8|"
    r"\b202\b|\b811\b|nonprofit|non-profit|transitional|institution|hospital|care facility|religious|dormitor|student|hotel|motel|"
    r"mobile ?home|condominium|single.family|alienable|rent control|rent stabilization|rent regulat|cooperative", re.I)

MIN_QUOTE = 15
MAX_QUOTE = 600
MAX_QUOTES = 4

Locate = Callable[[str], Optional[str]]


def empty() -> Dict[str, Any]:
    out: Dict[str, Any] = {k: None for k in APPL_KEYS}
    out["owner_dependent"] = False
    out["coverage_quotes"] = []
    out["deferred"] = []
    out["program_notes"] = []
    return out


def _text(v: Any) -> Optional[str]:
    if isinstance(v, str):
        v = v.strip()
        return None if v.lower() in {"", "null", "none", "n/a", "na", "unknown", "not stated", "not specified",
                                     "not applicable", "-"} else v
    return None


def _int(v: Any) -> Optional[int]:
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v if v >= 0 else None
    if isinstance(v, float) and v == int(v) and v >= 0:
        return int(v)
    if isinstance(v, str) and re.fullmatch(r"\s*\d+\s*", v):
        return int(v)
    return None


def _bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return isinstance(v, str) and v.strip().lower() == "true"


def _number_supported(n: int, nums: Optional[Set[str]]) -> bool:
    """A threshold may be stated as 'more than 4' and recorded as 5, so a neighbour of the value counts."""
    if nums is None:
        return True
    return any(facts._canon(float(x)) in nums for x in (n, n - 1, n + 1) if x >= 0)


def _date_supported(d: str, dates: Optional[Set[str]]) -> bool:
    return True if dates is None else d in dates


def _stricter(key: str, old: Optional[str], new: str) -> str:
    if old is None:
        return new
    a, b = facts.date_start(old), facts.date_start(new)
    keep_earlier = key in ("built_on_or_before", "built_before")
    return old if ((a <= b) == keep_earlier) else new


OWNER_KIND = re.compile(r"single.family|condominium|alienable|mobile ?home", re.I)


def _apply_flats(out: Dict[str, Any], flats: Dict[str, Any]) -> None:
    for k, v in flats.items():
        if k in DATE_KEYS:
            out[k] = _stricter(k, out[k], v)
        elif k == "min_units":
            out[k] = v if out[k] is None else max(out[k], v)
        elif k == "max_units":
            out[k] = v if out[k] is None else min(out[k], v)
        elif k == "exempt_if_newer_than_years":
            out[k] = v if out[k] is None else max(out[k], v)


def _finish_exempt(out: Dict[str, Any], members: List[Dict[str, Any]], conditional: bool, note: str,
                   basis_name: Optional[str], basis: List[str]) -> None:
    """Record an exemption that is made of one condition, or of several that must all hold ("a window").

    One unconditional condition becomes an ordinary exclusion. A conditional one (it holds only if the owner filed,
    registered or complied) or a window is kept apart in `deferred`: the lookup judges them as a whole, and a building
    inside a conditional exemption's reach is an open question, never an exclusion.
    """
    if len(members) == 1 and not conditional:
        _apply_flats(out, members[0])
        if basis_name:
            basis.append(basis_name)
        return
    if len(members) == 1:
        item: Dict[str, Any] = {"flats": dict(members[0]), "note": note, "conditional": True}
        if basis_name:
            item["flats"]["date_basis"] = basis_name
    else:
        item = {"flats_all": [dict(m, **({"date_basis": basis_name} if basis_name else {})) for m in members],
                "note": note, "conditional": conditional}
    if item not in out["deferred"]:
        out["deferred"].append(item)


def _exempt(c: Dict[str, Any], flats: Dict[str, Any], note: str, basis_name: Optional[str], out: Dict[str, Any],
            groups: Dict[str, Dict[str, Any]], basis: List[str]) -> None:
    gid = _text(c.get("group")) if isinstance(c.get("group"), str) else None
    conditional = c.get("conditional") is True
    if gid:
        g = groups.setdefault(gid, {"members": [], "conditional": False, "notes": [], "basis": []})
        g["members"].append(dict(flats))
        g["conditional"] = g["conditional"] or conditional
        g["notes"].append(note)
        if basis_name:
            g["basis"].append(basis_name)
        return
    _finish_exempt(out, [dict(flats)], conditional, note, basis_name, basis)


def _condition(c: Any, out: Dict[str, Any], unresolved: List[str], basis: List[str], warns: List[str],
               dates: Optional[Set[str]], nums: Optional[Set[str]], groups: Dict[str, Dict[str, Any]]) -> None:
    if not isinstance(c, dict):
        warns.append("applicability condition %r is not an object: ignored" % (c,))
        return
    kind = _text(c.get("type"))
    role = (_text(c.get("role")) or "").lower()
    label = "%s %s" % (kind, {k: v for k, v in c.items() if k not in ("type",)})

    def doubt(why: str) -> None:
        warns.append("applicability condition ignored (%s): %s" % (why, label[:160]))
        unresolved.append("a coverage condition the model reported could not be matched to the source (%s)" % label[:120])

    if kind == "built":
        op = (_text(c.get("op")) or "").lower()
        date = facts.normalize_date(c.get("date")) if isinstance(c.get("date"), str) else None
        if role not in ROLES or op not in BUILT_OPS or date is None:
            return doubt("needs role covered/exempt, an op and a date")
        if not _date_supported(date, dates):
            return doubt("date %s is not in the source" % date)
        key = (_COVERED_DATE if role == "covered" else _EXEMPT_DATE)[op]
        b = BASIS_NAMES.get((_text(c.get("basis")) or "").lower())
        if role == "exempt":
            return _exempt(c, {key: date}, "built %s %s" % (op.replace("_", " "), date), b, out, groups, basis)
        out[key] = _stricter(key, out[key], date)
        if b:
            basis.append(b)
    elif kind == "built_within_years":
        years = _int(c.get("years"))
        if role != "exempt" or years is None:
            return doubt("only an exemption for housing newer than N years can be tested")
        if not _number_supported(years, nums):
            return doubt("%s years is not in the source" % years)
        b = BASIS_NAMES.get((_text(c.get("basis")) or "").lower())
        _exempt(c, {"exempt_if_newer_than_years": years}, "built within the last %d years" % years, b, out, groups, basis)
    elif kind == "units":
        op = (_text(c.get("op")) or "").lower()
        n = _int(c.get("n"))
        if role not in ROLES or op not in UNIT_OPS or n is None:
            return doubt("needs role covered/exempt, an op and a whole number")
        if not _number_supported(n, nums):
            return doubt("%s units is not in the source" % n)
        # state who is covered, as a minimum or a maximum number of units
        if role == "covered":
            lo, hi = {"at_least": (n, None), "more_than": (n + 1, None), "at_most": (None, n), "fewer_than": (None, n - 1)}[op]
        else:
            lo, hi = {"at_most": (n + 1, None), "fewer_than": (n, None), "at_least": (None, n - 1), "more_than": (None, n)}[op]
        if role == "exempt":
            return _exempt(c, {"min_units": lo} if lo is not None else {"max_units": hi},
                           "%s %d units" % (op.replace("_", " "), n), None, out, groups, basis)
        _apply_flats(out, {"min_units": lo} if lo is not None else {"max_units": hi})
    elif kind == "owner":
        who = _text(c.get("who"))
        limit = _int(c.get("unit_limit")) if c.get("unit_limit") is not None else None
        if role not in ROLES or who is None:
            return doubt("needs role covered/exempt and who")
        if limit is not None and not _number_supported(limit, nums):
            return doubt("%s units is not in the source" % limit)
        if role == "exempt" and limit is None and OWNER_KIND.search(who):
            out["program_notes"].append(who)         # a kind of housing (single homes, condominiums), not the owner's status
            return
        out["owner_dependent"] = True
        if role == "exempt":
            if limit is None:
                out["_owner_unbounded"] = True
            elif out["owner_exempt_if_units_at_most"] is None or limit > out["owner_exempt_if_units_at_most"]:
                out["owner_exempt_if_units_at_most"] = limit
        elif limit is not None:
            _apply_flats(out, {"max_units": limit})  # the rule covers only owner-occupied buildings of up to this size
    elif kind == "other":
        text = _text(c.get("text"))
        if text:
            # a scope limit (role covered) always stays open; an exemption for a kind of housing is a note; with no role, the words decide
            note = role != "covered" and bool(PROGRAM_NOTE.search(text))
            (out["program_notes"] if note else unresolved).append(text)
    else:
        warns.append("applicability condition of unknown type ignored: %s" % label[:120])


def parse(a: Any, warns: List[str], dates: Optional[Set[str]] = None, nums: Optional[Set[str]] = None,
          locate: Optional[Locate] = None) -> Dict[str, Any]:
    """The applicability object the model wrote, as the flat fields the lookup tests. Never raises."""
    out = empty()
    if a is None:
        return out
    if not isinstance(a, dict):
        warns.append("applicability is not an object: ignored")
        return out
    unresolved: List[str] = []
    basis: List[str] = []
    conds = a.get("conditions")
    if "conditions" in a:
        out["contract"] = CONTRACT_VERSION
    if conds is not None and not isinstance(conds, list):
        warns.append("applicability.conditions is not a list: ignored")
        conds = None
    groups: Dict[str, Dict[str, Any]] = {}
    for c in conds or []:
        _condition(c, out, unresolved, basis, warns, dates, nums, groups)
    for g in groups.values():
        _finish_exempt(out, g["members"], g["conditional"], " and ".join(g["notes"]), (g["basis"] or [None])[0], basis)
    # An answer in the first format (flat keys) still reads; the list wins where both say something.
    for k in DATE_KEYS:
        v = _text(a.get(k))
        if v is not None and out[k] is None:
            nd = facts.normalize_date(v)
            if nd is None:
                warns.append("applicability.%s %r is not a date: ignored" % (k, v))
            else:
                out[k] = nd
    for k in ("min_units", "max_units", "exempt_if_newer_than_years", "owner_exempt_if_units_at_most"):
        v = _int(_text(a.get(k)) if isinstance(a.get(k), str) else a.get(k))
        if a.get(k) is not None and v is None:
            warns.append("applicability.%s %r is not an integer: ignored" % (k, a.get(k)))
        if v is not None and out[k] is None:
            out[k] = v
    if _bool(a.get("owner_dependent")):
        out["owner_dependent"] = True
    legacy_basis = _text(a.get("date_basis"))
    chosen = [b for b in basis if b != "unspecified"] or basis
    out["date_basis"] = chosen[0] if chosen else (legacy_basis if legacy_basis in DATE_BASES else None)
    legacy_other = _text(a.get("other"))
    if legacy_other:
        unresolved.append(legacy_other)
    out["other"] = "; ".join(dict.fromkeys(unresolved)) or None
    out["program_notes"] = list(dict.fromkeys(out["program_notes"]))
    out["per_tenancy"] = _text(a.get("per_tenancy"))
    quotes = a.get("coverage_quotes")
    if quotes is not None and not isinstance(quotes, list):
        warns.append("applicability.coverage_quotes is not a list: ignored")
        quotes = []
    kept: List[str] = []
    for q in (quotes or [])[:MAX_QUOTES]:
        q = _text(q)
        if q is None or "[[omitted" in q:
            continue
        if locate is not None:
            found = locate(q)
            if found is None:
                warns.append("applicability.coverage_quotes: a passage is not in the source and was dropped")
                continue
            q = found
        if MIN_QUOTE <= len(q) <= MAX_QUOTE and q not in kept:
            kept.append(q)
    out["coverage_quotes"] = kept
    if out.pop("_owner_unbounded", False):
        # an owner exemption without a size limit can reach a building of any size
        out["owner_exempt_if_units_at_most"] = None
    return out


def parse_relations(raw: Any, warns: List[str], locate: Optional[Locate] = None) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    if raw is None:
        return out
    if not isinstance(raw, list):
        warns.append("relations is not a list: ignored")
        return out
    for r in raw:
        kind = _text(r.get("type")) if isinstance(r, dict) else None
        quote = _text(r.get("quote")) if isinstance(r, dict) else None
        if kind not in RELATION_TYPES or quote is None:
            warns.append("a relation without a known type or quote was dropped")
            continue
        if locate is not None:
            quote = locate(quote)
            if quote is None:
                warns.append("a %s relation whose quote is not in the source was dropped" % kind)
                continue
        if len(quote) >= MIN_QUOTE and not any(x["type"] == kind and x["quote"] == quote for x in out):
            out.append({"type": kind, "quote": quote})
    return out


def merge(primary: Dict[str, Any], other: Dict[str, Any], doc_id: str, notes: List[str], warns: List[str]) -> None:
    """Fill the primary record's conditions from another document about the same law. Never overwrite."""
    a, b = primary["applicability"], other["applicability"]
    for k in DATE_KEYS + ["min_units", "max_units", "exempt_if_newer_than_years", "owner_exempt_if_units_at_most",
                          "date_basis"]:
        if a.get(k) is None and b.get(k) is not None:
            a[k] = b[k]
            notes.append("applicability.%s taken from %s" % (k, doc_id))
        elif b.get(k) is not None and a.get(k) != b[k]:
            warns.append("applicability.%s differs between sources: %s says %s, %s says %s"
                         % (k, primary["source_doc_id"], a.get(k), doc_id, b[k]))
    if b.get("owner_dependent") and not a.get("owner_dependent"):
        a["owner_dependent"] = True
        notes.append("owner_dependent taken from %s" % doc_id)
    for k in ("other", "per_tenancy"):
        if b.get(k) and b[k] not in (a.get(k) or ""):
            a[k] = "; ".join(x for x in (a.get(k), b[k]) if x)
    for q in b.get("coverage_quotes") or []:
        if q not in a["coverage_quotes"] and len(a["coverage_quotes"]) < MAX_QUOTES:
            a["coverage_quotes"].append(q)
    for item in b.get("deferred") or []:
        if item not in a["deferred"]:
            a["deferred"].append(item)
    for text in b.get("program_notes") or []:
        if text not in a["program_notes"]:
            a["program_notes"].append(text)
    if a.get("contract") is None:
        a["contract"] = b.get("contract")
    for k in ("valid_through",):
        if primary.get(k) is None and other.get(k) is not None:
            primary[k] = other[k]
            notes.append("%s filled in from %s" % (k, doc_id))
    for r in other.get("relations") or []:
        if r not in primary.setdefault("relations", []):
            primary["relations"].append(r)
