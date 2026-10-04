# Round 6: cite the section that holds the headline number, and write no record for a statement that has nothing to cite

Two sentences, both about the `citation` field, taken from what the round 5 side check showed (round 5 was never applied).

1. Under citation style: "When one record covers several sections of one act, cite the section that holds its `key_value` (for example the section that states the cap), not the act's range such as `et seq.`."
2. One bullet in "What counts as one rule": "A statement for which the packet names no law, ordinance, bill or program to cite (for example, that a state has no law on a subject) is not a rule: write no record for it."

**Why (hypothesis).** Two behaviours of the current prompt, both visible on the NJ handbook pages. (a) A guide that explains one act section by section gets one merged record cited by the act's range ("N.J.S.A. 46:8-19 et seq."), so the section that holds the headline number, the one the brief names (46:8-21.2), is lost. Round 5's side check showed the one-line anchor fixes this: 8 of 8 tries cite 46:8-21.2 on D067-01 (training), against 2 of 6 for the round 4 text and 8 of 8 for the original text. (b) A guide also contains statements that are not rules of any named law ("The State of New Jersey has no laws that establish, govern or control rents. Municipalities may pass an ordinance ..."). The model writes a record, has nothing to cite, leaves `citation` empty, and the validator rejects it, so the first answer needs a repair call. The page-title fallback tried in round 5 did not help (7 of 16 tries on D067-02 and D067-04 against 9 of 16 at v4), and a page-title citation would only let a record that matches no key rule through. Not writing the record gives the same final rules without the repair call.

**Evidence in numbers (stored rows).** Records rejected for a missing citation in the climb (tries 0-1, all pages): baseline 4, v1 0, v2 0, v3 1, v4 5. Fresh tries on D067-02 and D067-04 (8 each): v2 2 of 16 tries had one, v3 7, v4 9, round 5 text 7. On the training page D067-02 the records without a citation are two statements: that NJ has no state rent control and leaves it to municipalities (5 of 6 in round 5 tries), and that a landlord may charge for a credit report (1 of 6). Strict section count over the 15 labels with a section-level example in the brief: baseline 28 of 30, v1 26, v2 26, v3 29, v4 28; D067-01 alone 2 of 2, 1 of 2, 1 of 2, 1 of 2, 0 of 2.

**How I found it.** Reading D067-01 and D067-02 (training) and the brief's example citations, then counting tries; D067-04 (held out) was used for counts only and is not part of any decision below.

**Change** (`change.patch`). One line under citation style, one bullet in "What counts as one rule". `primer.md` is unchanged.

**Decision rule, written before the run.** A side check on the two training pages comes first (16 calls: D067-02 and D067-01, 8 tries each, `eval/explore/d067_check/v6/`); the text is applied to the live prompt only if both bars are met: (a) D067-02: at most 1 of 8 tries has a record without a citation (v4 3 of 8, round 5 6 of 8, v3 2 of 8, v2 0 of 8); (b) D067-01: 46:8-21.2 cited in at least 6 of 8 tries. If it passes, apply and run the full set (69 pages, 2 tries). Keep if (a) at most 2 records are rejected for a missing citation in the full pass (v4: 5), AND (b) the strict-section count over the 15 labels is at least v4's 28 of 30, AND (c) `clean` is not below v4's, the full-set score is not below v4's by more than 0.02, one_per_law, nonempty, cite_clean, cite_num, numbers_ok, recall, fields and silver_f1 do not fall outside noise, and the number of accepted records over all pages does not fall by more than 10% against v4, AND (d) the round 4 result holds: D076-01 and R002-01 keep a key_value in tries 0-1 (4 of 4) and the five status-only bill pages stay empty. Otherwise revert to the v4 text.

**Targets** records without a citation and the section cited for a headline number. **Must not regress** (b), (c), (d).

**Expected size.** About +0.003 on the full-set score (a first pass that needs no repair on the handbook pages), so the score cannot show it; the two counts above are the evidence. This is the last round of the plan (6 of 6).

**What I expect to lose.** Records on guide pages that describe a rule without naming any law (they would be dropped; the full pass watches nonempty, silver_f1 and the accepted-record count), and a citation moved to the wrong section when the headline number is not printed next to one (watch the strict count and cite_num). A bill, motion or petition page is not touched: it always names its bill or file number.

**De-fluff pass.** Each sentence says what to write or what to leave out; neither restates default behaviour.

## Result of the side check (fresh tries, training pages only, `eval/explore/d067_check/v6/`)

- (a) D067-02: **0 of 8** tries have a record without a citation, and 0 of 8 needed a repair (v4 3 of 8, round 5 text 6 of 8, v3 2 of 8, v2 0 of 8). Mean records per try 6.2 (v4 7.1). **Bar met** (at most 1 of 8).
- (b) D067-01: 46:8-21.2 cited in **8 of 8** tries (v4 2 of 6). **Bar met** (at least 6 of 8).

Both side-check bars are met, so the candidate text is ready to apply. **It has not been applied and no full pass has been run:** the live prompt files are still the round 4 text. Reason: a review of what the later stages (address lookup, change tests) need from this stage, done after the side check, changed the priorities (see `eval/extraction/REPORT.md` once written, and the project memory note). The full pass for this round costs about $0.45 (69 pages x 2 tries) and can be run any time: apply `v6/change.patch` to `prompts/extract_prompt.md`, run `python3 eval/run_eval.py --variant v6 --reps 2`, then judge it with the rule above.
