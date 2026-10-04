# Format change check (not a hill-climb round)

The extraction prompt got a new output format so that the address lookup and change tests can use it (see
`docs/STAGE1_CONTRACT.md`). Output fields were off-limits to the hill-climb, so this is recorded here, outside
`eval/extraction/`, and it does not change the climb's state, best round or numbers.

- Prompt: `prompts/extract_prompt.md` sha256 `64483a56a5a09138…`, `prompts/primer.md` `7e2a8ba4fe84f8ba…`
  (the old text, round 4, is in `eval/extraction/v4/`; copies of the other files changed on 2026-10-04 are in `eval/extraction/_harness_before_contract_v2/`).
- Run: all 69 cases, ONE try each, `deepseek-flash`, concurrency 2, spend $0.28.
- Compared with round 4 try 0 (same 69 cases, same grader, ingest re-run on the stored answers).

| part | round 4 | new | change (95% half-width) |
|---|---|---|---|
| score | 0.954 | 0.944 | -0.010 (0.027) |
| first pass OK | 0.928 | 0.942 | +0.014 (0.049) |
| one record per law | 0.966 | 0.938 | -0.029 (0.033) |
| numbered cites | 0.973 | 0.943 | -0.030 (0.042) |
| dates | 1.000 | 1.000 | 0.000 |
| numbers in text | 0.984 | 0.992 | +0.008 (0.016) |
| recall (brief) | 1.000 | 1.000 | 0.000 |
| field accuracy | 1.000 | 0.987 | -0.013 (0.025) |
| non-empty | 0.971 | 0.957 | -0.014 (0.028) |

Reading it
- Every change is inside its own interval. One try each, so it is weaker evidence than the climb's two tries.
- The first run showed a date drop (-0.036). It came from a new warning of mine ("valid_through ... does not appear in ...") that the grader's
  string match counted as a bad effective date. The wording was changed and the stored answers were graded again: dates are 1.000.
- Most of the score difference is one page: D012-01 (Boston Fair Housing Regulations) came back empty once. Three more runs of it all wrote the record.
- D004-01 (two records for one Berkeley law) and D043-01 were run again: D004-01 gave one record both times; D043-01 varies between 3 and 4 records, as it did before.
- Cost per call went up: mean 6.3k output tokens against 4.7k, because the model now reasons about the conditions (about 25 s a call).
- Not measured: whether the new fields are right. That is checked on the real run (a table of every rule's conditions with the quoted text).
