#!/usr/bin/env python3
"""Round 3's check: how many records of the cities on the citation list carry a code number, and do the controls hold?

  python3 eval/city_cites.py                       # every variant in eval/extraction, tries 0-1

Listed cities are the ones that have a row in prompts/primer.md. Controls: Santa Ana (not on the list, its pages print no code)
must stay unnumbered, and the invented rehearsal pages R001 (Cambridge) and R002 (Boston) must keep the citation their own
text prints instead of the list's Cambridge or Boston row. Reads stored rows only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import FLOW  # noqa: E402

LISTED = ["San Francisco, CA", "Los Angeles, CA", "Berkeley, CA", "San Diego, CA", "Jersey City, NJ", "Cambridge, MA", "Boston, MA"]


def numbered(c: str) -> bool:
    return bool(re.search(r"\d", c or ""))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tries", type=int, default=2)
    args = ap.parse_args()
    names = sorted((p.name for p in FLOW.iterdir() if (p / "results.jsonl").exists()), key=lambda n: (n != "baseline", int(n[1:]) if n[1:].isdigit() else 99))
    print("%-9s | %-26s | %-16s | %s" % ("variant", "listed cities: numbered", "Santa Ana (control)", "rehearsal controls keep their own citation (R001 / R002 tries)"))
    for v in names:
        rows = [json.loads(x) for x in (FLOW / v / "results.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        rows = [r for r in rows if r["rep"] < args.tries and r["status"] == "ok"]
        n = k = 0
        sa_n = sa_k = 0
        own = {"R001-01": [0, 0], "R002-01": [0, 0]}
        for r in rows:
            for a in r["meta"]["accepted"]:
                if a["jurisdiction"] in LISTED and not r["prompt_id"].startswith("R0"):
                    n += 1
                    k += numbered(a["citation"])
                if a["jurisdiction"] == "Santa Ana, CA":
                    sa_n += 1
                    sa_k += numbered(a["citation"])
            if r["prompt_id"] in own:
                own[r["prompt_id"]][1] += 1
                want = "2026-31|Ordinance No" if r["prompt_id"] == "R001-01" else "0842|Docket"
                if r["meta"]["accepted"] and all(re.search(want, a["citation"] or "") for a in r["meta"]["accepted"]):
                    own[r["prompt_id"]][0] += 1
        print("%-9s | %3d of %3d (%3.0f%%)           | %d of %d            | R001 %d/%d, R002 %d/%d" % (
            v, k, n, 100.0 * k / max(n, 1), sa_k, sa_n, own["R001-01"][0], own["R001-01"][1], own["R002-01"][0], own["R002-01"][1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
