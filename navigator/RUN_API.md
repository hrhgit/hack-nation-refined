# 直接调用 DeepSeek Flash API

这条流程由 Python 程序直接调用模型完成规则提取，不需要把文档交给订阅模型，也不需要模型读写本地文件。它使用现有原文分包、提取提示词和结果检查，保留订阅模型已经完成的进度。

## 1. 配置密钥

在 `/Users/herh/MyFiles/Projects/hack-nation/navigator/.env` 填写：

```dotenv
DEEPSEEK_API_KEY=你的密钥
NAV_API_MODEL=deepseek-flash
NAV_API_BASE_URL=https://api.deepseek.com
```

模板为 `.env.example`。密钥只放在本地 `.env` 或 `DEEPSEEK_API_KEY` 环境变量中；`.env` 已加入忽略规则。环境变量覆盖文件内的同名设置。使用 `--env-file /绝对路径/config.env` 可选择其他配置文件；文件只支持普通的 `KEY=value` 和整行 `#` 注释，不执行命令或替换变量。

当前默认模型名和请求接口依据 [DeepSeek 官方文档](https://api-docs.deepseek.com/api/create-chat-completion/)：`deepseek-flash`，`POST https://api.deepseek.com/chat/completions`。不需要安装模型 SDK，Python 标准库即可运行。

## 2. 运行

```bash
cd /Users/herh/MyFiles/Projects/hack-nation/navigator
python3 run.py api --dry-run
python3 run.py api
```

`--dry-run` 不需要密钥，不请求模型，也不写结果文件。

项目已经有 `work/index.json` 和原文分包，可以直接运行。若换成全新语料，先运行 `python3 run.py prepare`；原有 prepare 的分包和长文筛选行为保持不变。API 入口本身不再截短输入，也不设置应用层请求超时或回答长度上限。服务端仍有自己的上下文和回答限制。

程序按顺序处理未完成分包，每次发送完整提取提示词和一个完整分包。每次回答后自动执行引文检查、格式检查、生效状态推导和去重，写出 `outputs/rules.json` 与 `work/report.md`。未通过时把具体问题放在该分包前面，再交回模型修正，直到所选范围完成；默认不设置修正次数上限。

按 `Ctrl+C` 可停止；再次执行 `python3 run.py api` 会跳过已完成分包。每份回答使用新的文件名，旧回答不会被覆盖。

## 3. 只处理指定文档或一轮

```bash
python3 run.py api --only D067
python3 run.py api --only D067-01,X001
python3 run.py api --once
python3 run.py api --rules-format list
```

`--only` 可填文档编号或分包编号，逗号分隔，已完成分包仍会跳过。未知编号会在调用前报错。`--once` 对所选未完成分包各调用一次，不循环修正；有分包仍需修正时以退出码 2 结束。默认输出 `{"rules":[...]}`；`--rules-format list` 改成裸数组。

新增原文后：

```bash
python3 run.py add-doc --file ordinance.txt --jurisdiction "Cambridge, MA" --url https://example.org/ordinance
python3 run.py prepare --only X001
python3 run.py api --only X001
```

将 `X001` 替换成 add-doc 实际输出的编号。

## 4. 文件和错误处理

| 文件 | 内容 |
|---|---|
| `work/out/API_*.jsonl` | 进入结果检查的原始模型回答；与订阅模型回答一起处理 |
| `work/api/API_*.json` | 完整 API 返回，包括服务返回的用量；附模型、接口、日期、提示词及输入哈希 |
| `work/api/API_*.txt` | 原始文字，包括未正常结束或未被导入的回答 |
| `outputs/rules.json` | 通过现有检查、合并后的提交结果 |
| `work/report.md` | 引文/字段问题、覆盖情况与待人工复核项 |

网络断开、无效密钥、余额不足、服务繁忙或异常返回会停止流程，保留已完成进度。修复配置或网络后运行同一条命令。程序不自动重试失败的 HTTP 请求，也不改用另一模型。

API 明示 `finish_reason` 为 `length` 或任何非 `stop` 值时，回答只存入 `work/api/`，不会进入提交结果。无法解析的 JSON、其他分包的编号、重复或无效收据也会保留原始回答并停止。正常结束但缺收据、条数不符或引文不正确时，由已有检查反馈并重新提取。

退出码：0 = 所选范围完成或预览完成；1 = 请求/配置/输入异常；2 = `--once` 后仍有未完成分包；130 = 用户中止。

33 份没有原文的文档仍无法提取。API 不会自动找外部网页或补造规则，具体见 `work/COVERAGE_GAPS.md`。检查报告中的人工复核警告仍需查看，`done` 表示通过程序检查。

## 5. 更换兼容服务

可以修改 `.env`，或使用命令行覆盖模型和地址：

```bash
python3 run.py api --model deepseek-flash --base-url https://api.deepseek.com
```

其他兼容 Chat Completions 的服务使用 `NAV_API_KEY`、`NAV_API_MODEL`、`NAV_API_BASE_URL`。`NAV_API_KEY` 优先于 `DEEPSEEK_API_KEY`。地址填写基础地址（可带 `/v1`），程序在末尾追加 `/chat/completions`。远程地址必须用 HTTPS，密钥不会被转发到重定向地址。兼容服务需要返回 `choices[0].message.content` 和 `choices[0].finish_reason`。

## 分步模式（`--agent`）

单次模式把所有规则一次放进提示词。分步模式给模型一份短的核心提示词（`prompts/agent/core.md`）和 5 张参考卡（`prompts/agent/cards/`），模型可以在回答前调用两个工具，多步完成：

- `read_card(name)`：读一张卡，卡里是某一类字段的详细写法（楼龄和户数、房东与例外、日期、与其他层级法律的关系、引用）。
- `check_record(record_json)`：对一条写好的记录运行本流程自己的校验，并显示它的条件会让几栋虚构的楼得到什么结果；模型看到后果不对可以改了再查。

最终回答仍是和单次模式一样的 JSON 行，后面的校验、导入、"被拒收就带原因重写"全都不变。

```bash
python3 run.py api --agent --dry-run          # 看会处理哪些分包，不调用 API
python3 run.py api --agent --workers 3        # 同时处理 3 个分包；导入那一步仍是一次一个
```

要点：
- 没有步数上限（项目规则不让加提前结束的兜底）。每个分包的完整对话存在 `work/api/AGENT_<分包>_*.json`，里面记了步数、读了哪些卡、自检几次、每步用量。
- 某个分包失败（接口错误、回答没写完）只影响它自己，别的照常；最后列出失败的分包并以退出码 1 结束，重新运行会从没完成的开始。
- 卡片是这个模式的"源文件"，要改规则就直接改 `prompts/agent/` 里的文件。`eval/agent_build.py` 只用来第一次从单次提示词拆出这些文件，已存在时拒绝覆盖（要覆盖加 `--force`）。
- 评测用 `python3 eval/agent_run.py`（用的是同一份代码），答案清单评分用 `python3 eval/conditions_check.py`。
