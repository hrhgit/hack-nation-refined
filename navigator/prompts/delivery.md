# DELIVERY (read before you answer)

There are two ways to hand in your work. Use the one that matches your tools.

## A. You can create files and run shell commands (coding agent / IDE assistant)

1. Write your complete answer to this exact file with your file-writing tool (not a shell heredoc: quotes inside the JSON break it):

   `{{OUT_FILE}}`

   Format: UTF-8 text, JSON Lines. One JSON object per line. No markdown fences, no headings, no commentary. For each packet, in order: its rule records, then its receipt line. The records go into the file, not into the chat.
2. Then run these in `{{WORKDIR}}`:

   ```
   cd {{WORKDIR}}
   python3 run.py ingest
   python3 run.py status
   ```

   `ingest` validates your file against the source text and prints a summary. Read it, and open `work/report.md` if anything was rejected.
3. Then run `python3 run.py bundle`. It writes fresh batch files for the packets that are still open: not answered yet, or `needs_fix` / `incomplete` / `mismatch` (those come back with their problems listed above them). It prints the file names. Open the **first** file it lists, read it all, answer it the same way (its own DELIVERY section gives its exact output path), and run `ingest` again.
4. Repeat step 3 until `status` shows every packet as `done`. After three failed attempts on the same packet, stop retrying that packet and mention it in your final message. If `bundle` says nothing is pending, you are finished.
5. Change nothing except by adding `.jsonl` answer files under `work/out/`. Never edit code, `outputs/` or earlier answer files. Never write a script that generates records: read the text and write the records yourself.
6. Your chat reply is two or three lines: the file you wrote and the `ingest` summary line.

## B. You can only chat (no file access)

Reply with the JSON Lines answer only, exactly as described above. The user will save it.
