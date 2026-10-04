# RUN_EXTRACTION: do the whole extraction job yourself

You are an AI agent with file access and a shell. Your job is to turn a corpus of public U.S. housing law into validated rule records. The corpus is already cut into packets and the checking scripts are already written. You do two things: **read packets and write JSON**, and **run the scripts**. Work on your own from start to finish. Do not ask the user questions unless you hit a blocker listed under "When to stop".

Repository: `/Users/herh/MyFiles/Projects/hack-nation/navigator`. Run every command from that directory.

## 0. Check the setup

```
cd /Users/herh/MyFiles/Projects/hack-nation/navigator
npm ci
npm test
npm run nav -- status
```

The tests must pass without failures. `status` shows how many packets are `pending` (65 on a fresh start; fewer if a previous run already did some). All progress lives in files, so you can stop and resume at any time: after a restart or a context reset, run `status` and continue at step 1.

## 1. The loop (one batch at a time)

1. `npm run nav -- bundle`
   It prints the names of batch files in `work/paste/`. Each one covers only packets that still need an answer.
2. Open the **first** batch file and read all of it. It has three parts: the extraction instructions, a `# DELIVERY` section with the exact output path for this batch, and the source packets.
   - If your file reader cuts the file off, read it in slices (for example with `sed -n '1,400p'`) until you have seen everything. Never answer from a partial read.
   - If your context is small (under about 100k tokens), run `npm run nav -- bundle --paste-chars 25000` instead, to get smaller batches.
3. Write the answer: **UTF-8 JSON Lines, saved to the path named in the batch's DELIVERY section** (always `work/out/<batch name>.jsonl`). Use your file-writing tool, not a shell heredoc. For each packet, in order: its rule records, then its one receipt line. No markdown fences, no headings, no commentary inside the file. The field definitions, categories and rules are in the batch file; follow them exactly.
4. `npm run nav -- ingest`
   It validates every record against the source text and prints one summary line, for example `answer files: 3 | records: 40 | accepted: 36 | rejected (open): 4 | rules: 31 | packets done: 12/65`. It also writes `outputs/rules.json` and `work/report.md`.
5. Go back to step 1. The next `bundle` automatically drops packets that are `done` and brings back any packet that was rejected, cut off or miscounted, with the problems listed above that packet. Answer those problems like any other batch.

Stop looping according to "When to stop".

## 2. What the files look like

Each packet gets its records followed by one receipt:

```
{"packet_id":"D024-01","doc_id":"D024","jurisdiction":"CA","category":"rent_increase_limits", ... "quoted_span":"<verbatim from the packet>", ...}
{"packet_id":"D024-01","n_rules":1,"note":null}
```

`n_rules` is the number of records you wrote for that packet in this file. A packet with no relevant rule still gets its receipt (`n_rules` 0). The batch file lists every field.

## 3. Fixing rejections

`ingest` rejects a record only for a concrete reason, printed in `work/report.md` under "Rejected records" and repeated above the packet in the next `bundle`:

| message | what to do |
|---|---|
| `quoted_span not found in D0xx` | You paraphrased or merged sentences. Copy one passage exactly from the packet; a shorter passage is fine. |
| `category ... is not one of` / `lifecycle ... must be` | Use the exact allowed values. |
| `effective_date ... is not a date` | Use `YYYY-MM-DD`, `YYYY-MM`, `YYYY`, or `null`. |
| `doc_id ... does not match packet` | Copy `packet_id` and `doc_id` from the packet header. |
| `jurisdiction ... must be a state code or 'City, ST'` | Use `CA`, `NJ`, `MA`, or `City, ST`. |
| `no receipt line` / `receipt n_rules=...` | Your earlier answer was cut off or miscounted. Answer the packet again and finish with its receipt. |

Warnings on accepted records (for example "effective_date ... does not appear in the document") are for the human reviewer. Do not chase them afterwards, but while writing, use only dates and numbers that are in the packet, and put `null` where the packet is silent.

After **three** failed attempts on the same packet, stop retrying that packet and list it in your final message. (You can see attempts as `_r2`, `_r3` files in `work/out/`.)

## 4. Hard rules

- Use only the text in the packets. No outside knowledge, no web access, no memory of what a statute "really" says.
- Write the records yourself by reading. Do not write scripts, regexes or notebooks that generate records.
- Change nothing except by adding `.jsonl` answer files to `work/out/`. Do not edit code, `prompts/`, `outputs/`, `work/packets/`, `work/paste/`, or earlier answer files, and do not delete anything.
- Not legal advice: you extract what the text says, nothing more.

## 5. When to stop

- `npm run nav -- status` shows every packet as `done`, or
- only packets you gave up on after three attempts remain, or
- a blocker: the tests fail, a script crashes with a traceback, or a file named above is missing. Stop and report the exact error. Do not try to repair the pipeline yourself.

Then run `npm run nav -- ingest` one last time.

## 6. Final message to the user (at most 25 lines)

1. The last `ingest` summary line.
2. The coverage matrix copied from `work/report.md` (jurisdiction by category).
3. Packets you gave up on, with the rejection reasons.
4. The first ten entries under "Rules to check by hand" in `work/report.md`.
5. One sentence: 33 documents in the corpus have no text (see `work/COVERAGE_GAPS.md`), so rules that exist only in those documents cannot be extracted until someone supplies the text. Do not try to fetch them yourself.
