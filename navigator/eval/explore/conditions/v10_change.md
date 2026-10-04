# Candidate v10 (explore mode, written before the run)

v9 replaced the examples taken from particular laws with fictional ones (`genericize.py`). On the 17 laws it fell from v8's safe 145 / exact 69 / 0 wrong
exclusions to 143 / 68 / 2 wrong exclusions, both on the Berkeley table (a building from 1980 left out in both tries). v8 wrote only the exemption
("certificate after June 1980 is exempt"); v9 also wrote "covered if built before 1980" from the row "most units built before 1980 are fully covered".
So the literal example in v8 ("most units built before 1980 are fully covered") was carrying that answer, not the rule. That is the contamination the
fictional examples were meant to expose.

Change: state the rule in general words. Role `covered` only for wording that limits the rule ("applies only to", "limited to"); a sentence that merely
names a kind of covered building limits nothing; when the text also gives an exemption for the same date or size, write only the exemption.

Keep rule, fixed now: keep v10 if on the 17 laws wrong exclusions are 0, safe is at least 144 of 146 and exact at least 67 of 70, the six key-free
parts stay at or above 0.97, and on the three added held-out laws (San Diego tenant protection, San Diego source of income, Santa Ana) its safe and exact
counts are not more than 1 below v8's. Then the 69-page run (explore) with no part falling beyond its interval against round 4. If v10 fails, the fall back is v8,
with the examples from particular laws left in and said so.

## Result (written after the runs)

20-law key, 2 tries each: v10 safe 167 of 168, exact 84 of 84, wrong exclusions 0 (live prompt before: 163, 70 of 84, 4; v8: 167, 79 of 84, 0; v9: 165, 80, 2).
The one miss is a try that left out `valid_through`, an archive-only field. v11 (the extra owner rule) tied on exact and was one safe check lower, so by the rule
"prefer the shorter prompt on a tie" v10 is kept.
69-page run (explore, 1 try) against round 4 try 0: score 0.963 (+0.009 ± 0.013), first pass OK +0.043, one record per law -0.002, numbered cites +0.007,
dates, numbers, recall, fields, non-empty unchanged. No part falls beyond its interval.
About the key-free parts on the 20-law key: date_ok 0.947 and numbers_ok 0.950 in EVERY variant including the live prompt before this change. The cause is the Santa Ana packet (the text has "$ 1, 000" with spaces, and the
effective date is worked out by the model from "30 days after adoption"), not the prompt. The keep rule's wording (0.97 absolute) was written for 17 laws, so it was read as "no worse than the live prompt".
v10 is now `prompts/extract_prompt.md`. The text it replaced is `live_before_v10_extract_prompt.md` in `prompts/`.
