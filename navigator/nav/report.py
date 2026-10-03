"""Human-readable report written next to every ingest run."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import List

from .config import KNOWN_JURISDICTIONS, Paths, categories, load_schema

SHORT = {
    "rent_increase_limits": "rent", "just_cause_eviction": "just cause", "security_deposits": "deposit",
    "application_screening_fees": "app fees", "screening_restrictions": "screening",
    "algorithmic_rent_setting": "algo",
}
STATUS_MARK = {"not_yet_effective": "N", "pending": "P", "failed": "F"}


def _matrix(paths: Paths, res) -> List[str]:
    cats = categories(load_schema(paths))
    cell = defaultdict(list)
    for r in res.rules:
        cell[(r["jurisdiction"], r["category"])].append(r["status"])
    rows = list(KNOWN_JURISDICTIONS) + sorted({r["jurisdiction"] for r in res.rules} - set(KNOWN_JURISDICTIONS))
    out = ["| jurisdiction | " + " | ".join(SHORT.get(c, c) for c in cats) + " |",
           "|---|" + "---|" * len(cats)]
    for j in rows:
        cols = []
        for c in cats:
            sts = cell.get((j, c), [])
            if not sts:
                cols.append("·")
            else:
                marks = Counter(STATUS_MARK[s] for s in sts if s in STATUS_MARK)
                extra = (" (" + ",".join("%d%s" % (v, k) for k, v in sorted(marks.items())) + ")") if marks else ""
                cols.append("%d%s" % (len(sts), extra))
        out.append("| %s | %s |" % (j, " | ".join(cols)))
    out += ["", "`·` = no rule extracted. N = not yet effective, P = pending bill, F = failed. "
                "An empty cell is correct for some cells (e.g. MA has no rent control): check, do not assume."]
    return out


def render_report(paths: Paths, res) -> str:
    idx = json.loads(paths.index_file.read_text(encoding="utf-8"))
    c = res.counts
    L = ["# Extraction report", "",
         "- as of **%s**" % res.as_of,
         "- answer files read: %d | records parsed: %d | accepted: %d | rejected and still open: %d "
         "(+%d rejected earlier and since fixed) | rules after merging: **%d**"
         % (c["files"], c["records_parsed"], c["accepted"], c["rejected"], c["rejected_fixed"], c["rules"]),
         "- packets done: **%d / %d**" % (c["packets_done"], c["packets_total"]), ""]

    notdone = [(p, s) for p, s in res.states.items() if s["state"] != "done"]
    L += ["## Packets still open (%d)" % len(notdone), ""]
    if notdone:
        by = Counter(s["state"] for _, s in notdone)
        L.append("States: " + ", ".join("%s %d" % (k, v) for k, v in sorted(by.items())) + "")
        L.append("")
        L += ["| packet | state | detail |", "|---|---|---|"]
        for p, s in notdone[:200]:
            L.append("| %s | %s | %s |" % (p, s["state"], s["detail"]))
        L += ["", "Run `python run.py bundle` to get paste files for exactly these packets."]
    else:
        L.append("None. Every packet has a complete, clean answer.")
    L.append("")

    if res.parse_problems:
        L += ["## Answer-file problems", ""]
        L += ["- `%s`: %s" % (f, p) for f, p in res.parse_problems]
        L.append("")

    open_rej = [rj for rj in res.rejected if rj["open"]]
    if open_rej:
        L += ["## Rejected records (%d)" % len(open_rej), "",
              "These did not enter rules.json. `bundle` asks the model to fix them.", ""]
        for rj in open_rej[:100]:
            rec = rj["record"]
            L.append("- **%s** `%s` %s: %s" % (rj["packet_id"], str(rec.get("citation"))[:50],
                                              str(rec.get("title"))[:50], "; ".join(rj["reasons"])))
        L.append("")

    flagged = [r for r in res.rules if r["warnings"] or r["conflict_flag"]]
    L += ["## Rules to check by hand (%d of %d)" % (len(flagged), len(res.rules)), ""]
    for r in flagged:
        L.append("- **%s** %s | %s | %s" % (r["team_rule_id"], r["jurisdiction"], r["category"], r["citation"]))
        for w in r["warnings"]:
            L.append("    - warning: %s" % w)
        if r["conflict_flag"]:
            L.append("    - conflict: %s" % r["conflict_note"])
    L.append("")

    if res.conflicts:
        L += ["## Sources that disagree", ""]
        for name, notes in res.conflicts:
            L.append("- %s" % name)
            L += ["    - %s" % n for n in notes]
        L.append("")
    if res.near_duplicates:
        L += ["## Possible duplicates (same jurisdiction and category, overlapping citations)", ""]
        L += ["- %s: `%s` vs `%s`" % t for t in res.near_duplicates]
        L.append("")

    L += ["## Coverage matrix", ""] + _matrix(paths, res) + [""]

    dropped = [(d, v) for d, v in idx["docs"].items() if v.get("dropped_blocks")]
    if dropped:
        L += ["## Blocks left out of very long documents (check nothing you need is here)", ""]
        for d, v in dropped:
            L.append("- %s: %d of %d blocks left out (%s chars)" % (d, len(v["dropped_blocks"]), v["blocks"],
                                                                  format(sum(b["chars"] for b in v["dropped_blocks"]), ",")))
            for b in v["dropped_blocks"][:40]:
                L.append("    - block %d (%d chars): %s" % (b["idx"], b["chars"], b["heading"]))
        L.append("")
    return "\n".join(L) + "\n"
