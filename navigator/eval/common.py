"""Shared pieces of the extraction eval: context, cases, split, frozen reference answers."""
from __future__ import annotations

import json
import random
import re
import sys
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from nav import facts  # noqa: E402
from nav.config import KNOWN_JURISDICTIONS, STATE_NAMES, Paths, default_paths, load_schema  # noqa: E402
from nav.corpus import _read_manifest, load_corpus  # noqa: E402
from nav.ingest import Validator, _Positions  # noqa: E402
from nav.packets import load_index  # noqa: E402
from nav.parse import classify, extract_json_objects  # noqa: E402

FLOW = HERE / "extraction"
CASES_FILE = HERE / "cases.json"
SILVER_FILE = HERE / "silver.json"
SPLIT_SEED = 20261003
REHEARSAL = HERE / "rehearsal"


@dataclass
class Ctx:
    paths: Paths
    index: Dict[str, Any]
    docs: Dict[str, Any]
    schema: Dict[str, Any]
    validator: Validator
    pos: _Positions
    as_of: str
    rehearsal: set = field(default_factory=set)

    def packet_file(self, pid: str) -> Path:
        """Packets of the invented rehearsal documents live in the eval folder, never in work/packets."""
        return (REHEARSAL / "packets" / (pid + ".md")) if pid in self.rehearsal else (self.paths.packets_dir / (pid + ".md"))


def load_ctx(as_of: Optional[str] = None) -> Ctx:
    paths = default_paths()
    index = load_index(paths)
    docs = load_corpus(paths)
    schema = load_schema(paths)
    as_of = as_of or index["as_of"]
    reh: set = set()
    if (REHEARSAL / "manifest.csv").exists():  # invented documents, held in memory beside the real ones
        _read_manifest(REHEARSAL / "manifest.csv", REHEARSAL, "rehearsal", docs)
        for f in sorted((REHEARSAL / "packets").glob("*.md")):
            index["packets"][f.stem] = {"doc_id": f.stem.split("-")[0], "part": 1, "parts": 1,
                                        "chars": len(f.read_text(encoding="utf-8"))}
            reh.add(f.stem)
    return Ctx(paths, index, docs, schema, Validator(docs, index, schema, as_of), _Positions(docs), as_of, reh)


def kind_of(url: str) -> str:
    u = (url or "").lower()
    if re.search(r"leginfo|malegislature|njleg|justia", u):
        return "statute"
    if re.search(r"nj\.gov|calcivilrights", u):
        return "guide"
    if re.search(r"\.pdf|municode|amlegal|ecode|gocodebook", u):
        return "ordinance"
    return "web_page"


def build_cases(ctx: Ctx) -> Dict[str, Any]:
    from labels import LABELS

    labeled = {l["packet"] for l in LABELS}
    missing = labeled - set(ctx.index["packets"])
    if missing:
        raise SystemExit("labels name packets that do not exist: %s" % sorted(missing))
    cases: List[Dict[str, Any]] = []
    for pid, meta in ctx.index["packets"].items():
        doc = ctx.docs[meta["doc_id"]]
        kind = "rehearsal" if doc.origin == "rehearsal" else kind_of(doc.url)
        cases.append({
            "id": pid, "doc_id": doc.doc_id, "kind": kind, "jurisdiction": doc.jurisdictions or "none",
            "labeled": pid in labeled, "chars": meta["chars"],
            "tags": [kind, doc.jurisdictions or "none", "labeled" if pid in labeled else "unlabeled"],
        })
    # Random split, stratified by document kind and whether the case has labels. Never by score.
    rng = random.Random(SPLIT_SEED)
    strata: "OrderedDict[tuple, List[Dict[str, Any]]]" = OrderedDict()
    for c in sorted(cases, key=lambda c: c["id"]):
        if c["kind"] == "rehearsal":
            c["split"] = "test"   # the analyzer never reads these: they stand in for the unseen document of hour 16
            continue
        strata.setdefault((c["kind"], c["labeled"]), []).append(c)
    flip = 0
    for key, group in strata.items():
        rng.shuffle(group)
        for i, c in enumerate(group):
            c["split"] = "train" if (i + flip) % 2 == 0 else "test"
        flip += len(group) % 2  # alternate who gets the odd one out
    return {"seed": SPLIT_SEED, "as_of": ctx.as_of, "cases": sorted(cases, key=lambda c: c["id"])}


def build_silver(ctx: Ctx) -> Dict[str, Any]:
    """Frozen copy of what an independent, earlier extraction (Claude sub-agents) produced per packet.

    Used only for two coarse checks, never as the answer key: does a packet yield any record at all, and which
    (jurisdiction, category) cells does it touch.
    """
    out: Dict[str, Any] = {}
    for f in sorted((ctx.paths.inbox_dir).glob("BATCH-*.jsonl")):
        objs, _ = extract_json_objects(f.read_text(encoding="utf-8"))
        for o in objs:
            kind = classify(o)
            pid = o.get("packet_id")
            if pid not in ctx.index["packets"]:
                continue
            slot = out.setdefault(pid, {"n_records": 0, "cells": []})
            if kind == "record":
                slot["n_records"] += 1
                jur = facts.normalize_jurisdiction(str(o.get("jurisdiction") or ""), KNOWN_JURISDICTIONS, STATE_NAMES)
                cell = [jur, str(o.get("category"))]
                if cell not in slot["cells"]:
                    slot["cells"].append(cell)
    reh = REHEARSAL / "oracle.jsonl"
    if reh.exists():  # the invented documents have hand-written gold answers instead of an earlier extraction
        for o in extract_json_objects(reh.read_text(encoding="utf-8"))[0]:
            pid = o.get("packet_id")
            slot = out.setdefault(pid, {"n_records": 0, "cells": []})
            if classify(o) == "record":
                slot["n_records"] += 1
                cell = [o["jurisdiction"], o["category"]]
                if cell not in slot["cells"]:
                    slot["cells"].append(cell)
    return {"source": "work/out/BATCH-*.jsonl at the time of freezing, plus the hand-written gold of eval/rehearsal", "packets": out}


def load_cases() -> List[Dict[str, Any]]:
    return json.loads(CASES_FILE.read_text(encoding="utf-8"))["cases"]


def load_silver() -> Dict[str, Any]:
    return json.loads(SILVER_FILE.read_text(encoding="utf-8"))["packets"]


def main() -> int:
    ctx = load_ctx()
    cases = build_cases(ctx)
    CASES_FILE.write_text(json.dumps(cases, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if "--rebuild-silver" in sys.argv or not SILVER_FILE.exists():
        SILVER_FILE.write_text(json.dumps(build_silver(ctx), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    c = cases["cases"]
    print("cases: %d | train %d | test %d | labeled %d" % (
        len(c), sum(x["split"] == "train" for x in c), sum(x["split"] == "test" for x in c), sum(x["labeled"] for x in c)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
