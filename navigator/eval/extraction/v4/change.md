# Round 4: a bill page keeps the number it states

Repairs a side effect of round 2. The round 2 bullet tells the model to leave `key_value` empty on every page about a bill. That is right for a page that shows only a title and a list of actions, and wrong for a page that states what the bill would set (a cap, a fee, a penalty). New wording: `effective_date` stays empty, `key_value` stays empty unless the page states the number the proposal would set, and the quoted line is the one that states it.

**Why (hypothesis).** The instruction is unconditional ("leave `key_value` ... `null`"), so the model drops a figure the page gives. Nothing else in the prompt asks for it back.

**Evidence in numbers (stored rows, `python3 eval/bill_values.py`).** D076-01 (train): a pending bill whose page states "$1,000 per violation"; the earlier Claude answer kept that figure. Its key_value was filled in 2 of 2 tries at v1 and in 0 of 2 at v2 and at v3. The invented docket R002-01 (a $50 cap per application) scored 1.00 at v1 (filled, 2 of 2) and 0.94 at v2 and v3 (empty, `fields` 0.5). Over the two pages the tries with a key_value are: baseline 3 of 4, v1 12 of 12, v2 2 of 12, v3 0 of 4. On the five status-only bill pages the key_value is empty in every variant (0 of 60 records at v2): that has to stay so.

**How I found it.** Not from the score: unlabeled bill pages are not graded on key_value, and R002-01 is one case in 69. I looked at the five imperfect training pages after round 3 and then at what each variant wrote on the bill pages. R002-01 (a held-out rehearsal case) was opened for this; from here on it no longer counts as unseen. The change is justified by D076-01, a training page.

**Change** (`change.patch`). One bullet in "What counts as one rule", three clauses reworded. No new line in the checklist.

**Decision rule, written before the run.** Keep if (a) on the two figure pages (D076-01, R002-01) at least 18 of 20 tries (tries 0-9) carry a key_value, AND (b) on the five status-only pages (D011-01, D039-01, D045-01, D046-01, D047-01) at most 2 records in all carry a key_value, AND (c) all seven pages still write a record in at least 97% of tries (at most 2 empty in 70), AND (d) the full-set score does not fall by more than 0.02 against v3, and one_per_law, nonempty, cite_clean, numbers_ok, recall and fields do not fall outside noise. Otherwise revert to the v3 text.

**Targets** key_value on bill pages that state a figure. **Must not regress** (b), (c) and the guardrails in (d).

**Expected size.** About +0.001 on the full-set score (R002-01 `fields` 0.5 -> 1.0 is the only graded part), so the full set cannot show it. The slice at ten tries is the evidence, as in round 2. It is a repair, not an improvement the eval was built to see.

**What I expect to lose.** The model could copy a bill number or a docket number into key_value on a status-only page ((b) watches it), or a figure of the current law that the page mentions in passing (I will read the filled records of the training page and count the rest).

**De-fluff pass.** Every clause says what to write or what to leave empty; nothing restates default behaviour.
