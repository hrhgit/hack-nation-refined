#!/usr/bin/env python3
"""Make the examples in a candidate prompt fictional: python3 genericize.py base.md out.md
The rules stay; names, numbers and dates that came from a particular law are replaced. The citation-style list is left alone
(it shows the forms the hidden key uses, not a rule)."""
import sys
s = open(sys.argv[1], encoding="utf-8").read()
SWAPS = [
    ("`[Adopted 7-9-2025 by Ord. No. B-781]`", "`[Adopted 4-2-2024 by Ord. No. 123]`"),
    ('"exempt for 30 years after construction, or for the mortgage amortization period if shorter" is years 30',
     '"exempt for 20 years after construction, or until the construction loan is paid off if sooner" is years 20'),
    ("a carve-out inside the definition of a pricing-software provider or coordinator", "a carve-out inside the definition of a service provider or intermediary"),
    ('("most units built before 1980 are fully covered")', '("most units built before 1990 are covered")'),
    ('"May be preempted by NJ FAIR Act once effective"', '"May be preempted by the state act once it takes effect"'),
    ('(for example "the San Francisco Rent Ordinance")', '(for example "the Springfield Rent Ordinance")'),
]
for a, b in SWAPS:
    if a in s:
        s = s.replace(a, b)
    else:
        print("not found (already generic or text changed):", a[:60], file=sys.stderr)
open(sys.argv[2], "w", encoding="utf-8").write(s)
