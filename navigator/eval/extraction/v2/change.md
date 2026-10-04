# Round 2: a bill, motion or petition page always gets its record

Tell the model that a page about a pending or failed bill, motion, petition or ballot question is still one record (`pending_bill` or `failed`) even when it shows only a title and a history of actions.

**Why (hypothesis).** The prompt never says what a status-only proposal page yields, so the model sometimes settles the doubt by writing nothing. Round 1 reasoning on D045-01 (train, try 0): "I think it's better to write zero records and note the packet only contains bill status with no operative text ... But could they expect one record with lifecycle pending_bill?" (`eval/extraction/v1/traces/D045-01_rep0.json`). The baseline note on D011-01 (train) says the same: "page has no operative rule text".

**Evidence in numbers (v1).** On the six bill, motion and petition pages the model wrote at least one record in 55 of 60 tries (92%); the misses sit on D039-01 (6 of 8 fresh tries wrote one) and D047-01 (7 of 8). A silent miss is not caught by the pipeline (an empty receipt counts as done) and it costs a pending rule in the change tests T4 and T5.

**Change** (`change.patch`). One bullet in "What counts as one rule" and one line in the final checklist. The bullet limits itself: a bill that is not about one of the six categories still gets no record.

**Decision rule, written before the run.** Keep if the six pages reach at least 97% (58 of 60 tries) AND the full-set score does not fall by more than 0.02 against v1 AND one_per_law and nonempty do not fall outside noise.

**Targets** nonempty and recall on bill pages. **Must not regress** one_per_law, silver_f1, cite_clean, numbers_ok.

**Expected size.** About +0.003 on the full-set score, so it cannot be seen there; the six-page slice at ten tries is the evidence.

**What I expect to lose.** More records on pages that mention a bill in passing; watch silver_f1 and records per packet.

**De-fluff pass.** The new bullet says what to write and what to leave out; nothing restates default behaviour.
