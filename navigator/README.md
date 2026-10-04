# Rental Housing Law Navigator

## 安装与启动

后端已经迁移到 TypeScript：网页服务、原文处理、模型调用、地址判断和变更追踪都直接运行在 Node.js 上。前端、数据格式和已有处理进度继续沿用。

```bash
cd /Users/herh/MyFiles/Projects/hack-nation/navigator
npm ci
npm run build
npm start                         # http://127.0.0.1:8000
```

需要 Node.js 22 或更新版本。`npm test` 运行原生测试，不需要 Python；`npm run verify` 另运行 Python 基准及两个版本的对照测试，需要 Python 3。迁移范围和验证证据见 [迁移核对报告](docs/TYPESCRIPT_MIGRATION.md)。

## 三个阶段

| 阶段 | 负责什么 | 入口 |
|---|---|---|
| 第一阶段（Module A） | 从法律原文提取规则 | `npm run nav -- ingest`；提取流程见下文 |
| 第二阶段（Module B） | 确定城市、按查询日期判断规则是否覆盖某个地址 | `npm run lookup -- resolve`；`npm run lookup -- lookup --address-id A0001` |
| 第三阶段（Module C） | 比较实际查询结论、判断变更影响和需复核的州/市关系 | `npm run changes --` |

第二、三阶段按地址覆盖和变更题的需求独立实现，仅用 Node.js 自带功能、不调用模型。已有 Census 缓存后，可离线重新生成全部提交文件：

```bash
cd /Users/herh/MyFiles/Projects/hack-nation/navigator
npm run lookup -- build --offline
npm run test:parity
```

输入事实、运行方式和目前的规则缺口见 [第二、三阶段说明](docs/STAGE2_3.md)。每个界面和导出结论均带“非法律意见”。

## 网页界面

```bash
cd /Users/herh/MyFiles/Projects/hack-nation/navigator
npm start --            # 打开 http://127.0.0.1:8000 ；换端口用 --port
npm run test:parity
```

由 Node.js 直接运行，不需要模型 SDK。法规查询直接用当前规则和地址事实计算；结果显示后，自动调用已配置的 DeepSeek 模型整理总结。网页不读 `outputs/` 里已生成的文件：每次打开页面都用当前的规则和地址文件现场调用查询程序，所以重新提取规则后刷新页面就是新结果。

自动总结跟随页面语言，逐段显示；每句后的引用小图标可打开对应原文。颜色与符号区分适用、需确认、尚未生效或提案、已排除或被取代；虚线图标表示另行保存的来源。相同依据的总结会复用，切换地址、日期、房屋事实或语言后不会显示旧查询的内容。生成失败时，法规列表继续可用，并可手动重新生成。

总结使用 `.env` 中现有模型配置，密钥只在服务端读取。已完成总结和调用记录保存在本地 `work/summary/`，不纳入 Git；不设置按时间终止、输出长度截断或自动重试。接口与验证说明见 [自动总结说明](docs/AUTO_SUMMARY.md)。

| 页面 | 内容 |
|---|---|
| 地址查询 | 搜索或按州、市浏览地址。地址以蓝色门牌显示，下面是所属州和市、建筑事实；再往下是“截至某天的规则”，按六个类别列出，每条一行：结论、规则名、关键数字、来自哪一级、引用 |
| 法律变更 | 五道变更题：题目要求、受影响和标记复核的地址数、变化前后的结论、按城市统计（零也列出）。地址编号可点，跳到该地址在对应日期的查询 |
| 解析法规正文 | 粘贴正文或上传文本文件，智能体识别地区、状态和日期，再查看地址影响 |
| 全部规则 | 全部提取出的规则，按“州 → 市 → 类别”排列，可按地区、类别、状态筛选 |
| 系统如何工作 | 提取流程五步的实际数字和来源文档清单 |

信息分三层，越往后越细：

1. **一行结论**：扫一眼就能看完。结论不是“适用”时，直接在行内写出原因的开头。
2. **点开这一行**：为什么是这个结论、规则内容、原文引文（黄色高亮）、生效日期、需要人工复核的原因。
3. **右侧抽屉**：逐步的判断过程、引文在原文中的前后文、规则的完整字段、提取记录。建筑记录也在抽屉里。

几处约定：

- 蓝色实心圆是“适用”，空心圆是“尚未生效”，虚线圆是“提案”，琥珀色问号是“不确定”，半圆是“被取代”，划线圆是“未通过”。红字只用于“需要人看一眼”的地方。
- 无衬线字是系统说的话（结论、原因、按钮），衬线字是法律说的话（引用、引文、原文）。
- 查询日期属于“结论”而不是“地址”，所以放在规则列表的标题里；向下滚动时这一栏停在顶部，任何时候都能看到是截至哪一天。
- 规则提取还没跑完时，列出规则的页面会提示“只显示目前已提取出的规则”。
- 记录里缺建成年份或单元数时，可以在“建筑记录”里临时填入再判断；页面会写明这些事实是使用者填的，不写回任何文件。
- 界面和自动总结有英文、西班牙文、中文三种；法规原文及原有逐条判断解释保持原样。
- 每个页面顶部和底部、每个抽屉底部都有“非法律意见”。
- 字体从 Google Fonts 加载；没有网络时自动改用系统字体，功能不受影响。

## 第一阶段：规则提取

### 从网页提交正文

“法律变更”页面的 **解析法规正文** 按钮，以及导航中的同名入口，只要求提交正文：

1. 粘贴完整正文或上传 UTF-8 `.txt` 文件，点击“开始解析”。没有单独提交网址的选项；空正文或只含网址的提交会被拒绝。
2. 现有 DeepSeek 智能体从正文识别法规名称、所属州/市、通过状态、生效日期和规则内容，并检查原文引用。使用者不用先填写规则，也不用选择新增、修改或对应旧法规。
3. 系统自动按地区、类别、条文编号对应已有记录，保留原编号及未出现的其他类别；按正文中的日期判断，更早的查询保留旧版。正文缺少准确变更日期时，更早历史状态标记为不确定。
4. 查看智能体识别的规则及样本地址范围；相关法规同时按官方五道变更题的日期和形式计算。原文引用、已有记录的变化放在展开项中。核对后点击“使用解析结果”。

官方 [变更示例](../starter-pack/participant-final-no-hour16%203/dev/change_tests.json) 关注的是生效日期前后、城市边界、已通过但尚未生效、尚未通过的提案及公投失败。这些判断由提取后的规则和地址查询共同完成：未来生效的法规显示未来范围，提案显示“如果通过”的范围，失败提案的受影响列表为空。提交前后记录的修正另放在展开项，避免把记录变化误当成已经生效的影响。

任务保存在服务端，离开或刷新页面不取消任务；模型调用失败时可以继续已保存的进度。

需要服务端已经配置 `.env` 中的提取模型；密钥不发送到网页。正文按现有分段方式完整处理，不使用总字符预算删除低相关段落。

每次提交、原文、模型返回和版本记录独立保存在本地 `work/law_imports/`，不纳入 Git。应用后网页查询、规则列表和按日期的变更判断使用这些版本；原有命令行提取进度和比赛提交文件继续保留。用户提交的原文显示为额外来源，不自动纳入官方引用评分范围。

目标:把"读法律文本 → 结构化规则"拆成 **固定流程 + 一次模型调用**。模型只负责语义判断(这条法规定了什么),
其余全部由确定性脚本完成。现在可直接调用 **DeepSeek Flash API**，也可继续用订阅模型手动跑；两种方式使用同一份提示词和同一套结果检查。

```
corpus ──prepare──▶ packets ──bundle──▶ 粘贴文件 ──(你把它交给模型)──▶ work/out/*.txt ──ingest──▶ outputs/rules.json
 清洗/分块/筛选        每包≤24K字符      提示词+若干分包                    模型回答               校验/对齐引文/推导状态/去重

                         └── api ──▶ DeepSeek Flash ──▶ 保存回答 + 自动检查/修正 ──▶ outputs/rules.json
```

后端使用 TypeScript，由 Node.js（22 或更新版本）直接运行；运行时没有额外依赖。

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

在 `navigator/.env` 中填入 `DEEPSEEK_API_KEY`，默认模型是 `deepseek-flash`。配置文件模板见 `.env.example`；不需要安装模型 SDK。

```bash
cd /Users/herh/MyFiles/Projects/hack-nation/navigator
cp .env.example .env                 # 仅第一次配置；已有 .env 时不要覆盖
chmod 600 .env
# 编辑 .env，填入自己的密钥
npm run nav -- api --dry-run          # 查看还有哪些分包未完成，不调用 API
npm run nav -- api                    # 直接处理未完成分包，保存回答、检查并生成结果
```

已有 `work/index.json` 时直接运行即可；全新语料先执行 `npm run nav -- prepare`。API 每次处理一个完整分包，不需要 `bundle`，不发送给文件代理的 DELIVERY 指令。

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
npm run nav -- prepare      # 1. 清洗+分块(只需一次;语料变了再跑)
npm run nav -- bundle       # 2. 生成 work/paste/BATCH-*.md (默认约 15 个)
```

3. 打开一个 `BATCH-*.md`,**整份**粘给订阅模型(提示词已在文件开头)。
   把回答原样存到 `work/out/` 下任意文件名,例如 `01.txt`。文件名无所谓,记录里自带 packet_id。
4. 全部做完(或每做几批)运行:

```bash
npm run nav -- ingest       # 校验 → outputs/rules.json + work/report.md
npm run nav -- status       # 哪些包 done / 还要补
npm run nav -- bundle       # 只为"没做完/被拒"的包重新生成粘贴文件,问题清单已写在包前面
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
npm run nav -- prepare --max-chars 24000 --budget 80000   # 分包大小 / 超大文档预算
npm run nav -- bundle  --paste-chars 50000                # 一个粘贴文件的容量;模型上下文小就调小,大就调大(如 80000 → 9 个文件)
npm run nav -- ingest  --as-of 2026-10-01 --rules-format wrapped   # wrapped={"rules":[...]} (同模板) / list=裸数组 (同 README 文字)
```

## 缺失原文怎么办 / 第 16 小时的新条例

语料清单有 87 份,只有 54 份带原文。`work/COVERAGE_GAPS.md` 列出其余 33 份(包括霍博肯、纽瓦克、洛杉矶市法典等关键条例)。
没有原文就**提不出规则也没有可引用的 quoted_span**。自己打开页面、复制正文(阅读允许,不要批量爬取),存成 txt:

```bash
npm run nav -- add-doc --file ordinance.txt --jurisdiction "Cambridge, MA" --url https://...   # 得到 X001
npm run nav -- prepare --only X001
npm run nav -- api --only X001                          # 用 API 提取新文档并自动检查
# 或使用订阅模型：bundle → 模型保存回答 → ingest
```

## 目录

```
src/nav/          TypeScript 提取流程
src/lookup/       TypeScript 地址解析和规则判断
src/changes/      TypeScript 变更追踪
src/web/          TypeScript 网页服务
nav/ lookup/ changes/ web/*.py  Python 对照实现，保留给测试和离线研究脚本
RUN_EXTRACTION.md 全自动总控文档 (给能读写文件的代理)
RUN_API.md        直接调用 DeepSeek Flash API 的操作说明
.env.example     API 配置模板（复制为 .env 后填写密钥）
prompts/          extract_prompt.md (提取提示词模板), delivery.typescript.md (当前批次的保存/执行说明)
tests/            npm run verify   (含本地 HTTP 请求和完整流程测试)
work/PROMPT.md    渲染好的提示词 (as-of 已填入)
work/packets/     分包 (可再生,不进 git)       work/paste/  粘贴文件 (可再生)
work/out/         模型原始回答 (只保留在本地，不进 git)
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
