"""Load the starter-pack corpus (and any extra documents the team adds by hand)."""
from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from .config import Paths

MANIFEST_COLUMNS = [
    "doc_id", "jurisdictions", "url", "source_type", "capture",
    "retrieved_at", "sha256", "text_file", "status",
]


@dataclass
class Doc:
    doc_id: str
    jurisdictions: str
    url: str
    source_type: str
    capture: str
    retrieved_at: str
    status: str
    text_path: Optional[Path]
    origin: str = "starter"  # "starter" or "extra"
    body: str = ""           # raw text without the SOURCE/RETRIEVED header
    header_url: str = ""
    header_retrieved: str = ""
    file_sha256: str = ""

    @property
    def has_text(self) -> bool:
        return bool(self.body.strip())

    @property
    def retrieved(self) -> str:
        return self.header_retrieved or self.retrieved_at


_HEADER_RE = re.compile(r"^(SOURCE|RETRIEVED):\s*(.*)$")


def split_header(raw: str):
    """Return ({'SOURCE':..., 'RETRIEVED':...}, body)."""
    lines = raw.split("\n")
    meta: Dict[str, str] = {}
    i = 0
    while i < len(lines):
        m = _HEADER_RE.match(lines[i])
        if not m:
            break
        meta[m.group(1)] = m.group(2).strip()
        i += 1
    return meta, "\n".join(lines[i:]).lstrip("\n")


def _read_manifest(path: Path, base: Path, origin: str, docs: Dict[str, Doc]) -> None:
    if not path.exists():
        return
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            doc_id = (row.get("doc_id") or "").strip()
            if not doc_id:
                continue
            tf = (row.get("text_file") or "").strip()
            tpath = (base / tf) if tf else None
            doc = Doc(
                doc_id=doc_id,
                jurisdictions=(row.get("jurisdictions") or "").strip(),
                url=(row.get("url") or "").strip(),
                source_type=(row.get("source_type") or "").strip(),
                capture=(row.get("capture") or "").strip(),
                retrieved_at=(row.get("retrieved_at") or "").strip(),
                status=(row.get("status") or "").strip(),
                text_path=tpath,
                origin=origin,
            )
            if tpath is not None and tpath.exists():
                data = tpath.read_bytes()
                doc.file_sha256 = hashlib.sha256(data).hexdigest()
                raw = data.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
                meta, doc.body = split_header(raw)
                doc.header_url = meta.get("SOURCE", "")
                doc.header_retrieved = meta.get("RETRIEVED", "")
            docs[doc_id] = doc


def load_corpus(paths: Paths) -> Dict[str, Doc]:
    docs: Dict[str, Doc] = {}
    _read_manifest(paths.manifest, paths.corpus_dir, "starter", docs)
    _read_manifest(paths.extra_manifest, paths.extra_dir, "extra", docs)
    return docs


def next_extra_id(paths: Paths) -> str:
    n = 0
    if paths.extra_manifest.exists():
        with paths.extra_manifest.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                m = re.match(r"X(\d+)$", row.get("doc_id", ""))
                if m:
                    n = max(n, int(m.group(1)))
    return "X%03d" % (n + 1)


def add_extra_doc(paths: Paths, text: str, jurisdiction: str, url: str,
                  doc_id: str = "", source_type: str = "official",
                  retrieved: str = "") -> str:
    """Register a document the team supplies (e.g. the hour-16 ordinance or a code-publisher page)."""
    import datetime

    doc_id = doc_id or next_extra_id(paths)
    retrieved = retrieved or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    (paths.extra_dir / "text").mkdir(parents=True, exist_ok=True)
    rel = "text/%s.txt" % doc_id
    body = text.replace("\r\n", "\n").replace("\r", "\n")
    (paths.extra_dir / rel).write_text(
        "SOURCE: %s\nRETRIEVED: %s\n\n%s\n" % (url, retrieved, body.strip("\n")), encoding="utf-8")
    new = not paths.extra_manifest.exists()
    with paths.extra_manifest.open("a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_COLUMNS)
        if new:
            w.writeheader()
        w.writerow({
            "doc_id": doc_id, "jurisdictions": jurisdiction, "url": url, "source_type": source_type,
            "capture": "yes", "retrieved_at": retrieved, "sha256": "", "text_file": rel, "status": "ok",
        })
    return doc_id
