# Round 1: one record per law and category

Define "law" and require exactly one record per law and category; delete the "typical document yields 0 to 6 records" line that invites splitting.

**Why (hypothesis).** The model reads the rule and then argues itself out of it. Baseline reasoning on D025-01 (train): "I think cap and return deadline are two distinct rules within the same category — a typical document yields 0-6 records. Let me write: (1) deposit cap, (2) 21-day return deadline + itemized statement + penalty" (`eval/extraction/baseline/traces/D025-01_rep0.json`). The v1 wording ("one record per legal provision") leaves "provision" open and "0 to 6" makes five or six records look normal.

**Evidence in numbers (baseline).** clean 0.66, one_per_law 0.79 over all cases; in the exploration run 27 of 97 records were sent back for repeating a law, and 11 of 33 training packets would have needed a correction round.

**Change** (`change.patch`, full text in `extract_prompt.md`). One definition of "law" (section, chapter or division, bill, or named program); exactly one record per law and category; the cap, exceptions, deadlines, penalty and amendments of a law all go into that one record; a guide page listing several amendments of one law is still one law; a self-check before answering; the "0 to 6" count replaced by "most packets hold one to three laws". Also one line in the final checklist.

**Targets** clean and one_per_law. **Must not regress** recall, fields, numbers_ok, nonempty.

**Expected size.** About +0.04 to +0.06 on the score if the two target parts reach roughly 0.9. The noise floor is ±0.044 at 2 tries, so the target parts are the clearer evidence.

**What I expect to lose.** Packets that really hold several distinct laws in one category (the handbook D067) could be merged too far: watch recall, fields and nonempty.

**De-fluff pass.** Every sentence added carries an instruction or a check; nothing restates default behaviour.
