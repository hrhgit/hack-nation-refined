"""Paths, constants and schema-derived settings shared by the pipeline."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

PIPELINE_VERSION = "0.1.0"
DEFAULT_AS_OF = "2026-10-01"

ROOT = Path(__file__).resolve().parent.parent  # navigator/
PROJECT = ROOT.parent

# Jurisdictions named in the challenge brief: state code or "City, ST".
KNOWN_JURISDICTIONS = [
    "CA", "NJ", "MA",
    "Los Angeles, CA", "San Francisco, CA", "San Diego, CA", "Berkeley, CA", "Santa Ana, CA",
    "Jersey City, NJ", "Hoboken, NJ", "Newark, NJ",
    "Boston, MA", "Cambridge, MA",
]

STATE_NAMES = {"california": "CA", "new jersey": "NJ", "massachusetts": "MA"}

# Fallbacks; the real values are read from schema/rule_record.schema.json when present.
FALLBACK_CATEGORIES = [
    "rent_increase_limits", "just_cause_eviction", "security_deposits",
    "application_screening_fees", "screening_restrictions", "algorithmic_rent_setting",
]
LIFECYCLES = ["enacted", "pending_bill", "failed"]


@dataclass
class Paths:
    data_dir: Path
    work_dir: Path = ROOT / "work"
    out_dir: Path = ROOT / "outputs"
    extra_dir: Path = ROOT / "corpus_extra"

    @property
    def manifest(self) -> Path:
        return self.data_dir / "corpus" / "corpus_manifest.csv"

    @property
    def corpus_dir(self) -> Path:
        return self.data_dir / "corpus"

    @property
    def schema_file(self) -> Path:
        return self.data_dir / "schema" / "rule_record.schema.json"

    @property
    def extra_manifest(self) -> Path:
        return self.extra_dir / "extra_manifest.csv"

    @property
    def packets_dir(self) -> Path:
        return self.work_dir / "packets"

    @property
    def paste_dir(self) -> Path:
        return self.work_dir / "paste"

    @property
    def inbox_dir(self) -> Path:
        """Where the user saves raw model answers."""
        return self.work_dir / "out"

    @property
    def index_file(self) -> Path:
        return self.work_dir / "index.json"


def find_data_dir() -> Path:
    env = os.environ.get("NAV_DATA_DIR")
    if env:
        return Path(env).expanduser().resolve()
    for m in sorted(PROJECT.glob("starter-pack/**/corpus/corpus_manifest.csv")):
        return m.parent.parent
    raise FileNotFoundError(
        "Starter pack not found. Set NAV_DATA_DIR to the folder that contains corpus/corpus_manifest.csv"
    )


def default_paths() -> Paths:
    return Paths(data_dir=find_data_dir())


def load_schema(paths: Paths) -> Dict[str, Any]:
    if paths.schema_file.exists():
        return json.loads(paths.schema_file.read_text(encoding="utf-8"))
    return {
        "required": [], "properties": {"category": {"enum": FALLBACK_CATEGORIES}},
    }


def categories(schema: Dict[str, Any]) -> List[str]:
    return list(schema.get("properties", {}).get("category", {}).get("enum", FALLBACK_CATEGORIES))
