"""Rebuild per-packet answer text from the stored sub-agent answer files (free: no model call)."""
from __future__ import annotations

import json
from collections import defaultdict
from typing import Dict

from common import Ctx, classify, extract_json_objects


def stored_answers(ctx: Ctx) -> Dict[str, str]:
    lines: Dict[str, list] = defaultdict(list)
    for f in sorted(ctx.paths.inbox_dir.glob("BATCH-*.jsonl")):
        objs, _ = extract_json_objects(f.read_text(encoding="utf-8"))
        for o in objs:
            if classify(o) != "other" and o.get("packet_id") in ctx.index["packets"]:
                lines[o["packet_id"]].append(json.dumps(o, ensure_ascii=False))
    return {pid: "\n".join(v) for pid, v in lines.items()}
