# 缺失的法律条文清单（交给负责"找原文"的 AI）

## 任务

初始语料清单有 87 份文件、54 份带正文；这是补充前的历史状态。下方优先级列表保留原任务范围，是否仍缺失请以“当前核对状态”和结果登记表为准。
请逐条找到**官方来源**的原文，存成纯文本，再用下面的命令加入语料。

## 当前核对状态（2026-10-03，America/Los_Angeles）

- 合并原清单与补充清单后，共 **97 个不同编号，82 个有文本，15 个仍无文本**。补充清单有 28 行，其中 18 行替换原编号、10 行为新编号；不能把 87 与 28 直接相加。82 包含案件摘录和状态页，不代表 82 份完整法规。
- 前一轮对照优先级清单、结果表、实际文件与 `work/index.json`，当时 81 个文本的文件哈希均与索引一致；历史快照见 `docs/evidence/document-audit/corpus-snapshot.json`。本次新增 X102，现有 82 个文本均有实际文件；本次没有重新生成索引或提取规则，不能沿用旧快照声称新增文件已完成处理。
- **原文取得、登记入库、规则提取、适用判断是不同状态。** 本文登记的是前两项；不能据此声称覆盖表已经补满。本轮不修改规则输出，也不替其他工作重新运行提取。
- 麻州 IP 25-21：裁判结果已确认，案件记录摘录已入库 **X101**；27 页法院判决全文已取得（美国商会托管副本，案号、日期与结果经官方记录核对），可阅读和引用；仅未取得法院官网同一文件的下载件，不再列为全文缺失。洛杉矶：现有 **D038、D044、X008**，覆盖收入来源、押金利息和身份信息询问；统一筛查/犯罪记录提案的已颁布后续条例仍未找到。
- 五份新泽西条例现已补齐通过、批准和刊登日期，按通常 20 日规则推算的生效日已登记于文末。日期属于有来源的推算，尚非官方直接写明的生效日，未取得排除紧急决议或公投暂停的逐项证明。其余待完善项为适用范围/例外、原件文字识别和修订删除线核对。

## 规则

1. **只读官方来源**：市政府网站、市法典发布站（ecode360、American Legal、Municode、市政府自己的 PDF）、州议会网站、州法院网站。
   **不要用**新闻、律所文章、行业协会评论替代条文。依用户本轮指示，允许保存和引用法院判决的第三方托管全文副本，但须标明下载来源、核对范围，不冒称法院官网下载件；政府刊登的法定公告可使用报纸公告档案，与新闻报道区别登记。
2. 一次读一页，不要批量抓取。加州议会网站 (leginfo) 会挡脚本，用浏览器读。
3. **原样保存**，不要改写、不要总结、不要翻译。后面的程序会逐字核对引文，改一个字就对不上。
4. 文件开头写两行：`SOURCE: <网址>` 和 `RETRIEVED: <日期时间 UTC>`（与语料读取程序一致；`add-doc` 会自动生成这两行，输入文件只传正文，避免重复）。
5. 找不到或被挡住，就在本文件末尾的"结果登记表"里写明"没取到 + 原因"。**不要用二手解读顶替，也不要凭记忆写条文。** 规则 1 所述原始文件副本应准确标明出处。
6. 一条法规一个文件。一个网页里有多节，就整页保存。

加入语料的命令（在 `navigator/` 目录下）：

```bash
python3 run.py add-doc --file page.txt --jurisdiction "Hoboken, NJ" --url <网址>
```

如果这份文件在语料清单里本来就有编号（下面括号里的 D0xx），加上 `--doc-id D034` 这样的参数沿用原编号。

`--jurisdiction` 的写法必须是这几种之一：
`CA`、`NJ`、`MA`、`Los Angeles, CA`、`San Francisco, CA`、`San Diego, CA`、`Berkeley, CA`、`Santa Ana, CA`、
`Jersey City, NJ`、`Hoboken, NJ`、`Newark, NJ`、`Boston, MA`、`Cambridge, MA`。

## 初始规则覆盖快照（历史记录，不代表当前原文或规则覆盖）

| 地区 | 算法定租 | 申请/筛查费 | 正当理由驱逐 | 涨租上限 | 筛查限制 | 押金 | 样本地址数 |
|---|---|---|---|---|---|---|---|
| CA（州） | 1 | 1 | 4 | 2 | 4 | 6 | — |
| Los Angeles | 1（只是动议） | . | 9 | 5 | . | . | 80 |
| San Francisco | 1 | . | 4 | 3 | 1 | 1 | 80 |
| San Diego | 1（草案，误标为待定） | . | 3 | . | 1 | . | 50 |
| Berkeley | 1 | 2 | 6 | 4 | 1 | 2 | 40 |
| Santa Ana | **.** | . | 2 | 3 | . | . | 0 |
| NJ（州） | 2 | 2 | 6 | 4 | 5 | 7 | — |
| Jersey City | **.** | . | . | 1 | . | . | 50 |
| **Hoboken** | **.** | **.** | **.** | **.** | **.** | **.** | 40 |
| **Newark** | **.** | **.** | **.** | **.** | **.** | **.** | 50 |
| MA（州） | 2（待定法案） | 2 | 5 | 2 | 1 | 1 | — |
| Boston | . | . | 1 | . | 3 | . | 60 |
| Cambridge | . | . | . | . | 1 | . | 50 |

说明：本表是补充前的快照，尚未按当前输出重算，不能用它判断原文仍缺失。不是每个空格都该有规则（比如麻州的城市本来就没有涨租上限）。下面只列确实缺的。

---

## 第一优先：缺了就有测试题答不出

### P1-1 Hoboken 算法定租禁令（测试题 T2、T3 直接要用）
- 需要：Hoboken 市法典里禁止用算法软件定租金的那一节，全文，含生效日期和处罚。
- 语料给的地址：`https://ecode360.com/46833413`（D034，官方法典发布站，可读）。
- 要确认：章节号、通过日期、生效日期。

### P1-2 Jersey City 算法定租禁令（T2、T3）
- 需要：Jersey City 禁止算法定租的条例全文。
- 语料里只有新闻（D035）和律所文章（D037），**都不能用**。
- 去哪找：Jersey City 市法典（Municode 上的 Jersey City Code of Ordinances），或市议会网站上的条例 PDF。
- 要确认：条例编号、法典节号（现已核实为 §218-12，见 D035、D037）、通过和生效日期。

### P1-3 麻州租金管制公投 IP 25-21 被判无效（T5）
- 已取得官方案件记录：SJC-13893 的 2026-06-23 第 #43 条明确禁止将 IP 25-21 放上 2026 年全州选票；裁判日期和结果已核实。法院判决全文也已取得，可引用第三方托管副本；仅下载渠道不同，不再列为全文缺失。核对范围见文末“进一步找原文”。
- 语料里只有 WBUR 新闻（D059），不能用。
- 去哪找：麻州最高法院（SJC）的判决书（mass.gov 或 SJC 判决发布页，案名可能与 *Cella v. Attorney General* 有关，**以实际查到的为准**）；或州务卿 / 总检察长网站上的公投提案状态页。
- 用途：为 IP 25-21 这一提案登记失败状态；**不能由单个提案失败推断 Boston、Cambridge 不存在任何其他租金限制**。其他州法、项目限租等仍须分别判断。

### P1-4 加州 AB 325 / SB 763 的生效日期（T1）
- 当前：已补齐 X003–X006，登记结论见结果表。
- 初始缺口：已有 AB 325 正文（D022），但正文里没写生效日期，所以这条规则的日期是空的，T1 没法判"之前/之后"。
- 需要：
  - 加州议会网站上 AB 325 的法案状态页（写明哪天签署、哪一章 chaptered）；
  - SB 763 的正文和状态页（语料里完全没有）；
  - 加州宪法第 IV 条第 8(c) 款原文（常规会期通过的法律次年 1 月 1 日生效）——这是推出 2026-01-01 的依据。
- 网址都在 `leginfo.legislature.ca.gov`，需用浏览器读。

### P1-5 San Diego 算法定租条例的**正式通过版**
- 当前：正式法典已补为 D074，2025-06-21 生效。
- 初始缺口：手里只有一份日期留空的草案（D076），所以被标成了"待定"。题目说明里说它 2025 年 6 月已通过。50 个地址受影响。
- 需要：San Diego 市法典 §98.1101–§98.11xx（第 9 章第 8 条第 11 分部）正式文本，含通过日期和生效日期。
- 去哪找：市政府自己的法典 PDF（`docs.sandiego.gov/municode/`），或市书记官网站上的条例原件。语料里给的 gocodebook 链接（D074）是第三方站，优先用市政府的。

---

## 第二优先：缺了会漏报规则（漏报一条扣双倍分）

### P2-1 Hoboken 其余法规（40 个地址，现在一条市级规则都没有）
- `https://ecode360.com/15252438`（D032）和 `https://ecode360.com/15252470`（D033）。
- 已核实为 Chapter 155（D032）与 Article II（D033）。D033 与 D032 有内容重叠，不应重复计算同一条规则。
- 特别留意：按建成年份或单元数划分的适用范围、新建筑豁免年限——第二阶段判断"适不适用"全靠这些。

### P2-2 Newark 法规（50 个地址，现在一条市级规则都没有）
- `https://ecode360.com/36623772`（D070）、`https://ecode360.com/36637822`（D071）、`https://ecode360.com/36642000`（D072）。
- 已核实 D070 为 Chapter 19:2（租金控制）、D071 为 Chapter 2:10（部门组织等行政内容）、D072 为 Chapter 2:31（住房与许可两类犯罪记录规定）。不可把三份全部当作租金控制条例。
- 另外请确认：Newark **有没有**算法定租禁令。T2 的预期答案是"Newark 两条都不适用"，只可登记具体检索范围内“未见”；不得把搜索未命中当作证明不存在。州级 D069 的时间适用须另行判断。

### P2-3 新泽西州法（引用格式要和答案对上）
题目说明点名了这些节号，现在我们的规则多数来自一本州政府手册，引用的节号不准。请取州议会网站（`njleg.gov` 的法规库）上的原文：
- N.J.S.A. **46:8-21.2**（押金不超过一个半月租金）
- N.J.S.A. **46:8-26**（押金法的适用范围；房东自住且不超过两个出租单元的条件在这里；租客提前 30 日书面通知援引本法时，该豁免不成立）
- N.J.S.A. **2A:18-61.1**（正当理由驱逐）
- N.J.S.A. **10:5-12**（反歧视法，含收入来源）
语料里给的是 Justia 转载（D061–D064），不要用。

### P2-4 Los Angeles
- `https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-322208`（D038，官方法典发布站）。读了以后登记是哪一节。
- 押金利息要求：洛杉矶市法典 §151.06.02，节号已核实；D044 已替换为官方原文，须补记 RSO 适用范围，见文末。
- 押金、收入来源及身份信息询问的官方材料现已取得（D044、D038、X008）；规则输出是否已覆盖须另查。

### P2-5 San Diego 其他
- 收入来源歧视禁令：市法典第 9 章第 8 条第 8 分部（D075 给的是第三方站，请用市政府 PDF）。
- 租户保护条例（Tenant Protection Ordinance）：**已具备官方原文 D073**，无需用介绍页 D077 替代。市政府法典为 §§98.0701–98.0710，19 页（3-2024 版）；2026-10-03 太平洋时间重新打开官方 PDF 核实。原条例 2023-06-24 生效，2024 年修订的法典历史注记写明 2024-03-28 生效。

### P2-6 Santa Ana 算法定租禁令
- D086 现已替换为官方条例 NS-3090，编号及正文已核实；D087 仍是未抓取的新闻链接，无需重复补新闻。
- 没有 Santa Ana 的样本地址，只算提取分，排在最后。

### P2-7 Jersey City 其余
- 已确认第 260 章，取得 X002 及修订条例 X001；仍需将具体豁免及新旧条文衔接登记完整，不能只记“已有全文”。

### P2-8 麻州 803 CMR 5.00（犯罪记录用于住房筛查）
- `https://www.mass.gov/doc/803-cmr-5-criminal-offender-record-information-cori-housing/download`（D056，官方；现已取得 5.01–5.19 全文，见结果表）。

---

## 第三优先：有官方副本就补，没有就算了

- 加州法典：民法典 §1946.2、§1947.12、§1950.5、§1950.6，政府法典 §12955。语料里部分已有官方副本（例如 §1947.12 是 D024）。请先在 `navigator/work/index.json` 里查有没有，**没有的才补**。
- Cambridge（D030，新闻）、Berkeley（D002，律所文章）：先不管。

核对结果（2026-10-04）：上述五条均已有官方全文，分别为 D023、D024、D025、D026、D027，因此未重复加入。

---

## 每份文件要顺手登记的事实

读原文时请把下面几项抄在登记表里（抄原文的话，注明在哪一节）。这些是后两个阶段的硬需求：

| 要登记的事实 | 为什么要 |
|---|---|
| 通过日期、生效日期 | 判断"已生效 / 尚未生效" |
| 适用于哪些建筑（建成或取得入住证的截止日期、单元数门槛） | 判断某个地址适不适用 |
| 豁免（新建筑几年内豁免、房东自住、政府补贴住房等） | 同上 |
| 是否依赖房东身份（个人 / 公司、名下房产数量） | 数据里没有房东信息，这类一律答"不确定" |
| 是否写明与州法或其他条例的关系（谁优先） | 判断"被更严的规则取代"和冲突标记 |

## 结果登记表（请填）

| 编号 | 取到了吗 | 实际网址 | 实际章节号 | 生效日期 | 备注（没取到的原因） |
|---|---|---|---|---|---|
| P1-1 | 是（D034）；另补通过记录 | [Hoboken 市法典](https://ecode360.com/46833413)<br>[官方通过记录](http://hobokennj.iqm2.com/Citizens/Detail_LegiFile.aspx?ID=12291) | Chapter 158, Article II, §158-2 | **2025-07-29（通常规则推算）**；7 月 9 日最终通过及市长批准，7 月 13 日刊登 | 已补公告档案和原始生效条款；推算条件见文末日期表。 |
| P1-2 | 是（D035、D037、X102） | [Ord. 25-057](https://mcclibraryfunctions.azurewebsites.us/api/ordinanceDownload/16093/1418853/pdf?forceDownload=true)<br>[Ord. 25-076](https://mcclibraryfunctions.azurewebsites.us/api/ordinanceDownload/16093/1418863/pdf?forceDownload=true) | Jersey City Code §218-12 | **25-057：2025-06-11；25-076：2025-08-06；25-098：2025-10-15（均按通常规则推算）**；通过、批准、刊登记录及推算条件见文末 | 25-057 新增该节，25-076 修订；另补 25-098（X102）新增的涨租披露义务，详见文末。 |
| P1-3 | 已确认官方裁判记录（X101 为摘录）；另存完整判决的第三方托管副本 | [SJC-13893](https://www.ma-appellatecourts.org/docket/SJC-13893) | 案件记录 #43；497 Mass. 706 | 裁判日期 2026-06-23；裁判通知下发 2026-07-21 | 用户完成人机验证后已实读：IP 25-21 contains excluded matters in violation of art. 48，禁止州务卿将其放上 2026 年全州选票。第 #43 条没有附件链接；完整判决副本另从美国商会取得，不能声称来自法院下载。此前 X007 仅提供选票缺席证据，现由法院记录直接确认。 |
| P1-4 | 是（D022、X003–X006） | [AB 325 状态](https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202520260AB325)<br>[SB 763 正文](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260SB763)<br>[SB 763 状态](https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202520260SB763)<br>[加州宪法第 IV 条](https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=CONS&division=&title=&part=&chapter=&article=IV) | AB 325；SB 763；California Constitution, art. IV, §8(c) | 2026-01-01 | 两案均显示 2025-10-06 chaptered，且均为非紧急、非税收法案；宪法第 IV 条第 8(c) 款给出下一年 1 月 1 日的依据。 |
| P1-5 | 是（D074） | [San Diego 市法典 PDF](https://docs.sandiego.gov/municode/MuniCodeChapter09/Ch09Art08Division11.pdf) | San Diego Municipal Code §§98.1101–98.1104 | 2025-06-21 | Ord. O-21955 N.S.，2025-05-22 加入法典。 |
| P2-1 | 是（D032、D033） | [Chapter 155](https://ecode360.com/15252438)<br>[Article II](https://ecode360.com/15252470) | Hoboken Code Chapter 155（Rent Control）及 Article II | 各节的历史注记见原文；未把通过日期当作生效日期 | 已保存完整章节，含适用范围、豁免和涨租规则。 |
| P2-2 | 是（D070–D072） | [Chapter 19:2](https://ecode360.com/36623772)<br>[Chapter 2:10](https://ecode360.com/36637822)<br>[Chapter 2:31](https://ecode360.com/36642000) | Newark Code ch. 19:2、ch. 2:10、ch. 2:31 | 以各节法典历史注记为准 | 本次查看的公开市法典页面未见算法定租禁令，不是全库无此法的证明。D072 的 Article 1 是住房犯罪记录筛查，Article 2 是许可事项，不可整章都归为住房。 |
| P2-3 | 是（D061–D064） | [46:8-21.2](https://lis.njleg.state.nj.us/nxt/gateway.dll/statutes/1/44283/44474)<br>[46:8-26](https://lis.njleg.state.nj.us/nxt/gateway.dll/statutes/1/44283/44482)<br>[2A:18-61.1](https://lis.njleg.state.nj.us/nxt/gateway.dll/statutes/1/112/670)<br>[10:5-12](https://lis.njleg.state.nj.us/nxt/gateway.dll/statutes/1/7555/7610) | N.J.S.A. 46:8-21.2、46:8-26、2A:18-61.1、10:5-12 | 现行编纂文本 | 均已用新泽西州议会法规库原文替换转载来源。 |
| P2-4 | 已取得部分相关法规（D038、D044、X008）；统一筛查提案后续未证实 | [LAMC Article 5.6.1](https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-322208)<br>[LAMC §151.06.02](https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-195527) | LAMC §§45.65–45.69；§151.06.02；§§45.40–45.45 | 收入来源章 2020-01-01（§45.69）；身份信息章 2018-11-25；押金利息含多次修订，详见文末 | 已取到 Article 5.6.1、押金利息及 Ord. 185797 原件（新增 Article 5.4，§§45.40–45.45，2018-11-25 生效，见下方更新）。此前“未找到已正式通过的租客筛查限制”过于笼统，已更正：确有移民/公民身份询问限制；22-0279 等统一筛查及犯罪记录提案仍未找到已颁布的后续条例。 |
| P2-5 | 是（D073–D075） | [Tenant Protection Ordinance](https://docs.sandiego.gov/municode/municodechapter09/ch09art08division07.pdf)<br>[收入来源](https://docs.sandiego.gov/municode/MuniCodeChapter09/Ch09Art08Division08.pdf)<br>[算法定租](https://docs.sandiego.gov/municode/MuniCodeChapter09/Ch09Art08Division11.pdf) | San Diego Municipal Code §§98.0701–98.0710；§§98.0801–98.0806；§§98.1101–98.1104 | 租户保护原条例 2023-06-24，2024 修订 2024-03-28；收入来源 2018-10-18；算法定租 2025-06-21 | D073 已有官方原文；D074、D075 已换成市政府 PDF。 |
| P2-6 | 是（D086） | [Santa Ana Ord. NS-3090](https://publicdocs.santa-ana.org/WebLink/DocView.aspx?id=549791&dbid=1&repo=Clerk) | Santa Ana Municipal Code Article XXIV, §§8-3700–8-3703 | 2026-04-02 | NS-3090 于 2026-03-03 通过；第 6 节规定通过后 30 日生效。 |
| P2-7 | 是（X001、X002） | [Jersey City Code Chapter 260](https://library.municode.com/nj/jersey_city/codes/code_of_ordinances?nodeId=CH260RECO)<br>[Ord. 25-099](https://mcclibraryfunctions.azurewebsites.us/api/ordinanceDownload/16093/1418888/pdf?forceDownload=true) | Jersey City Code Chapter 260, §§260-1–260-21 | 25-099：**2025-10-15（通常规则推算）**；9 月 25 日市长批准，10 月 3 日刊登；不代表整个 Chapter 260 同日首次生效 | X002 含 §§260-1–260-20；X001 新增 §260-21 并修订 §260-6。 |
| P2-8 | 是（D056） | [803 CMR 5.00](https://www.mass.gov/doc/803-cmr-5-criminal-offender-record-information-cori-housing/download) | 803 CMR 5.00 | 2021-06-11（本版本；公报累计表） | 已保存住房犯罪记录规定原文；另补 Massachusetts Register 1448 的日期证据，见文末。 |


## 两份文件的进一步核查（2026-10-03，America/Los_Angeles）

### San Diego：已找到，不属于缺失

- [市政府法典全文，19 页](https://docs.sandiego.gov/municode/municodechapter09/ch09art08division07.pdf) 当前可打开，标题为 Residential Tenant Protections，涵盖 §§98.0701–98.0710。
- 项目已有 `starter-pack/participant-final-no-hour16 3/corpus/text/D073.txt`，包含全部十个节标题及最后一节正文。`navigator/work/index.json` 已将 D073 标为 official、no_text=false，14 个文本块全部保留，分为 D073-01 和 D073-02。这是“原文已经存在”的证据，不代表全部规则已被提取。
- 法典历史注记：O-21647 于 2023-05-25 加入，2023-06-24 生效；O-21769 的相关修订及新增 §98.0710 于 2024-02-27 加入，2024-03-28 生效。应以对应条文的历史注记为准，勿把州法 SB 567 的 2024-04-01 日期套用于本市条例。
- 前面的 P2-5 原先只提 D077，遗漏已有 D073，现已纠正；无需重复导入。

### 麻州 IP 25-21：早期检索过程（裁判结果以其后的已验证更新为准）

本次检查的入口及证据边界：

1. [法院案件征求意见公告](https://www.mass.gov/info-details/amicus-announcements-from-september-2025-to-august-2026) 可定位案号 **SJC-13893**，案名 **Arcangelo Cella & others v. Andrea Joy Campbell ... & another**，争议明确涉及 IP 25-21 的认证及摘要。[Reservation and Report](https://www.mass.gov/doc/arcangelo-cella-et-al-v-andrea-joy-campbell-attorney-general-et-al-sjc-13893-0/download) 的搜索索引显示原审号 **SJ-2026-0063**，正文明确为不作决定而提交全院审理；它不是最终判决。直接下载在本次网页工具中返回 403，不能据此断定文件不存在。
2. [法院发布规范 §5.02(1)(a)](https://www.mass.gov/doc/sjc-style-manual/download) 说明新发布判决在两周后移出发布页。[官方旧判决入口](https://www.mass.gov/lists/unofficial-collections-of-published-opinions) 则明确列出非官方判决库。这解释了为何只盯着旧 mass.gov 下载链接可能失败；它并不单独证明本案链接失效的具体原因。
3. [官方案件记录 SJC-13893](https://www.ma-appellatecourts.org/docket/SJC-13893)：本次已用普通浏览器直接访问，仍显示安全验证，未进入案件记录，也未取得判决附件。可以由用户在浏览器完成验证后，再查看与判决、命令或最终裁判有关的条目；是否有可下载附件仍待核实。
4. [总检察长提案页](https://www.mass.gov/info-details/ballot-initiatives-submitted-for-the-2026-biennial-statewide-election-proposed-laws-and-2028-biennial-statewide-election-proposed-constitutional-amendments)：浏览器实读 IP 25-21 下仍是 `Certified: Yes`，并列提案及摘要。这反映认证阶段，不能证明法院最终决定。
5. [州务卿最终选票页](https://www.sec.state.ma.us/divisions/elections/research-and-statistics/2026-ballot-questions.htm) 已保存为 X007。本次页面仍可打开；它支持最终选票不含该提案，不能单凭缺席确认法院判决日期或理由，更不能由单个提案失败推断所有租金限制均不存在。

不依赖下载链接的官方获取办法：

- 向 **SJC Clerk for the Commonwealth（最高法院书记处）** 提供案号 SJC-13893，索取最终判决、裁判命令及案件记录；[官方联系方式](https://www.mass.gov/info-details/supreme-judicial-court-contact-information) 本次浏览器核实电话 **617-557-1020**。
- 向 **Office of the Reporter of Decisions（判决出版办公室）** 询问已移除发布页的判决副本；[官方入口](https://www.mass.gov/orgs/office-of-the-reporter-of-decisions) 列有 **SJCReporter@sjc.state.ma.us**、**617-557-1030**。
- 可直接使用的索取文字：`Please provide an electronic copy of the final opinion, any dispositive order or judgment, and the docket sheet in SJC-13893, Arcangelo Cella & others v. Andrea Joy Campbell & another, concerning Initiative Petition No. 25-21 (county court case SJ-2026-0063). Please also confirm the decision date. The former Mass.gov opinion download is unavailable.`
- 本次没有代用户发送邮件或提交请求。是否提供副本、是否收费及交付时间均未获办公室确认。

**当前结论：San Diego 已有官方原文；麻州已另找到完整判决的第三方托管副本，法院下载件仍待取得；2026-06-23 裁判日期和第 #43 条概括的裁判结果已通过官方案件记录确认，见下方更新。上面的验证阻挡与索取渠道仅保留为早期过程记录；不再把已确认的日期标为未核实，也不执行资料申请。**

### 后续更新：用户完成验证，官方裁判结果已确认

此前“安全验证阻挡、日期和结果未确认”的说明记录的是验证前状态，现由以下实读结果更新：

- 官方页面：<https://www.ma-appellatecourts.org/docket/SJC-13893>。
- 案名：ARCANGELO CELLA & others vs. ATTORNEY GENERAL & another；案号 SJC-13893；判例引用 497 Mass. 706。
- 页面案头列出 Decision Date 06/23/2026，Case Status 为 Decided, Rescript issued；2026-07-21 是裁判通知下发日期，不应混作判决日期。
- 2026-06-23 第 #43 条原文：

> RESCRIPT (Full Opinion): The matter is remanded to the county court, where a judgment shall enter declaring that Initiative Petition 25-21 contains excluded matters in violation of art. 48, and enjoining the Secretary of the Commonwealth from taking steps to place the measure on the ballot for the 2026 Statewide election. (By the Court)

这条官方记录已足以确认本提案被阻止上选票，原因在记录中概括为包含第 48 条排除的事项。详细推理不能仅凭本条补写；现已另存完整判决副本，来源和语料边界见文末。本页第 #43 条没有附件链接，DOCUMENTS 区列的是诉讼书面意见，未发现完整判决下载链接。

官方记录摘录保存在 `navigator/docs/evidence/SJC-13893-docket-excerpt.txt`，现亦已登记为 `corpus_extra/text/X101.txt` 并进入索引；它是第 #43 条摘录，不是全页或完整判决。摘录内的 “Full Opinion” 是法院记录的标签，不能据此把 X101 归为全文判决。本轮复核不修改规则输出。


## 洛杉矶筛查提案：补充官方状态材料（2026-10-03，America/Los_Angeles）

本次补齐的是提案原件和处理记录；复查仍未找到对应的已生效市级条例。不能仅根据标题里有 Ordinance 或记录里有 adopted 就把它当作已通过法律，也不能据此宣称洛杉矶完全没有任何筛查限制。

| 事项 | 官方记录确认的事实 | 使用边界 |
|---|---|---|
| CF 22-0279：Rental Transparency and Accountability / Uniform Screening Criteria | 2022-03-09 动议转交住房委员会；2024-03-09 明确记录 File expired per Council policy。当前记录没有条例通过、公布或生效条目，投票区写 No votes were found。 | 标为已过期提案，不生成有效的市级筛查义务。 |
| CF 22-0280：Fair Chance Housing / Applicant Criminal History | 曾于 2024-03-09 过期；2024-04-09 通过的事项是 reactivating and restoring，即恢复该议题的讨论状态。记录最新行动是 2024-04-12，Expiration Date 字段为 2026-04-09。 | 不把 2024 年 adopted 当作实体条例已通过；也不只依据到期字段推断存在一次未列出的过期处分。尚未找到后续正式条例。 |

官方来源及本地副本：

- [22-0279 状态页](https://cityclerk.lacity.org/lacityclerkconnect/index.cfm?cfnumber=22-0279&fa=ccfi.viewrecord)：`docs/evidence/los-angeles-screening/CF-22-0279-status.html` 与同名 `.txt`。
- [22-0279 动议原件，两页](https://cityclerk.lacity.org/onlinedocs/2022/22-0279_mot_3-09-22.pdf)：`docs/evidence/los-angeles-screening/CF-22-0279-motion.pdf`。文件请求起草条例，列出拟议要求，不是已经颁布的条文。
- [22-0280 状态页](https://cityclerk.lacity.org/lacityclerkconnect/index.cfm?cfnumber=22-0280&fa=ccfi.viewrecord)：`docs/evidence/los-angeles-screening/CF-22-0280-status.html` 与同名 `.txt`。
- [22-0280 官方表决结果，一页](https://cityclerk.lacity.org/onlinedocs/2022/22-0280_CA.pdf)：`docs/evidence/los-angeles-screening/CF-22-0280-action-2024-04-09.pdf`。表决事项明确限于恢复提案状态。
- `docs/evidence/los-angeles-screening/sources.json` 保存各原件网址、实际取得时间和 SHA-256；状态页文本保留全部可提取页面文字，未将总结混入原文。

本次仅补充核查证据和清单，没有将过期动议导入有效规则输出。加州州法对洛杉矶的适用需单独判断，现有 D026（民法典 §1950.6）等州级材料并不因为市级提案过期而失效。未来若发现条例，应以正式条例编号、颁布原件和生效条款更新此结论。


### 先前追查记录：新增案号与未采用的查档路径

本次不只重看旧案号，还查了市议会站内的全部内容搜索，以及市律师、住房部门和县政府的公开网页索引：

- 新增相关案号 [CF 22-0265](https://cityclerk.lacity.org/lacityclerkconnect/index.cfm?cfnumber=22-0265&fa=ccfi.viewrecord)，标题包括 Rental Access、Credit Reports、Automated Tenant Screening。其官方记录同样明确于 2024-03-09 过期，未发现后续条例。原网页及全文文字已保存到 `docs/evidence/los-angeles-screening/CF-22-0265-status.*`。
- 市议会站内搜索 `screening` 显示最多 500 条结果，实际可见 22-0279、22-0280、22-0265 等相关记录；这不是全库穷尽检查。精确短语 `Fair Chance Housing` 曾返回零结果，尽管该标题的案卷实际存在，因此不能将搜索零结果当作无此事项的证明。
- 官方县政府的 [Fair Chance 说明](https://opportunity.lacounty.gov/fair-chance-hiring-campaign/) 指向招聘规则；它不能证明洛杉矶市已经通过租客筛查条例。公开网页索引也未找到可核实的换号后正式条例或后续部门报告。
- 下一步应向市书记处、住房部门、市律师办公室索取“后续报告、移交记录、替代案号、公开草案、最终条例及生效记录”。询问换号和合并记录，比仅问旧案号是否过期更能追到后续。
- [市书记处公开资料申请指引](https://clerk.lacity.gov/i-need)提供申请入口；市级申请网站为 <https://recordsrequest.lacity.org/>。本次网页工具访问该入口返回403，尚未验证提交表单。[市律师办公室联系页](https://cityattorney.lacity.gov/contact-us)的搜索索引列公开资料申请邮箱 `cpraatty@lacity.org`；另一个 Legal Documents 页面列旧的通用邮箱，优先核对联系页专用入口后再发送。
- 已准备具体英文申请稿 `docs/evidence/los-angeles-screening/follow-up-request-draft.txt`，覆盖三个案号，要求提供现存文件并说明未找到资料时的搜索范围。**尚未发信或提交申请**。

当前可确认：这三个公开案卷中未找到已生效条例证据。当前仍不能确认：所有后续均不存在、部门内部没有草案，或绝无其他案号。用户随后明确要求仅立即公开检索，不代为申请、不等待。以上申请渠道和草稿属于未采用的历史方案，不是当前待执行任务。


### 即时公开检索的新结果：已颁布条文和 2026 年相关进展

用户要求只做当下公开检索，不代为申请、不等待部门回复。本轮没有发信或提交资料申请。以下结果更新上面的早期检索结论。

**1. 确实找到已生效的市级申请人信息限制，已补入 X008。**

- [市书记处正式条例 Ord. 185797（5 页）](https://cityclerk.lacity.org/onlinedocs/2017/17-0461_ORD_185797_11-25-2018.pdf)，案号 17-0461，新增 LAMC Article 5.4（§§45.40–45.45）。原件第 4–5 页载明：2018-10-10 通过，2018-10-15 市长批准，**2018-11-25 生效**。
- §45.42 禁止房东询问租客、申请人及拟入住者的移民/公民身份，要求作相关声明或证明，以及披露或威胁披露相关信息。[现行法典 §45.42](https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-319032) 仍列该节及生效日期。
- 必须连同 §45.43 看：履行联邦/州法和法院命令，以及善意索取核实申请人的财务资格或身份所必需的资料等，不被该章禁止。**不能改写成“房东不能核实身份或收入”。** §45.41 还排除州法/联邦法明确豁免市级监管的住房。
- 原 PDF 与逐页提取文字存为 `docs/evidence/los-angeles-screening/Ord-185797.pdf`、`.txt`；全文文字另以 X008 加入语料。保留 PDF 自带文字层原样，不手工修补；其第 2 页目的说明末句存在文字识别缺损，引用该句应回看 PDF，不能把提取结果当作无误的人工誊本。§45.42、§45.43 和生效记录已核对。

**2. 另有租客隐私条文，但不可当成申请人犯罪记录的一律禁查令。**

[现行 §45.33(15)](https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-356199) 涉及侵犯租客隐私的资料要求，包括犯罪记录；所属条款针对恶意骚扰租客的行为，须结合 [§45.32 定义](https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-356215) 和法律授权例外。该节标示 Ord. 188416 于 2024-12-29 生效。这里只登记线索及适用边界，没有把它推导为所有新申请人的犯罪记录筛查禁令。

**3. 找到 2026-08-05 的相关议会决定，但未证实它接续旧提案。**

- [CF 24-0124](https://cityclerk.lacity.org/lacityclerkconnect/index.cfm?cfnumber=24-0124&fa=ccfi.viewrecord) 涉及通过 TOC、密度奖励等项目新建、受可负担住房约定约束的特定混合收入住房，不能扩大成全市所有出租房。
- [住房部门报告，正文日期 2025-10-29（8 页）](https://cityclerk.lacity.org/onlinedocs/2024/24-0124_rpt_lahd_10-23-25.pdf) 描述现有招租、选择租客和收入核验流程；报告文件名中的日期与正文不同，以正文日期登记。
- [2026-07-01 委员会建议（1 页）](https://cityclerk.lacity.org/onlinedocs/2024/24-0124_rpt_hh_7-1-26.pdf) 要求将报告归档，并请住房部门在 60 日内报告申请/收入审核耗时、人员容量、流程不清造成的签约延误及改进方法。
- [2026-08-05 官方表决记录（1 页）](https://cityclerk.lacity.org/onlinedocs/2024/24-0124_ca_08-05-26.pdf) 确认通过上述委员会报告。**这是已通过的行政推进事项，不是新颁布的全市统一筛查条例。** 尚无证据把它认作 22-0279、22-0280 或 22-0265 的换号接续。
- 上述三份 PDF 及原文提取已保存为 `CF-24-0124-report-2025-10-29.*`、`CF-24-0124-committee-2026-07-01.*`、`CF-24-0124-action-2026-08-05.*`，来源和文件哈希追加到同目录 `sources.json`。

更新后的结论：已补到真实生效的身份信息限制，并查到较新的相关议会行动；旧的统一筛查/犯罪记录提案仍没有找到正式颁布的后续条例。这个结论是本次公开检索所及，不能表述成证明后续不存在。仅登记原文和证据，未自动改写规则输出。


## 整份文档复核（2026-10-03，America/Los_Angeles）

本轮核对全部 P1/P2 登记项及第三优先清单。对照本地保存原文、清单和索引，并在线复核关键来源；未重新逐页下载每份法规，也未证明所有城市不存在其他法律。以下“缺口”区分记录遗漏与法律证据不足，不能一律理解为没找到文件。

### 已修正的记录问题与仍需补证的事项

| 对应记录 | 核查结果、修正及剩余事项 |
|---|---|
| 总数与覆盖表 | 前轮快照是 96 个编号、81 个有文本、15 个无文本，81 个文本与索引哈希相符；本次新增 X102 后为 97/82/15，未重新生成索引或提取规则。旧覆盖表为历史快照。 |
| P1-1 Hoboken | D034 实际包含整个 Chapter 158，除 §158-2 算法定租外，还有 §158-1 对续租年涨幅超过 10% 的披露要求；之前登记只写算法定租，遗漏了同页另一项义务。B-781 最终通过及市长批准为 2025-07-09，现补到 7 月 13 日刊登公告，通常规则推算生效日为 7 月 29 日；详见文末。适用定义排除医疗、长期照护和拘留设施。 |
| P1-2 Jersey City | D035 原始条例与 D037 修订都在；本次又补到 25-098（X102），新增 §218-12(3) 涨租披露。已补到刊登记录和通常规则推算日期，详见文末；未冒称原件直接标明生效日。文本含 `§218-1213` 等修订编号连写以及 `No changes`，这是带修订标记的原件提取结果，不可据此生成 §218-1213。应以原件视觉中的删除线/新增文字或正式编纂版确认最终编号与条文；25-076 修改的部分须与 25-057 对读。 |
| P1-3 麻州 | X101 已存在并入索引；它只有案件记录第 #43 条。另已取得完整判决副本（第三方托管，单独存档而未替代 X101）。已移除“日期仍未核实”的旧结论，并修正“提案失败所以所有租金限制都不存在”的错误推论。 |
| P1-4 加州 | 正文、两个法案状态页和宪法日期依据均在。2026-01-01 是依据 chaptered 记录与宪法一般规则推得的日期，不能描述为状态页逐字写出的日期；未发现这项仍缺原文。 |
| P1-5 San Diego 算法定租 | D074 有 §§98.1101–98.1104 及 2025-06-21 生效注记。已纠正上方仍称“只有草案”的现状；D076 草案不能与正式版并列当作两份有效法规。 |
| P2-1 Hoboken 租金控制 | D032 与 D033 重叠。范围/豁免应定位 §155-2（一般豁免），尤其 §155-2(H)（符合条件的新建多户住房）；§155-30 是登记要求，不能只登记“全文已取”。原文还包括 §155-1.1 的既往实付租金证明要求（2025-10-22 加入），这是此前简表没反映的内容；其加入日不自动等于生效日。 |
| P2-2 Newark | D072 Article 1（§§2:31-1–2:31-9）是住房筛查，Article 2（§§2:31-10–2:31-18）是许可事项。市住房条文把正式申请后作为检查节点，州 D065 通常要求先提出附条件租房要约；不能简单用“市法更严”处理。已查州法原文，尚未取得足以断言整部市条例被取代的依据，保留逐条关系核查。D070 的豁免入口是 §19:2-2、§19:2-18.1、§19:2-18.2；没有把“未见算法禁令”升级为“不存在”。 |
| P2-3 新泽西四条州法 | 明确编号映射：D063＝46:8-21.2；D064＝46:8-26；D062＝2A:18-61.1；D061＝10:5-12。D064 不是笼统“房东自住且总共两单元”：原文说不超过两个出租单元，并有租客提前 30 日书面通知援引法律的条件。D063 除一个半月上限，还限制每年追加押金不得超过当前押金的 10%，之前简表漏记。 |
| P2-4 洛杉矶 | 收入来源章 §45.69 明写 2020-01-01 生效，已填回结果表。D044 押金利息须结合 RSO 住房范围，不能扩展为所有出租房；§151.06.02(H) 排除 mobile home parks，押金通常须持有至少一年。1990 年新增日期、2001/2003/2021 修订与各利率适用年度不可混成一个日期。另一个来源定位问题：D038 保存 §§45.65–45.69，但所记网址目前标题是 §45.67；内容范围比该链接单节宽，后续逐句引用其他节时需补对应节/整章入口。 |
| P2-5 San Diego 其他 | 原文均在。补登记 D075 收入来源分部于 2018-10-18 生效；D073 豁免应看 §98.0703，包括建筑、房东身份、通知等组合条件，不能只凭单元数判断。已有原文不代表这些条件已提取到规则。 |
| P2-6 Santa Ana | 正文含 §§8-3700–8-3703，2026-03-03 通过后 30 日，即 2026-04-02 生效。定义还排除特定历史汇总报告及按可负担住房项目要求定价的软件，不能写成一切算法软件均禁止。D086 后附刊登证明的文字层有明显乱码，核心条例与刊登证明须分开核对，不能称整份逐字无误。 |
| P2-7 Jersey City 租金控制 | X001 不仅新增 §260-21，还修订 §260-6；仅说“补 §260-21”会遗漏一处更新。§260-21 限定某些豁免只针对 §260-3(A)/(B) 定期租金涨幅，不等于登记、披露等其他义务一并豁免。X002 旧章与 X001 必须合读；25-099 的 2025-09-25 是市长批准日，现补到 10 月 3 日公告，通常规则推算 10 月 15 日生效；不据此把其所述既有义务全部视为当天才生效。 |
| P2-8 麻州 CORI | D056 全文含 5.01–5.19。需分别登记市场租赁的 5.04、补贴住房的 5.05、拒绝申请前程序的 5.14，以及使用第三方报告的 5.15；不能用“犯罪记录规定全文”替代适用范围。本次已在州图书馆保存的 Massachusetts Register 1448 累计表补到本版本的 2021-06-11 生效依据；不可外推为所有条款最早起效日期。 |
| 第三优先 | 五条加州法分别已有 D023–D027，不需要再抓转载。未找到任何理由把“新闻链接没正文”当成这些法条缺失。 |

### 原清单之外发现的相关证据缺口

1. **新泽西犯罪记录分类的配套法律未登记。** 已有 D065 是住房筛查法，但[州总检察长说明](https://www.njoag.gov/about/divisions-and-offices/division-on-civil-rights-home/know-the-law/fair-chance-in-housing-act/)还明确关联 P.L.2021, c.298，用于解释外州和联邦犯罪记录分类。本轮取得[州议会正式文本](https://pub.njleg.gov/bills/2020/PL21/298_.HTM)，第 4 节规定立即生效，批准日期为 2021-11-08。该法修改/补充刑法分类，并非直接修改 D065 的住房条文；不能说 D065 全文因此错误。HTML 和纯文本保存在 `docs/evidence/document-audit/NJ-PL2021-c298.*`，本轮未另入语料编号。
2. **洛杉矶押金利息的适用解释缺失。** 已保存[住房部门官方说明](https://housing.lacity.gov/wp-content/uploads/2023/01/44-Interest-Payments-on-Security-Deposits-English.pdf)至 `docs/evidence/document-audit/LAHD-deposit-interest.*`，用于支持上表 RSO 范围；它是官方说明，不替代 D044 条文本身。年度利率需按所判断年份另查，不从旧年份外推。
3. **Newark 测试结论需要明确日期与层级。** D069 的新泽西 FAIR Act 为 2026-07-20 批准，其第 9 节写“批准后第十二个月的第一日”生效，即 **2027-07-01**。因此截至本次核查日尚未生效；“Newark 没搜到市级禁令”和“州法何时适用”是两个问题，不能把测试某一日的“两条均不适用”写成永久法律事实。[州议会原文](https://pub.njleg.state.nj.us/Bills/2026/AL26/43_.HTM)

### 15 个仍无正文的编号，不等于 15 份法律缺失

| 编号 | 本轮处理判断 |
|---|---|
| D017–D021 | 加州条文转载，已有 D026、D023、D024、D025、D027 对应官方文本，无需补转载。 |
| D028 | 加州反垄断法律评论，已有 D022、X003–X006 相关官方材料；不再为评论补正文。 |
| D055、D059 | 麻州诉讼评论/新闻；X101 已补裁判结果；完整法院判决已有第三方托管副本，可引用，不能再算作全文缺失。 |
| D060 | 新泽西 FAIR Act 评论；已有 D069 官方文本。 |
| D077 | San Diego 租户保护介绍；已有 D073 官方条文。 |
| D087 | Santa Ana 新闻；已有 D086 正式条例。 |
| D002、D015、D030、D054 | 仍未抓取的评论/新闻/协会材料。原清单未要求补这些二手全文，本轮也未逐项证明其全部命题已被官方文本覆盖；不应直接标为“已完全替代”，亦不应只为消除空格而导入二手资料。 |

### 后续使用本清单时的证据要求

- “是”仅表示取得所列材料；整章、单节、摘要、案件摘录、状态页应明确区分。X101 尤其不可标为完整判决。
- 日期分成通过、批准、公布、生效；前三者结合适用的州法可形成注明条件的推算日期，不能冒称原件直接标明的日期。UTC 抓取日期 2026-10-04 与本地工作日期 2026-10-03 是时区差异，不是矛盾。
- 新旧条文、重复章节、修订删除线和文字识别问题须在提取前核对。保留原始文本，不靠猜测修补字词。
- 本轮证据文件来源、抓取时间和哈希见 `docs/evidence/document-audit/sources.json`。本轮没有发送公开资料申请，也没有把上述未决事项包装为已经解决。


## 进一步找原文（2026-10-03，America/Los_Angeles）

本次改查诉讼参与方保留的文件、州图书馆法规公报、法典发布站的条例附件及市政府旧会议档案。没有提交资料申请或联系外部人员。所有下载件及来源记录放在 `docs/evidence/further-research/`。

### 1. 麻州 IP 25-21：法院判决全文已取得，可引用托管副本

- [美国商会案件页](https://www.uschamber.com/cases/administrative-law-and-government-litigation/cella-v-campbell)链接一份[27 页判决 PDF](https://www.uschamber.com/assets/documents/Opinion-Cella-v.-Campbell-Mass.pdf)，已下载为 `Cella-opinion-third-party-copy.pdf`，另存文字层。内容为 16 页多数意见及 11 页 Kafker 协同意见。
- PDF 案号 SJC-13893、2026-06-23 日期和末尾裁判结果，与已读的[法院官方案件记录](https://www.ma-appellatecourts.org/docket/SJC-13893)一致。这是法院判决文本的第三方托管副本，不是美国商会对判决的新闻摘要，也不是法院官方下载件。
- 依用户本轮指示，纠正之前过严的来源分类：**可以引用这份法院判决全文，同时注明第三方托管。** 法院是文本的作出者，商会是文件保存者；托管方不同不会自动把判决变成二手评论。已核对主要身份信息和裁判结果，但未取得法院文件作逐字/逐字节比对，也不声称是法院认证副本。文件目前仍单独存档，未另分配语料编号或覆盖 X101；这是入库状态，不是全文缺失。

### 2. 麻州 CORI：生效日期已补到

- 州图书馆保存的 [Massachusetts Register 第 1448 期](https://archives.lib.state.ma.us/bitstreams/52909959-c92e-4864-aae5-14199d53f46e/download)，PDF 第 48 页（纸页 40）的累计表，列出 `803 CMR 5.00 ... Housing`、原发布期号 `1445`，**Effective Date 为 6/11/21**。
- 因此 D056 对应的 2021 年版本可登记为 **2021-06-11 生效**。这比法规主页的版本日期更直接；不是用下载时间猜测。不能据此说所有条款都在这天首次出现。
- 已保存整份公报和单页文字摘录。公报注明电子版供信息使用，正式版为纸本；这里准确标为“州图书馆官网保存的公报电子版”，不声称取得认证纸本。

### 3. Jersey City：找到遗漏的后续修订 25-098

- [正式条例 PDF](https://mcclibraryfunctions.azurewebsites.us/api/ordinanceDownload/16093/1436781/pdf?forceDownload=true) 共 4 页，**2025-09-24 最终通过，2025-09-25 市长批准**；已保存原 PDF 和文字，登记为 **X102**。
- 新增 §218-12(3) “Mandatory Disclosure for Rent Increases”：住宅单位的租约或书面涨租通知须附相应声明，说明未以条例所列方式使用租金定价服务商等。不能只保留 25-057 和 25-076，就把后续条文当作齐全。
- 该新增文本未设置 Hoboken §158-1 的“续租年涨幅超过 10%”门槛；两个城市的披露要求不能混用。25-098 同时修正 §218-1 的保安服务文字，这部分不是算法定租条款。
- PDF 未单列确切生效日期；本轮结合批准及刊登证据，按通常规则推算为 2025-10-15，见下节。X102 已完成保存和登记，未重新生成索引或修改规则输出。

### 4. 五份新泽西条例：补到刊登证据与具体推算日期

此次沿市书记处 Public Notices 和报纸公告档案继续查，补到了此前缺少的批准/刊登信息。以下五项从“缺日期依据”更新为“按通常规则推算，有通过、批准、刊登来源”；不是五份官方生效日期证明书。

| 条例 | 最终通过 | 市长批准 | 公告刊登 | 生效日（通常规则推算） |
|---|---|---|---|---|
| Hoboken B-781（D034） | 2025-07-09 | 2025-07-09 | 2025-07-13 | **2025-07-29** |
| Jersey City 25-057（D035） | 2025-05-21 | 2025-05-22 | 2025-05-30 | **2025-06-11** |
| Jersey City 25-076（D037） | 2025-07-16 | 2025-07-17 | 2025-07-25 | **2025-08-06** |
| Jersey City 25-098（X102） | 2025-09-24 | 2025-09-25 | 2025-10-03 | **2025-10-15** |
| Jersey City 25-099（X001） | 2025-09-24 | 2025-09-25 | 2025-10-03 | **2025-10-15** |

**推算方法及边界。** [州议会原文包](https://pub.njleg.state.nj.us/statutes/STATUTES-TEXT.zip)的 N.J.S.A. 40:69A-181(b)、40:69A-185 规定，适用条例通常不得早于最终通过并获必要的市长批准后 20 日生效；40:49-2(d) 要求通过后刊登公告。上表从最后完成的必要批准日期加 20 个日历日，且各项公告均在该日之前刊登。B-781 第 4 节要求依法通过和公布后生效；本轮未在所读条例中发现更晚指定日期。推算以适用通常程序、没有紧急决议提前生效、有效公投申请暂停或其他特别延期为条件；未取得对每项排除这些例外的证明，故不标为“官方直接确认”。这是条例本身的起效日期推算，不能替代具体条款可能涉及的既有义务或适用时间判断。

**Jersey City 原始证据。** [市书记处](https://www.jerseycitynj.gov/cityhall/Clerk)保存的三份最终通过公告：[May 21 公告](https://www.jerseycitynj.gov/common/pages/GetFile.ashx?key=ryk%2bAW7X)、[July 16 公告](https://www.jerseycitynj.gov/common/pages/GetFile.ashx?key=QSk%2fAYHX)、[September 24 公告](https://www.jerseycitynj.gov/common/pages/GetFile.ashx?key=hHxAATuC)，分别列有 25-057、25-076、25-098/099，底部 Insert Date 分别为 5 月 30 日、7 月 25 日、10 月 3 日。三份一页 PDF 已下载并视觉核对上述字段。另在 [NJPA 公告档案](https://www.njpublicnotices.com/Archive/ArchiveSearch.aspx)分别按条例号检索，The Record, Hackensack 的 Published 字段与三个日期一致；市方预定刊登日期和档案实际刊登日期分别登记。通过及市长批准日期见原有 D035、D037、X001、X102 正式条例。

**Hoboken 原始证据。** [会议记录 ID 12291](http://hobokennj.iqm2.com/Citizens/Detail_LegiFile.aspx?ID=12291)确认 7 月 9 日最终通过；[原始附件](http://hobokennj.iqm2.com/Citizens/FileOpen.aspx?Type=30&ID=69209)第 4 节提供生效条款。附件第 3 页是留空的签署表，不能当成已签署批准证明。批准证据来自 NJPA 档案的 B-781 法定公告：The Record, Hackensack 2025-07-13 刊登，明写市长 APPROVED: July 9, 2025，另有 7 月 31 日重复刊登。公告的 PASSED: June 4, 2025 与会议记录中的首次审议对应，不能误当最终通过日；此处保留来源差异并采用会议记录确认最终通过。该公告是政府刊登的原始公示，不是记者的解释文章。

**保存与限制。** 新证据在 `docs/evidence/effective-dates/`，包括三份 Jersey City 公告、Hoboken 会议附件、两节州法摘录、公告档案可见字段及检索条件。NJPA 详情页遇到验证码，未继续；已读取的搜索结果足以看到报纸名称、刊登日期及 Hoboken 的批准文字，但不声称取得报纸整版或刊登宣誓证明。来源与文件哈希见该目录 `sources.json`，逐项推算记录见 `date-derivations.json`。图片公告未作为逐字文本导入语料。

其余适用范围、Newark 市条文与州法的关系、原件删除线/文字识别问题仍按上方复核表保留。此次仅更新证据和登记说明，语料编号数量仍为 97/82/15，没有重新运行规则提取，也没有发出资料申请。
