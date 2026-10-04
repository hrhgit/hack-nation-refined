# Candidate v8 (explore mode, written before the run)

Starting point: v7 (`prompts/v7_extract_prompt.md`), graded with the two-layer key after the decision that the key judges the whole
building: safe 144 of 146, exact 66 of 70, wrong exclusions 0. The live prompt (contract v2) scores safe 141, exact 60 of 70, 4 wrong exclusions.

The four exact answers v7 still misses, and the one change aimed at each:

| failure | what the model wrote | change |
|---|---|---|
| NJ 2A:18-61.1, a 5-unit building comes out "unknown" (both tries; also in the live prompt) | the trust and family-occupancy exceptions written as owner conditions with no size limit | an exception that reaches only particular units is a note in `per_tenancy`, never an `owner` or `other` condition |
| NJ 46:8-18.1, a 3-unit building comes out "unknown" (one try) | a licensee who is not the landlord written as an owner exemption | a licensee, broker or agent who is not the landlord is not an owner condition either; it is a note |

Keep rule, fixed now: keep v8 if (1) exact checks rise by at least 2 over v7's 66 of 70 and safe checks do not fall below v7's 144 of 146,
(2) wrong exclusions stay at 0, (3) none of the six answer-key-free parts drops below 0.97, and (4) its 69-page run (explore) shows no part
falling by more than its interval against round 4 and none worse than v7's own 69-page run by more than its interval.
Otherwise v7 (if it passed its own 69-page run) stays the candidate.

Not changed: everything else in v7. The key is small and the two failures come from two packets, so a gain here is weak evidence about other laws;
the review table after the real run (every rule's conditions with the quoted text) is the check that covers all of them.

## Result (written after the run)

v8 on the 17 laws, 2 tries each: safe 145 of 146, exact 69 of 70, wrong exclusions 0, all six key-free parts 1.000. v7 was 144, 66, 0. Keep rule
points (1) to (3) hold (exact +3 over v7). The one miss is a single try of the New Jersey FAIR law with no unit count answered "unknown"; v7 passed it,
so it reads as run-to-run variation. Point (4), the 69-page run, is still to do and will be done on the final text.

## v9 (planned, same rules)

v9 = v8 with the examples taken from particular laws replaced by fictional ones (`genericize.py`). Rule fixed now: keep v9 over v8 if safe and exact
are each no lower than v8's minus 2, wrong exclusions stay 0, and the key-free parts stay at or above 0.97. It is the same rules, so a drop would mean
the old examples were carrying the answer.
