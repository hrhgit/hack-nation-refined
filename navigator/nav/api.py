"""Call DeepSeek (or a Chat Completions compatible API) and use the existing checks."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .config import Paths, ROOT
from .ingest import pending_packets, run_ingest, write_outputs
from .packets import load_index, render_packet_input, render_prompt
from .parse import classify, extract_json_objects


class ApiError(Exception):
    """An actionable API/configuration failure, without credentials in its message."""


@dataclass
class ApiConfig:
    key: str
    model: str = "deepseek-flash"
    base_url: str = "https://api.deepseek.com"

    @property
    def endpoint(self) -> str:
        url = urllib.parse.urlsplit(self.base_url)
        if (not url.hostname or url.username or url.password or url.query or url.fragment
                or url.scheme not in {"https", "http"}):
            raise ApiError("API 地址必须是无用户名、密码或查询参数的 https 地址。")
        if url.scheme == "http" and url.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ApiError("远程 API 地址必须使用 https；http 仅用于本地测试。")
        return self.base_url.rstrip("/") + "/chat/completions"


def load_api_config(env_file: Optional[Path] = None, model: Optional[str] = None,
                    base_url: Optional[str] = None, require_key: bool = True) -> ApiConfig:
    """Read simple KEY=value lines; never execute shell code or overwrite the environment."""
    values: Dict[str, str] = {}
    f = env_file if env_file is not None else ROOT / ".env"
    if f.exists():
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, sep, value = line.partition("=")
            if not sep:
                raise ApiError("配置文件第 %d 行应为 KEY=value。" % n)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            values[name.strip()] = value
    elif env_file is not None:
        raise ApiError("指定的配置文件不存在。")

    def get(name: str, default: str = "") -> str:
        return os.environ.get(name, values.get(name, default)).strip()

    key = get("NAV_API_KEY") or get("DEEPSEEK_API_KEY")
    if require_key and (not key or key == "your-deepseek-api-key"):
        raise ApiError("尚未配置密钥。请在 navigator/.env 填入 DEEPSEEK_API_KEY，或设置同名环境变量。")
    config = ApiConfig(key, model or get("NAV_API_MODEL", "deepseek-flash"),
                       base_url or get("NAV_API_BASE_URL", "https://api.deepseek.com"))
    if not config.model.strip():
        raise ApiError("模型名不能为空。请设置 NAV_API_MODEL 或 --model。")
    config.endpoint  # validate before any requests
    return config


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # A redirect must never forward the Authorization header to another host.
        return None


class ChatClient:
    def __init__(self, config: ApiConfig):
        self.config = config
        self.opener = urllib.request.build_opener(_NoRedirect())

    def complete(self, prompt: str, packet: str) -> Dict:
        payload = {"model": self.config.model, "stream": False,
                   "messages": [{"role": "system", "content": prompt},
                                {"role": "user", "content": packet}]}
        request = urllib.request.Request(
            self.config.endpoint, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.config.key},
            method="POST")
        try:
            # No application timeout, token cap, truncation, or automatic HTTP retries.
            with self.opener.open(request, timeout=None) as response:
                raw = response.read()
        except urllib.error.HTTPError as e:
            code = e.code
            e.close()
            hints = {401: "密钥无效，请检查配置。", 402: "账户余额不足。",
                     403: "账户没有调用权限。", 429: "服务当前限制请求，请稍后重新运行。"}
            raise ApiError("API 请求失败（HTTP %d）。%s 已保存的进度可继续使用。" %
                           (code, hints.get(code, "请检查 API 地址、模型名或服务状态。"))) from None
        except (urllib.error.URLError, OSError, ValueError):
            raise ApiError("无法完成 API 连接。请检查网络和 API 地址，然后重新运行。") from None
        try:
            body = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            raise ApiError("API 返回的内容不是有效 JSON，请检查服务。") from None
        if not isinstance(body, dict):
            raise ApiError("API 返回的内容应为 JSON 对象。")
        return body


def _answer(body: Dict):
    try:
        choice = body["choices"][0]
        text = choice["message"]["content"]
        reason = choice["finish_reason"]
    except (KeyError, IndexError, TypeError):
        raise ApiError("API 返回内容缺少 choices/message/content 或 finish_reason。") from None
    if not isinstance(text, str) or not text.strip():
        raise ApiError("模型没有返回可用的文字回答。")
    return text, reason


def _select(pending: Dict[str, List[str]], index: Dict, only: Optional[List[str]]) -> Dict[str, List[str]]:
    if not only:
        return pending
    unknown = set(only) - set(index["packets"]) - set(index["docs"])
    if unknown:
        raise ApiError("未知文档或分包编号：" + ", ".join(sorted(unknown)))
    return {pid: msgs for pid, msgs in pending.items()
            if pid in only or index["packets"][pid]["doc_id"] in only}


def run_api(paths: Paths, config: ApiConfig, only: Optional[List[str]] = None,
            once: bool = False, dry_run: bool = False, rules_format: str = "wrapped",
            client=None, emit: Callable[[str], None] = print) -> int:
    index = load_index(paths)
    prompt = render_prompt(index["as_of"])
    res = run_ingest(paths, persist_ids=not dry_run)
    todo = _select(pending_packets(res), index, only)
    # Read/verify every selected input before the first paid request.
    packets: Dict[str, str] = {}
    for pid in todo:
        f = paths.packets_dir / (pid + ".md")
        if not f.exists():
            raise ApiError("缺少分包 %s，请先运行 prepare。" % pid)
        raw = f.read_bytes()
        if hashlib.sha256(raw).hexdigest() != index["packets"][pid]["sha256"]:
            raise ApiError("分包 %s 与目录记录不一致，请先运行 prepare。" % pid)
        packets[pid] = raw.decode("utf-8")
    emit("模型：%s | 待处理：%d 个分包 | 已完成：%d/%d" %
         (config.model, len(todo), res.counts["packets_done"], res.counts["packets_total"]))
    if dry_run:
        for pid in todo:
            emit("  %s%s" % (pid, "（需修正）" if todo[pid] else ""))
        emit("预览完成，未调用 API。")
        return 0
    if not todo:
        write_outputs(paths, res, rules_format)
        emit("所选范围没有待处理分包。结果：%s" % (paths.out_dir / "rules.json"))
        return 0
    if not config.key:
        raise ApiError("尚未配置 API 密钥。")
    client = client or ChatClient(config)
    archive = paths.work_dir / "api"
    archive.mkdir(parents=True, exist_ok=True)
    paths.inbox_dir.mkdir(parents=True, exist_ok=True)
    while todo:
        for pid, problems in todo.items():
            emit("正在处理 %s%s…" % (pid, "（修正上一份回答）" if problems else ""))
            request_text = render_packet_input(pid, packets[pid], problems)
            body = client.complete(prompt, request_text)
            attempt = "API_%s_%s_%s" % (pid, dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%f"),
                                        uuid.uuid4().hex)
            # Keep full API response, usage and provenance outside the ingest inbox.
            response_file = archive / (attempt + ".json")
            response_file.write_text(json.dumps({"packet_id": pid, "model": config.model,
                "endpoint": config.endpoint, "as_of": index["as_of"],
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "input_sha256": hashlib.sha256(request_text.encode("utf-8")).hexdigest(),
                "response": body}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            text, reason = _answer(body)
            (archive / (attempt + ".txt")).write_text(text, encoding="utf-8")
            if reason != "stop":
                raise ApiError("%s 的回答未正常结束（%s）。原始回答已存入 %s；未作为完成结果导入。" %
                               (pid, reason, response_file))
            objects, parse_problems = extract_json_objects(text)
            if parse_problems:
                raise ApiError("%s 的回答有无法解析或未写完的 JSON，已保留原始回答，未导入。" % pid)
            relevant = [obj for obj in objects if classify(obj) != "other"]
            if not relevant:
                raise ApiError("%s 的回答没有规则或收据，原始内容已保存到 %s。" % (pid, response_file))
            if any(obj.get("packet_id") != pid for obj in relevant):
                raise ApiError("%s 的回答包含其他分包编号，已保留原始回答，未导入。" % pid)
            receipts = [obj for obj in relevant if classify(obj) == "receipt"]
            if len(receipts) > 1 or any(type(obj.get("n_rules")) is not int or obj["n_rules"] < 0
                                        for obj in receipts):
                raise ApiError("%s 的收据重复或条数不是非负整数，已保留原始回答，未导入。" % pid)
            answer_file = paths.inbox_dir / (attempt + ".jsonl")
            answer_file.write_text(text, encoding="utf-8")
            res = run_ingest(paths)
            write_outputs(paths, res, rules_format)
            state = res.states[pid]
            emit("  %s：%s（%s）；回答已保存。" % (pid, state["state"], state["detail"]))
        todo = _select(pending_packets(res), index, only)
        if once:
            break
    emit("已完成：%d/%d | 规则：%d | 所选范围剩余：%d\n结果：%s\n检查报告：%s" %
         (res.counts["packets_done"], res.counts["packets_total"], res.counts["rules"], len(todo),
          paths.out_dir / "rules.json", paths.work_dir / "report.md"))
    return 2 if todo else 0
