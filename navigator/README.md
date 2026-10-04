# Rental Housing Law Navigator

## 三个阶段

| 阶段 | 负责什么 | 入口 |
|---|---|---|
| 第一阶段（Module A） | 从法律原文提取规则 | `python3 run.py ingest`；提取流程见下文 |
| 第二阶段（Module B） | 确定城市、按查询日期判断规则是否覆盖某个地址 | `python3 -m lookup resolve`；`python3 -m lookup lookup --address-id A0001` |
| 第三阶段（Module C） | 比较实际查询结论、判断变更影响和需复核的州/市关系 | `python3 -m changes` |

第二、三阶段按地址覆盖和变更题的需求独立实现，仅用 Python 标准库、不调用模型。已有 Census 缓存后，可离线重新生成全部提交文件：

```bash
cd /Users/herh/MyFiles/Projects/hack-nation/navigator
python3 -m lookup build --offline
python3 -m unittest tests.test_stage23 tests.test_stage23_acceptance -q
```

输入事实、运行方式和目前的规则缺口见 [第二、三阶段说明](docs/STAGE2_3.md)。每个界面和导出结论均带“非法律意见”。

## 第一阶段：规则提取

目标:把"读法律文本 → 结构化规则"拆成 **固定流程 + 一次模型调用**。模型只负责语义判断(这条法规定了什么),
其余全部由确定性脚本完成。现在可直接调用 **DeepSeek Flash API**，也可继续用订阅模型手动跑；两种方式使用同一份提示词和同一套结果检查。

```
corpus ──prepare──▶ packets ──bundle──▶ 粘贴文件 ──(你把它交给模型)──▶ work/out/*.txt ──ingest──▶ outputs/rules.json
 清洗/分块/筛选        每包≤24K字符      提示词+若干分包                    模型回答               校验/对齐引文/推导状态/去重

                         └── api ──▶ DeepSeek Flash ──▶ 保存回答 + 自动检查/修正 ──▶ outputs/rules.json
```

只用 Python 标准库(3.9+)。

## 固定的部分(不用模型)

| 步骤 | 做什么 |
|---|---|
| 清洗 | 删除网页导航垃圾(连续 ≥8 行短句且不含数字的菜单),删除处留 `[[omitted…]]` 占位;不改动任何字符,所以引文仍能对回原文 |
| 分块/筛选 | 按标题和长度切块;只有超大文档(>8 万字符,目前仅 D067)才按相关度丢弃最低分的块,被丢弃的块写进报告 |
| 解析 | 容忍 markdown 围栏、前后废话、缩进 JSON、尾逗号;能检测回答被截断 |
| **引文对齐** | 模型的 `quoted_span` 常有弯引号、换行、省略号差异。脚本在原文里定位,换成**原文自己的字符**(精确 → 省略号 → 模糊≥0.85,找不到就拒收)。直接保证"引文在语料里能找到" |
| 状态推导 | 模型只报事实(`lifecycle` + `effective_date`),`status` 由代码按 as-of 日期算(in_force / not_yet_effective / pending / failed) |
| 事实核对 | 生效日期、`key_value` 里的数字是否真在原文出现;类别是否被原文提到;辖区与文档是否一致。不符合只**警告**,进报告供人工复核 |
| 去重合并 | 同辖区+同类别+同条文编号合并;来源之间生效日期/数值不一致 → 自动 `conflict_flag`(正好能暴露伯克利、洛杉矶 RSO 这类"两个生效日期") |
| ID | `r-0001` 起,按条文固定,重跑不变(`work/id_registry.json`),后面 lookups.json 不会错位 |
| 审计 | 原始回答留在 `work/out/`,每次运行写 `work/audit.json`(输入文件哈希、数量) |

## 直接调用 DeepSeek Flash API

在 `navigator/.env` 中填入 `DEEPSEEK_API_KEY`，默认模型是 `deepseek-flash`。配置文件模板见 `.env.example`；不需要安装额外 Python 库。

```bash
cd /Users/herh/MyFiles/Projects/hack-nation/navigator
cp .env.example .env                 # 仅第一次配置；已有 .env 时不要覆盖
chmod 600 .env
# 编辑 .env，填入自己的密钥
python3 run.py api --dry-run          # 查看还有哪些分包未完成，不调用 API
python3 run.py api                    # 直接处理未完成分包，保存回答、检查并生成结果
```

已有 `work/index.json` 时直接运行即可；全新语料先执行 `python3 run.py prepare`。API 每次处理一个完整分包，不需要 `bundle`，不发送给文件代理的 DELIVERY 指令。

- 跳过已完成的分包，包括订阅模型已经做完的部分；退出后用同一条命令继续。
- 检查未通过的回答会附带问题清单，再交回模型修正，直到所选范围全部完成。没有固定重试次数或应用层时间、回答长度限制；服务本身仍可能限制回答长度。
- 网络/账户错误、异常返回或 API 明示回答未完成时停止，保留此前进度；不会把被截断的回答算作完成。
- 原始回答在 `work/out/API_*.jsonl`；完整 API 返回和用量在 `work/api/`，密钥不写入这些文件。
- `--only D067` 或 `--only D067-01,X001` 选择文档/分包；`--once` 只处理一轮，未通过的留待下次；`--rules-format list` 输出裸数组。
- 配置优先级：命令行参数 > 环境变量 > `.env`。其他兼容 Chat Completions 的服务可配置 `NAV_API_KEY`、`NAV_API_BASE_URL` 和 `NAV_API_MODEL`。

完整操作说明：[RUN_API.md](RUN_API.md)。订阅模型操作仍见下面的流程和 `RUN_EXTRACTION.md`。

## 订阅模型流程

```bash
cd navigator
python3 run.py prepare      # 1. 清洗+分块(只需一次;语料变了再跑)
python3 run.py bundle       # 2. 生成 work/paste/BATCH-*.md (默认约 15 个)
```

3. 打开一个 `BATCH-*.md`,**整份**粘给订阅模型(提示词已在文件开头)。
   把回答原样存到 `work/out/` 下任意文件名,例如 `01.txt`。文件名无所谓,记录里自带 packet_id。
4. 全部做完(或每做几批)运行:

```bash
python3 run.py ingest       # 校验 → outputs/rules.json + work/report.md
python3 run.py status       # 哪些包 done / 还要补
python3 run.py bundle       # 只为"没做完/被拒"的包重新生成粘贴文件,问题清单已写在包前面
```

循环到 `status` 全是 `done`。`work/report.md` 里 **Rules to check by hand** 是需要你人工看一眼的规则。

### 包的状态

| 状态 | 含义 | 处理 |
|---|---|---|
| pending | 还没有回答 | `bundle` 会包含 |
| incomplete | 没有收据行,多半被截断 | 重新粘贴,或调小 `--paste-chars` |
| mismatch | 收据声称的条数与解析出的不符 | 同上 |
| needs_fix | 有记录被拒(引文不在原文、类别写错等) | `bundle` 会把原因写在包前面 |
| done | 完整且无拒收 | |

### 全自动:订阅模型是能读写文件、跑命令的代理(Claude Code / Codex 等)

在 `navigator/` 目录里对它说一句:**"读 RUN_EXTRACTION.md 并按它执行"**。文档里写明了存什么格式、存到哪、
每批做完自己跑 `ingest`、被拒的包自己重做、什么时候停、最后汇报什么。每个 `BATCH-*.md` 里也带有一段
`# DELIVERY`,写着这一批的确切保存路径和要执行的命令,所以单独给它某一个批次文件也能自己完成。
(纯聊天、不能读写文件的模型,仍然是粘贴 + 手动保存。)

## 参数

```bash
python3 run.py prepare --max-chars 24000 --budget 80000   # 分包大小 / 超大文档预算
python3 run.py bundle  --paste-chars 50000                # 一个粘贴文件的容量;模型上下文小就调小,大就调大(如 80000 → 9 个文件)
python3 run.py ingest  --as-of 2026-10-01 --rules-format wrapped   # wrapped={"rules":[...]} (同模板) / list=裸数组 (同 README 文字)
```

## 缺失原文怎么办 / 第 16 小时的新条例

语料清单有 87 份,只有 54 份带原文。`work/COVERAGE_GAPS.md` 列出其余 33 份(包括霍博肯、纽瓦克、洛杉矶市法典等关键条例)。
没有原文就**提不出规则也没有可引用的 quoted_span**。自己打开页面、复制正文(阅读允许,不要批量爬取),存成 txt:

```bash
python3 run.py add-doc --file ordinance.txt --jurisdiction "Cambridge, MA" --url https://...   # 得到 X001
python3 run.py prepare --only X001
python3 run.py api --only X001                          # 用 API 提取新文档并自动检查
# 或使用订阅模型：bundle → 模型保存回答 → ingest
```

## 目录

```
nav/              流水线代码
RUN_EXTRACTION.md 全自动总控文档 (给能读写文件的代理)
RUN_API.md        直接调用 DeepSeek Flash API 的操作说明
.env.example     API 配置模板（复制为 .env 后填写密钥）
prompts/          extract_prompt.md (提取提示词模板), delivery.md (每个批次里的保存/执行说明)
tests/            python3 -m unittest discover -s tests   (含本地 HTTP 请求和完整流程测试)
work/PROMPT.md    渲染好的提示词 (as-of 已填入)
work/packets/     分包 (可再生,不进 git)       work/paste/  粘贴文件 (可再生)
work/out/         模型原始回答 (审计证据,要进 git)
work/api/         API 完整返回、用量、输入哈希（不含密钥）
work/report.md    本次运行报告                  work/rules_enriched.json  含 applicability/penalty/来源/警告,供 Module B 使用
outputs/rules.json  提交用,严格符合 schema
```

## 比赛材料与评分范围（v5）

- 本届不向参赛者提供 `score.py` 或开发集答案。参赛视频应展示本队系统的实际输出和自行验证过程，不展示 `score.py` 的评分结果。
- 引用评分只依据比赛资料包中官方分发且可核验的语料原文。单独保存的链接原文可在遵守来源条款时用于研究；除非组织方正式将其加入并映射到分发语料，否则不计入引用评分。

## 待向组织者确认

1. `rules.json` 格式:模板是 `{"rules":[…]}`,README 文字说是"记录列表"。默认按模板输出,`--rules-format list` 切换。
2. 引文风格(`Cal. Civ. Code § 1947.12` / `G.L. c.186 §15B` …)与答案键的匹配规则未知。本流水线只做保守规范化:统一 `§`、去掉款项括号。
