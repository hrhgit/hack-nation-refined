"""Write eval/INPUTS.md: every case and every expected law, for review."""
from __future__ import annotations

import json
import sys

from common import HERE, load_cases
from labels import LABELS


def main() -> int:
    cases = load_cases()
    silver = json.loads((HERE / "silver.json").read_text(encoding="utf-8"))["packets"]
    by_label = {}
    for l in LABELS:
        by_label.setdefault(l["packet"], []).append(l)
    L = ["# Extraction eval: the inputs", "",
         "One case = one packet (`work/packets/<id>.md`, or `eval/rehearsal/packets/` for the four invented documents), sent exactly as production sends it. %d cases: %d train, %d test; "
         "%d have hand-made expected laws. The split is random inside each (document kind, has-labels) group, seed 20261003, "
         "never chosen by score. The four invented rehearsal documents (R001 to R004) are all in the test split." % (len(cases), sum(c["split"] == "train" for c in cases), sum(c["split"] == "test" for c in cases),
                                      sum(c["labeled"] for c in cases)), "",
         "## Expected laws (written by hand from the challenge brief, not from any model)", "",
         "| id | packet | jurisdiction | category | checks | source |", "|---|---|---|---|---|---|"]
    for l in LABELS:
        checks = ", ".join(x for x in ("status=%s" % l["status"] if l.get("status") else "",
                                        "date=%s" % l["effective_date"] if l.get("effective_date") else "",
                                        "numbers=%s" % "/".join(l["key_numbers"]) if l.get("key_numbers") else "") if x) or "found only"
        L.append("| %s | [%s](%s/%s.md) | %s | %s | %s | %s |" % (
            l["id"], l["packet"], "rehearsal/packets" if l["packet"].startswith("R") else "../work/packets", l["packet"], l["jurisdiction"], l["category"], checks, l["source"].replace("|", ";")))
    L += ["", "Laws whose text is not in the corpus (Santa Ana, Jersey City, Hoboken, Newark ordinances) cannot appear in any packet and are not listed.", "",
          "## All cases", "", "| packet | split | kind | document jurisdiction | expected laws | chars | records in the earlier extraction |", "|---|---|---|---|---|---|---|"]
    for c in cases:
        L.append("| [%s](%s/%s.md) | %s | %s | %s | %s | %d | %d |" % (
            c["id"], "rehearsal/packets" if c["id"].startswith("R") else "../work/packets", c["id"], c["split"], c["kind"], c["jurisdiction"],
            ", ".join(l["id"] for l in by_label.get(c["id"], [])) or "-", c["chars"], silver[c["id"]]["n_records"]))
    L += ["", "## Things to know before trusting a number from this eval", "",
          "- It stands in for the organisers' scoring script, which is not in the data pack. The final answer must be checked on the real one.",
          "- Only %d laws have hand-made expectations. For every other packet the score rests on the code-checked parts (clean first pass, one record per law, clean and numbered citations, dates) and on agreement with the earlier extraction about whether a packet holds any rule." % len(LABELS),
          "- The earlier extraction (Claude sub-agents) is used for two coarse checks only: does the packet yield any record, and which (jurisdiction, category) cells. It is a frozen copy (`silver.json`), not an answer key.",
          "- A label may only expect a date the packet text supports (tests enforce it). Berkeley and AB 325 therefore carry no date check.",
          "- D046-01 and D047-01 hold the same bill text, so that bill counts twice.",
          "- Claude's earlier answers already find all expected laws, so `recall` cannot show gains for a model as strong; it matters for DeepSeek.",
          "- The primer planned as a later round names some laws that are also expected here. A gain on those laws then measures \"knows the citation\", not general skill; the unlabeled packets keep the general part honest."]
    (HERE / "INPUTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("INPUTS.md:", len(L), "lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
