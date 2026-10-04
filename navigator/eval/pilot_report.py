"""Grade the stored sub-agent answers (no model call) into eval/pilot/baseline, so the grading can be reviewed."""
from __future__ import annotations

import json
import shutil
import sys

from common import HERE, load_cases, load_ctx
from grader import grade
from nav.packets import render_prompt
from stored_answers import stored_answers

PILOT = HERE / "pilot"


def main() -> int:
    ctx = load_ctx()
    cases = load_cases()
    answers = stored_answers(ctx)
    prompt = render_prompt(ctx.as_of)
    if PILOT.exists():
        shutil.rmtree(PILOT)
    (PILOT / "baseline" / "traces").mkdir(parents=True)
    state = json.loads((HERE / "extraction" / "_state.json").read_text(encoding="utf-8"))
    state.update({"harness_sha": None, "current_round": 0})
    (PILOT / "_state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    rows = []
    for c in cases:
        if c["kind"] == "rehearsal":
            continue   # no stored answer exists for the invented documents
        text = answers.get(c["id"], "")
        res = grade(ctx, c["id"], text, "stop")
        packet = ctx.packet_file(c["id"]).read_text(encoding="utf-8")
        rows.append({"prompt_id": c["id"], "rep": 0, "prompt": packet, "tags": c["tags"], "grade": res["grade"],
                     "explanation": res["explanation"], "model": "claude-subagent (stored answer)", "status": res["status"],
                     "latency_s": 0, "usage": {"input_tokens": 0, "output_tokens": 0},
                     "meta": {"accepted": res["accepted"], "rejected": res["rejected"], "split": c["split"]}})
        (PILOT / "baseline" / "traces" / ("%s_rep0.json" % c["id"])).write_text(json.dumps(
            [{"role": "system", "content": prompt}, {"role": "user", "content": packet},
             {"role": "assistant", "content": text}], ensure_ascii=False, indent=1), encoding="utf-8")
    (PILOT / "baseline" / "results.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    (PILOT / "baseline" / "summary.json").write_text(json.dumps({
        "description": "Pilot: answers already written by Claude sub-agents under the old prompt, graded by the new grader. No model call."}, indent=2))
    print("pilot rows:", len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
