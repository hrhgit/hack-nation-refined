"""Step-by-step extraction: the model reads reference cards when it needs them and checks its own records before it answers.

The single-shot prompt (prompts/extract_prompt.md) puts every rule in front of the model at once. Here the model gets a short core
(prompts/agent/core.md) and may call two tools before it answers:

  read_card(name)           a short reference card (prompts/agent/cards/<name>.md) for one kind of field
  check_record(record_json) this pipeline's own validator on one finished record, plus what its conditions do to made-up buildings

The final message is the same JSON Lines answer as in the single-shot run, so ingest, the checks and the re-ask-on-rejection flow are
unchanged. There is no cap on the number of steps (the repo's AGENTS.md asks for none); each packet's conversation is archived whole in
work/api/, with the cards it read and the number of self-checks.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import threading
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .api import ApiConfig, ApiError, _select
from .config import KNOWN_JURISDICTIONS, ROOT, Paths, load_schema
from .corpus import load_corpus
from .ingest import Validator, pending_packets, run_ingest, write_outputs
from .packets import load_index, render_packet_input
from .parse import classify, extract_json_objects

import os

AGENT_DIR = Path(os.environ.get("NAV_AGENT_DIR") or ROOT / "prompts" / "agent")   # the override is for A/B tests of card sets
AS_OF = "2026-10-01"
PROBES = [(2022, 20, None), (2005, 20, None), (1990, 20, None), (1970, 20, None), (None, 20, None),
          (1950, 2, None), (1950, 5, None), (1950, None, None)]
WORDS = {"applies": "applies", "unknown": "unknown (a fact is missing)", "excluded": "NOT in the results (the building is left out)",
         "not_yet_effective": "not yet effective", "pending": "pending (a proposal)", "superseded": "superseded"}
CITY_FOR_STATE = {"CA": "Los Angeles, CA", "NJ": "Newark, NJ", "MA": "Boston, MA"}
Post = Callable[[List[Dict[str, Any]], List[Dict[str, Any]]], Dict[str, Any]]


# ---------------------------------------------------------------- prompt and cards

def card_names() -> List[str]:
    return sorted(p.stem for p in (AGENT_DIR / "cards").glob("*.md"))


def load_cards() -> Dict[str, str]:
    return {n: (AGENT_DIR / "cards" / (n + ".md")).read_text(encoding="utf-8") for n in card_names()}


def render_core(as_of: str) -> str:
    raw = (AGENT_DIR / "core.md").read_text(encoding="utf-8")
    return raw.replace("{{AS_OF}}", as_of).replace("{{JURISDICTIONS}}", ", ".join('"%s"' % j for j in KNOWN_JURISDICTIONS))


def tool_specs(tools=("cards", "check")) -> List[Dict[str, Any]]:
    specs: List[Dict[str, Any]] = []
    if "cards" in tools:
        specs.append({"type": "function", "function": {
            "name": "read_card", "description": "Read one short reference card with the detailed rules for one kind of field.",
            "parameters": {"type": "object", "properties": {"name": {"type": "string", "enum": card_names()}}, "required": ["name"]}}})
    if "check" in tools:
        specs.append({"type": "function", "function": {
            "name": "check_record", "description": "Run the pipeline's checks on one finished record and show how a program will read its conditions.",
            "parameters": {"type": "object", "properties": {"record_json": {"type": "string", "description": "one record as a JSON object, as text"}},
                           "required": ["record_json"]}}})
    return specs


# ---------------------------------------------------------------- the self-check tool

def outcome(rule: Dict[str, Any], facts: Dict[str, Any], as_of: str) -> str:
    """What the address lookup does with this one rule for a building with these facts."""
    from lookup.engine import LookupEngine
    state = rule["jurisdiction"] if rule["level"] == "state" else rule["jurisdiction"].rsplit(", ", 1)[-1]
    city = rule["jurisdiction"] if rule["level"] == "city" else CITY_FOR_STATE.get(state, state)
    address = {"state": state, "legal_city": city, "resolved_by": "geocoder", **facts}
    rows = LookupEngine([dict(rule, team_rule_id="probe")], {"P": address}, precedence=[], review=[]).lookup("P", as_of)
    return rows[0]["result"] if rows else "excluded"


def describe_conditions(a: Dict[str, Any]) -> str:
    keys = ["built_on_or_before", "built_before", "built_after", "built_on_or_after", "min_units", "max_units",
            "exempt_if_newer_than_years", "owner_exempt_if_units_at_most", "date_basis"]
    parts = ["%s=%s" % (k, a[k]) for k in keys if a.get(k) is not None]
    if a.get("owner_dependent"):
        parts.append("owner_dependent" + ("" if a.get("owner_exempt_if_units_at_most") is not None
                                          else " (no size limit: every building comes out unknown)"))
    if a.get("other"):
        parts.append("unresolved: %s" % a["other"])
    if a.get("program_notes"):
        parts.append("note only (kinds of housing the data cannot show): %s" % "; ".join(a["program_notes"])[:160])
    for d in a.get("deferred") or []:
        parts.append("exemption only if the owner filed (open inside its reach): %s" % d["note"])
    if a.get("per_tenancy"):
        parts.append("note: %s" % a["per_tenancy"][:100])
    return "; ".join(parts) or "none (the rule covers every building)"


def check_record(validator: Validator, lock: threading.Lock, record_json: str) -> str:
    try:
        raw = json.loads(record_json)
    except ValueError as e:
        return "NOT VALID JSON: %s. Send one record as a JSON object." % e
    if not isinstance(raw, dict):
        return "Send one record as a JSON object."
    with lock:
        rule, errors, warns = validator.check(raw)
        if rule is None:
            return "REJECTED. Fix and check again:\n- " + "\n- ".join(errors)
        lines = ["ACCEPTED." + (" Warnings:\n- " + "\n- ".join(warns) if warns else "")]
        lines.append("How a program reads it: citation %r; lifecycle %s; effective_date %s; valid_through %s." % (
            rule["citation"], rule["lifecycle"], rule["effective_date"], rule["valid_through"]))
        lines.append("Conditions it will test: " + describe_conditions(rule["applicability"]))
        if rule["relations"]:
            lines.append("Relations kept: " + ", ".join(r["type"] for r in rule["relations"]))
        if rule["lifecycle"] == "enacted":
            lines.append("What the conditions do to made-up buildings on %s (year built, units):" % AS_OF)
            for year, units, lower in PROBES:
                got = outcome(rule, {"year_built": year, "units": units, "units_at_least": lower}, AS_OF)
                lines.append("  built %s, %s units -> %s" % (year or "unknown year", units if units is not None else "unknown", WORDS.get(got, got)))
    return "\n".join(lines)


# ---------------------------------------------------------------- one packet, several steps

def make_post(config: ApiConfig) -> Post:
    def post(messages: List[Dict[str, Any]], specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"model": config.model, "stream": False, "messages": messages}
        if specs:
            payload["tools"] = specs
        req = urllib.request.Request(config.endpoint, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                                     headers={"Content-Type": "application/json", "Authorization": "Bearer " + config.key}, method="POST")
        hints = {401: "密钥无效，请检查配置。", 402: "账户余额不足。", 403: "账户没有调用权限。", 429: "服务当前限制请求，请稍后重新运行。"}
        try:
            with urllib.request.urlopen(req, timeout=None) as r:     # no timeout and no automatic retries, as in nav.api
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            code = e.code
            e.close()
            raise ApiError("API 请求失败（HTTP %d）。%s 已保存的进度可继续使用。" % (code, hints.get(code, "请检查 API 地址、模型名或服务状态。"))) from None
        except (urllib.error.URLError, OSError, ValueError):
            raise ApiError("无法完成 API 连接。请检查网络和 API 地址，然后重新运行。") from None
    return post


def converse(post: Post, system: str, user: str, cards: Dict[str, str], validator: Validator, lock: threading.Lock,
             tools=("cards", "check")) -> Tuple[str, Dict[str, Any]]:
    """Run the step-by-step conversation for one packet. Returns the final text and a log of what happened."""
    specs = tool_specs(tools)
    messages: List[Dict[str, Any]] = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    log: Dict[str, Any] = {"steps": 0, "cards_read": [], "checks": 0, "usage": []}
    while True:
        body = post(messages, specs)
        log["steps"] += 1
        log["usage"].append(body.get("usage") or {})
        try:
            choice = body["choices"][0]
            message = {k: v for k, v in choice["message"].items() if v is not None}
            reason = choice["finish_reason"]
        except (KeyError, IndexError, TypeError):
            raise ApiError("API 返回内容缺少 choices/message/content 或 finish_reason。") from None
        messages.append(message)
        if not message.get("tool_calls"):
            if reason != "stop":
                raise ApiError("回答未正常结束（%s）。" % reason)
            log["messages"] = messages[2:]
            return message.get("content") or "", log
        for call in message["tool_calls"]:
            name = call["function"]["name"]
            try:
                arg = json.loads(call["function"].get("arguments") or "{}")
            except ValueError:
                arg = {}
            if name == "read_card":
                log["cards_read"].append(arg.get("name"))
                result = cards.get(arg.get("name")) or "No such card. Cards: " + ", ".join(sorted(cards))
            elif name == "check_record":
                log["checks"] += 1
                result = check_record(validator, lock, arg.get("record_json", ""))
            else:
                result = "Unknown tool."
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})


def check_final(text: str, pid: str) -> None:
    """The same acceptance tests as nav.api.run_api applies to a single-shot answer."""
    objects, parse_problems = extract_json_objects(text)
    if parse_problems:
        raise ApiError("%s 的回答有无法解析或未写完的 JSON，已保留原始回答，未导入。" % pid)
    relevant = [o for o in objects if classify(o) != "other"]
    if not relevant:
        raise ApiError("%s 的回答没有规则或收据。" % pid)
    if any(o.get("packet_id") != pid for o in relevant):
        raise ApiError("%s 的回答包含其他分包编号，已保留原始回答，未导入。" % pid)
    receipts = [o for o in relevant if classify(o) == "receipt"]
    if len(receipts) > 1 or any(type(o.get("n_rules")) is not int or o["n_rules"] < 0 for o in receipts):
        raise ApiError("%s 的收据重复或条数不是非负整数，已保留原始回答，未导入。" % pid)


# ---------------------------------------------------------------- the pipeline loop

def run_agent_api(paths: Paths, config: Optional[ApiConfig], only: Optional[List[str]] = None, once: bool = False,
                  dry_run: bool = False, rules_format: str = "wrapped", workers: int = 1, post: Optional[Post] = None,
                  emit: Callable[[str], None] = print) -> int:
    index = load_index(paths)
    system = render_core(index["as_of"])
    res = run_ingest(paths, persist_ids=not dry_run)
    todo = _select(pending_packets(res), index, only)
    packets: Dict[str, str] = {}
    for pid in todo:
        f = paths.packets_dir / (pid + ".md")
        if not f.exists():
            raise ApiError("缺少分包 %s，请先运行 prepare。" % pid)
        raw = f.read_bytes()
        if hashlib.sha256(raw).hexdigest() != index["packets"][pid]["sha256"]:
            raise ApiError("分包 %s 与目录记录不一致，请先运行 prepare。" % pid)
        packets[pid] = raw.decode("utf-8")
    emit("分步模式 | 模型：%s | 待处理：%d 个分包 | 已完成：%d/%d | 并行：%d" %
         (config.model if config else "-", len(todo), res.counts["packets_done"], res.counts["packets_total"], workers))
    if dry_run:
        for pid in todo:
            emit("  %s%s" % (pid, "（需修正）" if todo[pid] else ""))
        emit("预览完成，未调用 API。")
        return 0
    if not todo:
        write_outputs(paths, res, rules_format)
        emit("所选范围没有待处理分包。结果：%s" % (paths.out_dir / "rules.json"))
        return 0
    if post is None:
        if config is None or not config.key:
            raise ApiError("尚未配置 API 密钥。")
        post = make_post(config)
    validator = Validator(load_corpus(paths), index, load_schema(paths), index["as_of"])
    cards = load_cards()
    archive = paths.work_dir / "api"
    archive.mkdir(parents=True, exist_ok=True)
    paths.inbox_dir.mkdir(parents=True, exist_ok=True)
    check_lock, ingest_lock = threading.Lock(), threading.Lock()
    state = {"res": res}
    errors: List[str] = []

    def work(item: Tuple[str, List[str]]) -> None:
        pid, problems = item
        try:
            text, log = converse(post, system, render_packet_input(pid, packets[pid], problems), cards, validator, check_lock)
            attempt = "AGENT_%s_%s_%s" % (pid, dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%f"), uuid.uuid4().hex)
            (archive / (attempt + ".json")).write_text(json.dumps({
                "packet_id": pid, "model": config.model if config else None, "as_of": index["as_of"],
                "prompt_sha256": hashlib.sha256(system.encode("utf-8")).hexdigest(), "steps": log["steps"],
                "cards_read": log["cards_read"], "checks": log["checks"], "usage": log["usage"], "messages": log["messages"]},
                indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            (archive / (attempt + ".txt")).write_text(text, encoding="utf-8")
            check_final(text, pid)
            with ingest_lock:
                (paths.inbox_dir / (attempt + ".jsonl")).write_text(text, encoding="utf-8")
                state["res"] = run_ingest(paths)
                write_outputs(paths, state["res"], rules_format)
                s = state["res"].states[pid]
                emit("  %s：%s（%s）；%d 步，读了 %s，自检 %d 次。" % (pid, s["state"], s["detail"], log["steps"], log["cards_read"] or "-", log["checks"]))
        except (ApiError, OSError) as e:
            errors.append("%s：%s" % (pid, e))
            emit("  %s：失败：%s" % (pid, e))

    while todo:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            list(pool.map(work, list(todo.items())))
        todo = _select(pending_packets(state["res"]), index, only)
        if once or errors:
            break
    res = state["res"]
    emit("已完成：%d/%d | 规则：%d | 所选范围剩余：%d\n结果：%s\n检查报告：%s" %
         (res.counts["packets_done"], res.counts["packets_total"], res.counts["rules"], len(todo),
          paths.out_dir / "rules.json", paths.work_dir / "report.md"))
    if errors:
        emit("有 %d 个分包没有完成（API 或回答格式问题），已保存的进度仍在，重新运行会继续：\n  %s" % (len(errors), "\n  ".join(errors)))
        return 1
    return 2 if todo else 0
