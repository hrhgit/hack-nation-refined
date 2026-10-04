# Extraction eval (prompt hill-climb)

**Current recommended checks:** [v2/README.md](v2/README.md) adds document/family grouping, explicit omissions and applicability errors, new synthetic validation/final cases, and the shipped TypeScript extraction/lookup path. This directory remains the historical extraction regression suite; its old score is not a complete product acceptance result.

Measures how well the extraction prompt works with the real model, without an answer key from the organisers.
Grading is done by code (`grader.py`), never by a model. Everything the grader needs is in this folder.

| file | what it is |
|---|---|
| `INPUTS.md` | the 69 cases (65 real packets + 4 invented rehearsal pages) and the 28 hand-made expected laws, for review |
| `labels.py` | expected laws, written by hand from the challenge brief; a label accepts any citation that names the right law |
| `grader.py` | scores one answer to one packet (9 parts, mean = `score`) |
| `run_eval.py` | runs every case x try through the real API path; resumable; failures go to `errors.jsonl` |
| `status.py` | status table recomputed from raw rows |
| `compare.py` | every comparison number (levels, paired change with its confidence, every part, cost), recomputed from raw rows |
| `bill_values.py` | diagnostic: do bill pages keep a figure the page states, and stay empty when it states none |
| `strict_cites.py` | diagnostic: does an answer cite the exact provision the brief names for its own example rules |
| `cond_labels.py`, `conditions_run.py`, `conditions_check.py` | answer key for the coverage conditions (contract v2) and its runner and checker, see `CONDITIONS.md`; explore-mode, outside the harness |
| `train_view.py` | the only way transcripts are read while choosing a change: training packets only |
| `cases.json`, `silver.json` | frozen case list with the train/test split, frozen copy of the earlier extraction |
| `oracle/oracle.jsonl` | hand-made ideal answers; must score 1.0 (tested) |
| `rehearsal/` | four invented documents with hand-written answers, stand-ins for the unseen hour-16 ordinance |
| `pilot/` | the stored Claude answers graded by this grader, for reviewing the grading (no model call) |
| `explore/` | side runs (first look at the model, noise checks); never part of the climb |
| `extraction/` | the climb: `_state.json`, `narrative.md`, `report.html`, `baseline/`, `v1/`, ... Each round has `change.md` (why, the keep rule written before the run, the result), `change.patch`, a copy of the prompt files, `results.jsonl` and `traces/` |

```bash
python3 eval/run_eval.py --variant baseline --dry-run         # shows what would run, spends nothing
python3 eval/run_eval.py --variant baseline --approve-harness # a person runs this once, after reading the harness
python3 eval/run_eval.py --variant baseline                   # the paid pass; run it again to resume
python3 eval/status.py                                        # one row per round
python3 eval/compare.py --a baseline --b v4                   # the numbers behind the headline
```

Changing any file listed under `harness_paths` in `extraction/_state.json` (grader, labels, silver, runner, the checks in `nav/`)
makes the next paid run stop until a person runs `--approve-harness` again.

Known limits: see the end of `INPUTS.md` and the last section of `v2/README.md`.
