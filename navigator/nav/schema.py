"""Tiny JSON-Schema checker for the subset the challenge schema uses (no third-party dependency)."""
from __future__ import annotations

import re
from typing import Any, Dict, List

_TYPES = {
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "null": lambda v: v is None,
}


def check(obj: Any, schema: Dict[str, Any], path: str = "$") -> List[str]:
    errs: List[str] = []
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_TYPES[x](obj) for x in types):
            return ["%s: expected %s, got %s" % (path, "/".join(types), type(obj).__name__)]
    if "enum" in schema and obj not in schema["enum"]:
        errs.append("%s: %r not in %s" % (path, obj, schema["enum"]))
    if isinstance(obj, str):
        if "minLength" in schema and len(obj) < schema["minLength"]:
            errs.append("%s: shorter than %d characters" % (path, schema["minLength"]))
        if "pattern" in schema and not re.search(schema["pattern"], obj):
            errs.append("%s: %r does not match %s" % (path, obj, schema["pattern"]))
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if "minimum" in schema and obj < schema["minimum"]:
            errs.append("%s: below minimum %s" % (path, schema["minimum"]))
        if "maximum" in schema and obj > schema["maximum"]:
            errs.append("%s: above maximum %s" % (path, schema["maximum"]))
    if isinstance(obj, list) and "items" in schema:
        for i, item in enumerate(obj):
            errs.extend(check(item, schema["items"], "%s[%d]" % (path, i)))
    if isinstance(obj, dict):
        for k in schema.get("required", []):
            if k not in obj:
                errs.append("%s: missing required field %r" % (path, k))
        for k, sub in schema.get("properties", {}).items():
            if k in obj:
                errs.extend(check(obj[k], sub, "%s.%s" % (path, k)))
    return errs
