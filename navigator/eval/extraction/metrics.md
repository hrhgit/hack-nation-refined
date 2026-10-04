# Metrics

Every metric is in [0, 1], graded by code (eval/grader.py), never by a model.

- **Score** (`score`): Mean of the parts below that apply to the packet (the headline).
- **First pass OK** (`clean`): 1 if the first answer needs no correction: parses, receipt matches, nothing rejected, no law written twice.
- **One per law** (`one_per_law`): 1 minus the share of records that repeat a law already recorded in the same answer.
- **Clean cites** (`cite_clean`): Share of accepted records whose citation is only the citation (no topic or descriptor after it).
- **Numbered cites** (`cite_num`): Share of accepted records whose citation has a section, chapter or bill number, counted only for documents that print such numbers.
- **Dates** (`date_ok`): Share of enacted records whose date is present, supported by the text, and not one the code had to work out from the act's own clause.
- **Numbers in text** (`numbers_ok`): Share of accepted records whose key_value numbers all appear in the source text (a guard against invented numbers).
- **Recall (brief)** (`recall`): Share of the laws listed in labels.py for this packet that the answer contains. Hand-made from the challenge brief.
- **Field accuracy** (`fields`): Of the found labelled laws: share of expected status / effective date / key numbers that are right.
- **Non-empty** (`nonempty`): 0 only when the earlier extraction found rules in this packet and the answer has none; writing more than the earlier extraction is never punished.
- **Cells F1** (`silver_f1`): Diagnostic only, not in the score: F1 of the (jurisdiction, category) cells against the earlier extraction.
- **Accepted** (`rec_ok`): Diagnostic only, not in the score: accepted records / records written.

The score is the plain mean of: clean, one_per_law, cite_clean, cite_num, date_ok, numbers_ok, recall, fields, nonempty (only those that apply to the packet). If the earlier extraction found rules in a packet and the answer has none, clean and one_per_law are forced to 0, so writing nothing cannot earn credit.
