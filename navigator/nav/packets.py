"""Turn corpus documents into packets, and pending packets into paste-ready batch files."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .config import KNOWN_JURISDICTIONS, ROOT, PIPELINE_VERSION, Paths
from .corpus import Doc, load_corpus
from .keywords import merge_scores
from .textutil import Block, clean_text, select_blocks, split_blocks

DEFAULT_MAX_CHARS = 24000     # largest packet
DEFAULT_BUDGET = 80000        # documents above this lose their lowest-scoring blocks
DEFAULT_PASTE_CHARS = 50000   # target size of one paste-ready batch (packets only)


@dataclass
class Packet:
    packet_id: str
    doc_id: str
    part: int
    parts: int
    text: str
    hits: Dict[str, int]
    title_hint: str
    context: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def chars(self) -> int:
        return len(self.text)


def _omit(n: int) -> str:
    return "[[omitted: %s characters not relevant to the six categories]]" % format(n, ",")


def build_doc_packets(doc: Doc, max_chars: int = DEFAULT_MAX_CHARS, budget: int = DEFAULT_BUDGET):
    """Return (packets, stats). Stats feed the index and the human-readable report."""
    clean, rm_lines, rm_chars = clean_text(doc.body)
    blocks = split_blocks(clean)
    keep = select_blocks(blocks, budget)

    groups: List[List[Block]] = []
    cur: List[Block] = []
    cur_len = 0
    for b, k in zip(blocks, keep):
        if not k:
            continue
        if cur and cur_len + len(b.text) + 2 > max_chars:
            groups.append(cur)
            cur, cur_len = [], 0
        cur.append(b)
        cur_len += len(b.text) + 2
    if cur:
        groups.append(cur)

    dropped_before: Dict[int, int] = {}
    prev = -1
    for b, k in zip(blocks, keep):
        if k:
            dropped_before[b.idx] = sum(len(x.text) for x in blocks[prev + 1:b.idx])
            prev = b.idx
    tail_dropped = sum(len(x.text) for x in blocks[prev + 1:])

    title = ""
    for ln in clean.split("\n"):
        if ln.strip():
            title = ln.strip()[:120]
            break

    packets: List[Packet] = []
    for gi, group in enumerate(groups):
        parts: List[str] = []
        for b in group:
            if dropped_before.get(b.idx):
                parts.append(_omit(dropped_before[b.idx]))
            parts.append(b.text)
        if gi == len(groups) - 1 and tail_dropped:
            parts.append(_omit(tail_dropped))
        notes: List[str] = []
        if len(groups) > 1:
            notes.append("part %d of %d of a long document; the rest is in the other packets" % (gi + 1, len(groups)))
        if sum(1 for k in keep if not k):
            notes.append("%d of %d blocks of this document were left out as least relevant"
                         % (sum(1 for k in keep if not k), len(blocks)))
        ctx: List[str] = []
        if gi > 0 and group[0].idx > 0:
            ctx = [blocks[group[0].idx - 1].heading]
        packets.append(Packet(
            packet_id="%s-%02d" % (doc.doc_id, gi + 1), doc_id=doc.doc_id, part=gi + 1, parts=len(groups),
            text="\n\n".join(parts), hits=merge_scores([b.scores for b in group]),
            title_hint=title, context=ctx, notes=notes))

    stats = {
        "raw_chars": len(doc.body), "clean_chars": len(clean),
        "nav_lines_removed": rm_lines, "nav_chars_removed": rm_chars,
        "blocks": len(blocks), "blocks_kept": sum(keep),
        "dropped_blocks": [{"idx": b.idx, "chars": len(b.text), "heading": b.heading}
                           for b, k in zip(blocks, keep) if not k],
        "packets": [p.packet_id for p in packets],
    }
    return packets, stats


def render_packet(p: Packet, doc: Doc, as_of: str) -> str:
    hits = ", ".join("%s=%d" % (k, v) for k, v in sorted(p.hits.items(), key=lambda kv: -kv[1]) if v) or "none"
    lines = [
        "<<<PACKET %s>>>" % p.packet_id,
        "doc_id: %s" % doc.doc_id,
        "packet_id: %s" % p.packet_id,
        "part: %d of %d" % (p.part, p.parts),
        "source_url: %s" % doc.url,
        "retrieved: %s" % doc.retrieved,
        "manifest_jurisdiction: %s" % (doc.jurisdictions or "unknown"),
        "as_of_date: %s" % as_of,
        "document_title_hint: %s" % p.title_hint,
        "keyword_hints (rough, may be wrong): %s" % hits,
    ]
    for n in p.notes:
        lines.append("note: %s" % n)
    for c in p.context:
        lines.append("preceding_heading: %s" % c)
    lines.append("<<<TEXT>>>")
    lines.append(p.text)
    lines.append("<<<END PACKET %s>>>" % p.packet_id)
    return "\n".join(lines) + "\n"


def render_prompt(as_of: str) -> str:
    raw = (ROOT / "prompts" / "extract_prompt.md").read_text(encoding="utf-8")
    if "{{PRIMER}}" in raw:   # the background file is read only by a prompt that asks for it
        raw = raw.replace("{{PRIMER}}", (ROOT / "prompts" / "primer.md").read_text(encoding="utf-8").strip())
    return (raw.replace("{{AS_OF}}", as_of)
               .replace("{{JURISDICTIONS}}", ", ".join('"%s"' % j for j in KNOWN_JURISDICTIONS)))


def render_delivery(out_file: Path) -> str:
    raw = (ROOT / "prompts" / "delivery.md").read_text(encoding="utf-8")
    return raw.replace("{{OUT_FILE}}", str(out_file)).replace("{{WORKDIR}}", str(ROOT))


def answer_path(paths: Paths, base: str) -> Path:
    """Where the model should save its answer; never an existing file, so earlier answers survive."""
    cand = paths.inbox_dir / (base + ".jsonl")
    n = 2
    while cand.exists():
        cand = paths.inbox_dir / ("%s_r%d.jsonl" % (base, n))
        n += 1
    return cand


def load_index(paths: Paths) -> Dict:
    if not paths.index_file.exists():
        raise SystemExit("No packet index yet. Run: python run.py prepare")
    return json.loads(paths.index_file.read_text(encoding="utf-8"))


def prepare(paths: Paths, as_of: str, max_chars: int = DEFAULT_MAX_CHARS, budget: int = DEFAULT_BUDGET,
            only: Optional[List[str]] = None) -> Dict:
    docs = load_corpus(paths)
    paths.packets_dir.mkdir(parents=True, exist_ok=True)
    paths.inbox_dir.mkdir(parents=True, exist_ok=True)

    if only:
        index = json.loads(paths.index_file.read_text(encoding="utf-8")) if paths.index_file.exists() else \
            {"packets": {}, "docs": {}}
        for did in only:
            for pid in [k for k, v in index["packets"].items() if v["doc_id"] == did]:
                (paths.packets_dir / (pid + ".md")).unlink(missing_ok=True)
                index["packets"].pop(pid, None)
            index["docs"].pop(did, None)
        todo = [docs[d] for d in only if d in docs]
        missing = [d for d in only if d not in docs]
        if missing:
            raise SystemExit("Unknown doc_id(s): %s" % ", ".join(missing))
    else:
        if paths.packets_dir.exists():
            shutil.rmtree(paths.packets_dir)
        paths.packets_dir.mkdir(parents=True)
        index = {"packets": {}, "docs": {}}
        todo = [docs[k] for k in sorted(docs)]

    for doc in todo:
        if not doc.has_text:
            index["docs"][doc.doc_id] = {"no_text": True, "jurisdictions": doc.jurisdictions, "url": doc.url,
                                         "source_type": doc.source_type, "capture": doc.capture,
                                         "status": doc.status, "origin": doc.origin}
            continue
        packets, stats = build_doc_packets(doc, max_chars, budget)
        stats.update({"no_text": False, "jurisdictions": doc.jurisdictions, "url": doc.url,
                      "source_type": doc.source_type, "origin": doc.origin, "file_sha256": doc.file_sha256})
        index["docs"][doc.doc_id] = stats
        for p in packets:
            body = render_packet(p, doc, as_of)
            (paths.packets_dir / (p.packet_id + ".md")).write_text(body, encoding="utf-8")
            index["packets"][p.packet_id] = {
                "doc_id": doc.doc_id, "part": p.part, "parts": p.parts, "chars": len(body),
                "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(), "hits": p.hits,
            }

    index.update({"as_of": as_of, "pipeline_version": PIPELINE_VERSION,
                  "max_chars": max_chars, "budget": budget})
    index["packets"] = dict(sorted(index["packets"].items()))
    index["docs"] = dict(sorted(index["docs"].items()))
    paths.index_file.write_text(json.dumps(index, indent=1, ensure_ascii=False), encoding="utf-8")
    (paths.work_dir / "PROMPT.md").write_text(render_prompt(as_of), encoding="utf-8")
    write_gaps(paths, index)
    return index


def write_gaps(paths: Paths, index: Dict) -> None:
    rows = [(d, v) for d, v in index["docs"].items() if v.get("no_text")]
    out = ["# Documents without text (not extractable until someone supplies the text)", "",
           "The corpus lists %d documents but only %d have text. The rest cannot produce rules or quoted spans."
           % (len(index["docs"]), len(index["docs"]) - len(rows)), "",
           "To add one by hand (reading a page is allowed; do not bulk-scrape sites whose terms forbid it):", "",
           "    python run.py add-doc --file page.txt --jurisdiction \"Hoboken, NJ\" --url <page url>", "",
           "| doc_id | jurisdiction | source type | capture | url |", "|---|---|---|---|---|"]
    for d, v in rows:
        out.append("| %s | %s | %s | %s | %s |" % (d, v["jurisdictions"], v["source_type"][:24], v["capture"], v["url"]))
    (paths.work_dir / "COVERAGE_GAPS.md").write_text("\n".join(out) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- batches

def render_packet_input(pid: str, text: str, problems: List[str]) -> str:
    """Identical packet/correction instructions for manual and API extraction."""
    if not problems:
        return text
    head = ["!!! CORRECTIONS NEEDED for packet %s. An earlier answer for it had these problems:" % pid]
    head += ["    - %s" % m for m in problems]
    head.append("    Re-emit the corrected records for this packet (you may re-emit all of them), then its receipt.")
    head.append("    `n_rules` in the receipt counts the records in THIS answer.\n")
    return "\n".join(head) + "\n" + text


def make_batches(paths: Paths, pending: Dict[str, List[str]], paste_chars: int = DEFAULT_PASTE_CHARS) -> List[str]:
    """Write paste-ready files for the pending packets. `pending` maps packet_id -> problem messages."""
    index = load_index(paths)
    as_of = index["as_of"]
    prompt = render_prompt(as_of)
    if paths.paste_dir.exists():
        shutil.rmtree(paths.paste_dir)
    paths.paste_dir.mkdir(parents=True)

    items: List[tuple] = []
    for pid in sorted(pending):
        f = paths.packets_dir / (pid + ".md")
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        items.append((pid, render_packet_input(pid, text, pending[pid])))

    batches: List[List[tuple]] = []
    cur: List[tuple] = []
    cur_len = 0
    for it in items:
        if cur and cur_len + len(it[1]) > paste_chars:
            batches.append(cur)
            cur, cur_len = [], 0
        cur.append(it)
        cur_len += len(it[1])
    if cur:
        batches.append(cur)

    written: List[str] = []
    for n, batch in enumerate(batches, 1):
        ids = [i for i, _ in batch]
        name = "BATCH-%02d_%s_to_%s.md" % (n, ids[0], ids[-1])
        out_file = answer_path(paths, name[:-3])
        body = [prompt, "\n---\n", render_delivery(out_file), "\n---\n", "# SOURCE PACKETS",
                "", "This batch contains %d packet(s): %s." % (len(ids), ", ".join(ids)),
                "Now write your answer as described under DELIVERY: for each packet, in order, its JSON records "
                "and then its receipt line. JSON Lines only.", ""]
        body += [t for _, t in batch]
        (paths.paste_dir / name).write_text("\n".join(body), encoding="utf-8")
        written.append(name)
    return written
