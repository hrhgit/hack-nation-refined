# Answer key for the coverage conditions

Why it exists. The extraction now writes conditions the address lookup tests against a building (see
`docs/STAGE1_CONTRACT.md`). The climb's grader scores citations, dates, one record per law and so on, but not these
conditions, so a wrong exemption would not show in its numbers. This key does, with made-up addresses.

| file | what it is |
|---|---|
| `cond_labels.py` | the key: 17 laws, 46 probes. Written by hand from the law texts, not from model answers. `held_out` marks laws from packets that no prompt edit looked at |
| `conditions_run.py` | runs the labeled packets through the real API path and keeps the raw answers under `eval/explore/conditions/<variant>/traces/` |
| `conditions_check.py` | reads stored answers, validates them with the current ingest code, runs each probe through the real lookup engine, counts passes and wrong exclusions |

```bash
python3 eval/conditions_run.py --variant now --reps 2 --dry-run     # size, spends nothing
python3 eval/conditions_run.py --variant now --reps 2               # live prompt files, about $0.25
python3 eval/conditions_check.py --variant now --verbose
python3 eval/conditions_run.py --variant cand --prompt-file eval/explore/conditions/prompts/v7_extract_prompt.md
```

A probe is an address (year built, unit count, query date) with two answers, scored as two checks:

* **safe**: the set of results that do not hide a law that covers the address. A **wrong exclusion** is a probe where the law was left
  out although the key says it covers the address: the costliest error, because nothing in the output shows it.
* **exact**: the single best result with its reason (the fact that settles it, or the missing fact that could change it). A probe whose
  exact answer the key does not settle is marked open and is not scored for exactness.

Rule for "unknown" (from a second reviewer, adopted): unknown only when a fact the data lacks could change the result: owner status, a
filing or notice the law requires, a year that straddles the cutoff, a missing unit count. Not because data is incomplete in general, and
not "applies" merely because no exemption was seen. Year-based probes assume year built stands in for the certificate date except in the
cutoff year (Participant Guide 4.1). The organizers' own template points the same way: a rule whose only open exemption is owner-occupancy
is "applies" once the unit count rules it out (r-0007), and a rule whose exemption needs a filing the data lacks is "unknown" (r-0031).

Changes to the key after the first results (each from reading the source, not from what a model wrote): NJ screening accepts the citation
"P.L. 2021, c.110" (the prompt itself lists that form); Hoboken's 2015 building is "unknown" only; the Los Angeles old-building answer is
open because the page lists a luxury exemption granted on application.

Decided: the key judges coverage of the building. A unit-level exception (NJ 2A:18-61.1: a unit held in trust for, or occupied by, a family
member with a developmental disability) can make a given unit an exception, but it does not make the whole building "unknown". The exact answer
for a 5-unit building under that law is "applies"; the answer says so in its note: this judges building-level coverage, and a particular unit may
still be an exception.

Open policy question, not scored for exactness until decided: whether exemptions for public housing, deed-restricted affordable housing or other
programs that the assessor data does not show should turn an old building's answer into "unknown" (the strict reading says yes; the organizers'
template ignores seasonal rentals, so the key may not). Those probes are marked open in the key.
