"""Pull JSON objects out of a pasted chat answer (fences, prose, pretty-printing, truncation)."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

_TRAILING_COMMA = re.compile(r",\s*([}\]])")


def _match_brace(text: str, i: int) -> Optional[int]:
    depth, in_str, esc = 0, False, False
    for j in range(i, len(text)):
        ch = text[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return j
    return None


def _loads(chunk: str) -> Optional[Any]:
    try:
        return json.loads(chunk)
    except ValueError:
        pass
    try:
        return json.loads(_TRAILING_COMMA.sub(r"\1", chunk))
    except ValueError:
        return None


def classify(obj: Dict[str, Any]) -> str:
    if "category" in obj or "quoted_span" in obj:
        return "record"
    if "packet_id" in obj and "n_rules" in obj:
        return "receipt"
    return "other"


def extract_json_objects(text: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Return (objects, problems). Nested objects of a parsed record are not returned separately."""
    objs: List[Dict[str, Any]] = []
    problems: List[str] = []
    suspect: Optional[str] = None  # an unclosed '{' that looks like a record; cleared if later records parse
    i, n = 0, len(text)
    while i < n:
        if text[i] != "{":
            i += 1
            continue
        end = _match_brace(text, i)
        if end is None:
            tail = text[i:]
            if suspect is None and ('"category"' in tail[:3000] or '"packet_id"' in tail[:400]):
                suspect = tail[:120].replace("\n", " ")
            i += 1
            continue
        chunk = text[i:end + 1]
        obj = _loads(chunk)
        if isinstance(obj, dict):
            objs.append(obj)
            if classify(obj) != "other":
                suspect = None  # the unclosed brace was stray text, not a cut-off record
            i = end + 1
        else:
            if '"category"' in chunk or '"quoted_span"' in chunk:
                problems.append("unparseable JSON object near: %s" % chunk[:120].replace("\n", " "))
            i += 1
    if suspect is not None:
        problems.append("truncated JSON object (answer cut off?) near: %s" % suspect)
    return objs, problems
