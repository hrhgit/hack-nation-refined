#!/usr/bin/env python3
"""Split an extraction prompt into a short core and reference cards, for the step-by-step ("agent") run.

  python3 eval/agent_build.py                                   # from the latest candidate prompt
  python3 eval/agent_build.py --base prompts/extract_prompt.md  # from the live prompt

Writes prompts/agent/core.md and prompts/agent/cards/*.md, the files `run.py api --agent` reads. They are the source of truth once they
exist, so this refuses to overwrite them unless you pass --force (edit a card by hand instead). The wording of every rule is taken from the base prompt, so the single-shot prompt
and the agent stay in step. What the model sees at once is only the core; a card is read when the packet raises the question it answers.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_BASE = HERE / "explore" / "conditions" / "prompts" / "v11_extract_prompt.md"
OUT = ROOT / "prompts" / "agent"


def bullet(lines, prefix):
    """The bullet that starts with `prefix` and its indented continuation lines."""
    for i, line in enumerate(lines):
        if line.startswith(prefix):
            j = i + 1
            while j < len(lines) and lines[j].startswith(" "):
                j += 1
            return i, j
    raise SystemExit("not found in the base prompt: %s" % prefix)


def pick(block, *markers):
    return [l for l in block if any(m in l for m in markers)]


CARD_INDEX = [
    ("building_age_and_size", "the packet limits which buildings are covered or exempt by when they were built, how old they are, or how many units they have"),
    ("owner_and_exceptions", "the packet makes coverage or an exemption depend on who owns or lives in the building, names a scope limit the data cannot show, or has exceptions for single units, tenancies or conduct"),
    ("dates", "the packet gives any date for the rule (adoption, approval, effective date) or publishes a value for a period"),
    ("relations", "the packet says how this law fits with other levels of law (bars local rules, or yields to local rules)"),
    ("citations", "you are about to write a `citation`, or the page does not print a code number"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default=str(DEFAULT_BASE))
    ap.add_argument("--primer", default=str(ROOT / "prompts" / "primer.md"))
    ap.add_argument("--force", action="store_true", help="overwrite prompts/agent/ (hand edits are lost)")
    args = ap.parse_args()
    text = Path(args.base).read_text(encoding="utf-8")
    lines = text.split("\n")

    a0, a1 = bullet(lines, "- `applicability`:")
    app = lines[a0:a1]
    e0, e1 = bullet(lines, "- `effective_date`:")
    v0, v1 = bullet(lines, "- `valid_through`:")
    c0, c1 = bullet(lines, "- `citation`:")
    i0, i1 = bullet(lines, "- `interaction`:")
    r0, r1 = bullet(lines, "- `relations`:")

    d_start = next(i for i, l in enumerate(lines) if l.startswith("# DATES AND CITATIONS"))
    n_start = next(i for i, l in enumerate(lines) if l.startswith("# NAMING A LAW"))
    h_start = next(i for i, l in enumerate(lines) if l.startswith("# HARD RULES"))
    date_rule = next(l for l in lines[d_start:n_start] if l.startswith("- Use only dates and numbers"))
    cite_style = next(l for l in lines[d_start:n_start] if l.startswith("- Citation style"))
    primer = Path(args.primer).read_text(encoding="utf-8").strip()

    cards = {
        "building_age_and_size": ["# Card: building age and size", "",
                                  app[0], *pick(app[1:], "Each condition is one of", '{"type":"built"', '{"type":"built_within_years"', '{"type":"units"', 'Add `"conditional":true`')],
        "owner_and_exceptions": ["# Card: owner conditions and other exceptions", "",
                                 *pick(app[1:], '{"type":"owner"', '{"type":"other"', "`per_tenancy`:", "`coverage_quotes`:")],
        "dates": ["# Card: dates", "", *lines[e0:e1], *lines[v0:v1], date_rule],
        "relations": ["# Card: relations to other levels of law", "", *lines[i0:i1], *lines[r0:r1]],
        "citations": ["# Card: citations", "", *lines[c0:c1], cite_style, "", "When the packet prints no code citation, name the law as follows.", "", primer],
    }

    # the core: the base prompt with those blocks replaced by pointers
    stubs = {
        a0: ['- `applicability`: the coverage conditions a program tests against a building (year built, certificate date, unit count, owner). Shape: `{"conditions":[...],"per_tenancy":"short text"|null,"coverage_quotes":[...]}`; all three keys are required and `conditions` is `[]` when the text sets none.',
             '  Copy each condition in the direction the text states it (`covered` only for wording that limits the rule to those buildings; `exempt` for exemptions and exclusions), copy numbers and dates as printed, never do arithmetic.',
             '  **If the packet limits or exempts buildings in any way, read the cards `building_age_and_size` and `owner_and_exceptions` before you write this field.**'],
        e0: ["- `effective_date`, `valid_through`: read the card `dates` whenever the packet gives a date for the rule or publishes a value for a period; `null` when the text gives none."],
        c0: ["- `citation`: the legal provision the rule comes from, at section level with no subdivision letters; read the card `citations` before you write it."],
        i0: ["- `interaction`, `relations`: how the law fits with other levels of law, only if the packet says so; read the card `relations` when it does (`[]` otherwise)."],
    }
    skip = set()
    for start, end in ((a0, a1), (e0, e1), (v0, v1), (c0, c1), (i0, i1), (r0, r1)):
        skip.update(range(start, end))
    skip.update(range(d_start, n_start + 3))      # DATES AND CITATIONS and NAMING A LAW sections
    core = []
    for i, line in enumerate(lines):
        if i in stubs:
            core += stubs[i]
        if i in skip:
            continue
        core.append(line)
    core_text = "\n".join(core)
    core_text = re.sub(r"\n{3,}", "\n\n", core_text)

    tools = ["", "# TOOLS AND CARDS", "",
             "You work in steps. You may call tools before you give the final answer.", "",
             "- `read_card(name)`: returns a short reference card. Read a card when the packet raises the question it answers; skip the cards that do not apply. Cards:"]
    tools += ["  - `%s`: read when %s." % (n, w) for n, w in CARD_INDEX]
    tools += ["- `check_record(record_json)`: runs the pipeline's own checks on one finished record (a JSON object as text) and shows how a program will read its conditions, including what they do to made-up buildings. "
              "Call it for each record before the final answer. If it reports an error, or the shown consequences are not what the packet says (for example a building the packet covers is left out), fix the record and check it again.", "",
              "The final answer is the JSON Lines described under OUTPUT FORMAT and nothing else. Do not call tools in the final message."]
    marker = "# HARD RULES"
    core_text = core_text.replace(marker, "\n".join(tools).strip("\n") + "\n\n" + marker, 1)

    if (OUT / "core.md").exists() and not args.force:
        raise SystemExit("prompts/agent/ already exists and is the source of truth; pass --force to rebuild it from the base prompt")
    OUT.mkdir(exist_ok=True)
    (OUT / "cards").mkdir(exist_ok=True)
    (OUT / "core.md").write_text(core_text.strip() + "\n", encoding="utf-8")
    for name, body in cards.items():
        (OUT / "cards" / (name + ".md")).write_text("\n".join(body).strip() + "\n", encoding="utf-8")
    print("core %d chars (the base prompt was %d); cards: %s" % (len(core_text), len(text), ", ".join("%s %d" % (n, len("\n".join(b))) for n, b in cards.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
