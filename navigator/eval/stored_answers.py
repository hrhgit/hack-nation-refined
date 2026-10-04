"""Rebuild per-packet answer text from the stored sub-agent answer files (free: no model call)."""
from __future__ import annotations

import json
from collections import defaultdict
from typing import Dict

from common import Ctx, classify, extract_json_objects


def stored_answers(ctx: Ctx) -> Dict[str, str]:
    lines: Dict[str, list] = defaultdict(list)
    # the earlier sub-agent answers: in the inbox while they were live, in work/archive_claude_run/ since the real run replaced them
    folders = [ctx.paths.inbox_dir, ctx.paths.work_dir / "archive_claude_run"]
    for f in sorted(p for d in folders for p in d.glob("BATCH-*.jsonl")):
        objs, _ = extract_json_objects(f.read_text(encoding="utf-8"))
        for o in objs:
            if classify(o) != "other" and o.get("packet_id") in ctx.index["packets"]:
                lines[o["packet_id"]].append(json.dumps(o, ensure_ascii=False))
    return {pid: "\n".join(v) for pid, v in lines.items()}
