# Round 5: put back the two citation defaults that rounds 1 and 3 took away

Two sentences about what to cite. (1) The guide-page bullet gets its fallback back: cite the underlying law as under NAMING A LAW, **or the page title if the page names none**. (2) One new line under citation style: when one record covers several sections of one act, cite **the section that holds its `key_value`**, not the act's range such as `et seq.`.

**Why (hypothesis).** The prompt used to tell the model what to cite when a page gives no single clean citation, and two earlier edits of mine removed those defaults without replacing them. Round 3 replaced "otherwise cite the page title" with a pointer to NAMING A LAW, which has no answer for a statement that names no law at all, so the model writes `citation: null` and the validator rejects the record. Round 1's "a law is ... one named program" lets the model merge several sections of one act into one record and cite the act's range, and the section that holds the headline number is lost. One story about one field.

**Evidence in numbers.**
- No-citation records on the NJ handbook pages. Fresh tries (8 per cell, kept apart in `eval/explore/d067_check/`, D067-02 and D067-04): the round 2 text 2 of 16 tries had one, the round 3 text 7 of 16, the round 4 text 9 of 16. Records rejected for a missing citation in the climb (tries 0-1, all pages): baseline 4, v1 0, v2 0, v3 1, v4 5. Training page D067-02, try 0 of v4, the model's own words about the record it then wrote without a citation: "There's no citation for it. Hmm, risky."
- Section of the headline rule. The brief names N.J.S.A. 46:8-21.2 (1.5 months) for the New Jersey deposit cap; the packet D067-01 (training) prints "one and one-half times one month's rent ( N.J.S.A. 46:8-21.2 )". The original text cites that section in 8 of 8 fresh tries (2 of 2 in the climb). Later rounds, tries 0-1: v1 1/2, v2 1/2, v3 1/2, v4 0/2, the other tries cite "N.J.S.A. 46:8-19 et seq.". The label in `labels.py` accepts either citation (`46:8-(19|21)`), so the score cannot see it. Over the 15 labels that have a section-level example in the brief (`python3 eval/strict_cites.py`): baseline 28 of 30, v1 26, v2 26, v3 29, v4 28.

**How I found it.** Reading what each version wrote on the training page D067-01, then the brief's own example citations, then counting tries on the handbook pages. Not from the score: unlabeled citations and the form of a labeled one are not graded.

**Change** (`change.patch`). Two edits in `prompts/extract_prompt.md`; `primer.md` is unchanged.

**Decision rule, written before the run.** A cheap side check comes first (24 calls: the round 5 text on D067-01, D067-02, D067-04, 8 tries each, in `eval/explore/d067_check/`); nothing is applied to the live prompt until it passes. Side-check bars: (a) at most 3 of the 24 tries have a record without a citation (v4: 9 of 16 on two of the three pages), and (b) 46:8-21.2 is cited in at least 6 of the 8 tries on D067-01. If the side check passes, apply and run the full set (69 pages, 2 tries). Keep if (a) the full pass has at most 2 records rejected for a missing citation (v4: 5), AND (b) the strict-section count over the 15 labels is at least v4's 28 of 30, AND (c) `clean` is not below v4's and the full-set score is not below v4's by more than 0.02, and one_per_law, nonempty, cite_clean, cite_num, numbers_ok, recall and fields do not fall outside noise, AND (d) the round 4 result holds: D076-01 and R002-01 keep their key_value in tries 0-1 (4 of 4) and the five status-only bill pages stay empty. Otherwise revert to the v4 text.

**Targets** records without a citation and the section cited for a headline number. **Must not regress** (b), (c), (d).

**Expected size.** About +0.003 on the full-set score (a first pass that needs no repair on the handbook pages), so the score cannot show it; the two counts above are the evidence. Said up front: this repairs two side effects of my own earlier rounds.

**What I expect to lose.** Page titles as citations on pages whose rules name no law (they never match the hidden key, but they stop the record from being rejected); the new line could move a citation to the wrong section when the headline number is not printed next to a section (watch cite_num and the strict count); records for statements that used to be dropped as "no citation" (watch records per page on D067-02 and D067-04: v4 averages 7.1 and 8.8).

**De-fluff pass.** Each sentence says what to cite; neither restates default behaviour.

## Result of the side check (fresh tries, `eval/explore/d067_check/`)

- (b) Section of the headline rule, D067-01: 46:8-21.2 cited in **8 of 8** tries (v3 3 of 8, v4 2 of 6, original text 8 of 8). **Met.**
- (a) No-citation records: D067-01 0 of 8, D067-02 **6 of 8**, D067-04 1 of 8, together 7 of 24 (bar: at most 3). **Not met.** On the two pages where v4 had 9 of 16, the round 5 text has 7 of 16. The fallback sentence did not do what I expected: the model's reasoning on D067-02 never mentions it, and the records that stay without a citation are the same two statements (a state that has no rent control law and leaves it to cities, 5 of 6; the landlord's right to charge for a credit report, 1 of 6).

Decision, by the rule written before the run: **not applied.** The live prompt stays at the v4 text and no full pass was run for round 5. What the side check did show is that the section-anchor sentence works (8 of 8) and the page-title fallback does not. Round 6 keeps the anchor sentence and tries a different answer for the statements that have nothing to cite.

The side check also had rate-limit trouble: 62 calls came back "too many requests" (HTTP 429) and were re-run at a lower number of simultaneous calls; they are listed in `eval/explore/d067_check/v5/errors.jsonl` and cost nothing.
