# Candidate v7 (explore mode, written before the run)

Baseline: the live prompt (contract v2) on the 17 labeled packets, 2 tries: 137 of 146 checks, 4 wrong exclusions
(`eval/explore/conditions/now`). The 34 answers also score 1.000 on every part the climb's grader can compute without an answer key.

Failures seen in the baseline and the change aimed at each:

| failure | cause | change in `prompts/v7_extract_prompt.md` |
|---|---|---|
| Hoboken 155: a building from 2015 is left out (both tries) | the exemption for new construction holds only if the owner filed notices, but the exemption is stored as unconditional | `"conditional":true` on an exempt condition that depends on an owner's filing; ingest turns it into an open question (already in `nav/conditions.py`, tested) |
| Berkeley: a building from 1980 is left out (both tries) | a table row "most units built before 1980 are fully covered" was written as a condition that covers ONLY those | role `covered` means "only" and a row that just names one covered kind is not a condition |
| California 1947.12: the `yields_to_local` sentence missing in one try; in an earlier run a sentence that only says the law does not authorize local limits was written as `preempts_local`, which would flag every California address | loose definition | `preempts_local` needs an explicit bar ("shall not", "prohibited", "void") |

Keep rule, fixed now: keep v7 if (1) it passes at least 3 more of the 146 checks than the baseline, (2) wrong exclusions do not go up,
(3) none of the six answer-key-free parts drops below 0.97, and (4) the 69-page check (explore) shows no part falling by more than its own interval.
Otherwise the live prompt stays. The key is small, so a gain of a few checks is weak evidence; the keep rule is a floor, not a proof.

Not changed: the unlabeled behaviour the 17 laws cannot show. Packets of the key were used to write these edits (development set); only
NJ-2A:18-61.1 and CAM-14.04 were held out, and both already pass 8 of 8 under the baseline.
