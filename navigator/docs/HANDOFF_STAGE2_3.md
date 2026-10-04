# 第二、三阶段交接规范

> **更新：** 第一阶段的输出格式已改为版本 2，字段含义、方向规则见 [STAGE1_CONTRACT.md](STAGE1_CONTRACT.md)。本文第 2、4 节中关于 `applicability` 和冲突标记的描述以那份文件和 [STAGE2_3.md](STAGE2_3.md) 为准。

读者：负责搭"地址查询"（第二阶段，题目里叫 Module B）和"变更追踪"（第三阶段，Module C）的 AI。

- 题目说明：`starter-pack/participant-final-no-hour16 3/README.md`（必读第 4、5、7、8 节）
- 第一阶段（从法律原文里提取规则）已经做完，代码在 `navigator/`，不要改 `navigator/nav/`、`navigator/eval/`、`navigator/prompts/` 里的文件。
- 新代码放在 `navigator/lookup/`（第二阶段）和 `navigator/changes/`（第三阶段）。只用 Python 标准库。

---

## 1. 三个阶段怎么接

```
第一阶段  work/rules_enriched.json ──┐
                                     ├─► 第二阶段 ─► outputs/lookups.json
data/sample_addresses.csv ─► 地址解析 ┘        │
                                               └─► 第三阶段 ─► outputs/changes.json
dev/change_tests.json ─────────────────────────────┘
```

第二、三阶段**不调用大模型**。全部是确定的程序：同样的输入，每次跑出同样的结果。

---

## 2. 输入一：规则表 `navigator/work/rules_enriched.json`

一个列表，现在 114 条。每条的字段：

| 字段 | 含义 | 第二、三阶段怎么用 |
|---|---|---|
| `team_rule_id` | 我们自己的编号，如 `r-0022` | 写进 `lookups.json` |
| `jurisdiction` | `CA` / `NJ` / `MA`，或 `"San Francisco, CA"` 这种 | 和地址的州、城市比对 |
| `level` | `state` 或 `city` | 判断谁取代谁 |
| `category` | 六类之一（见下） | 同类规则之间才谈取代和冲突 |
| `status` | `in_force` / `not_yet_effective` / `pending` / `failed` | **只是提取时的快照，不要直接用**，见第 5 节 |
| `lifecycle` | `enacted`（已通过）/ `pending_bill`（提案）/ `failed`（已失败） | 用它加 `effective_date` 重新算状态 |
| `effective_date` | `YYYY-MM-DD` 或空 | 和查询日期比较 |
| `applicability` | 适用条件，见下 | 判断某个地址适不适用 |
| `coverage_conditions`、`exemptions` | 文字描述 | 写解释时引用；程序判断只用 `applicability` |
| `overrides` | 这条规则取代或让位的规则编号 | **现在永远是空的**，见第 4 节 |
| `conflict_flag`、`conflict_note` | 来源之间对不上 | **现在不可靠**，见第 4 节 |
| `citation`、`source_url`、`quoted_span`、`retrieved` | 出处 | 写解释、做展示时用 |

六类 `category`：`rent_increase_limits`（涨租上限）、`just_cause_eviction`（正当理由驱逐）、`security_deposits`（押金）、
`application_screening_fees`（申请/筛查费）、`screening_restrictions`（筛查限制）、`algorithmic_rent_setting`（算法定租）。

`applicability` 的样子：

```json
{
  "built_on_or_before": "1979-06-13",   // 这天或之前建成的才适用；没有就是 null
  "built_after": null,                   // 这天之后建成的才适用
  "date_basis": "certificate_of_occupancy",  // 日期指的是"入住证日期"还是 "construction_date"
  "min_units": null, "max_units": null,  // 单元数门槛
  "owner_dependent": true,               // 是否取决于房东是谁
  "other": null                          // 其他写不成结构的条件（文字）
}
```

---

## 3. 输入二：地址表（第二阶段自己先做出来）

原始文件 `starter-pack/participant-final-no-hour16 3/data/sample_addresses.csv`，500 行。
列：`address_id, street_address, postal_city, state, zip, year_built, units, use_code, use_description`。

**先做一步"地址解析"，产出 `navigator/work/addresses_resolved.json`：**

```json
{
  "A0001": {
    "state": "CA",
    "legal_city": "Los Angeles, CA",        // 法律上属于哪个市，写法和规则表的 jurisdiction 一致；不在这九个市里就写 null
    "geocode": {"matched": true, "source": "census", "place_name": "Los Angeles city", "place_geoid": "0644000"},
    "resolved_by": "geocoder",              // geocoder / postal_city_fallback / unresolved
    "year_built": 1927,                      // 没有就是 null
    "units": 32,                             // 没有就是 null
    "units_at_least": 5                      // 从 use_description 能读出的下限，读不出就是 null
  }
}
```

要点：

1. **邮寄城市不等于法律上的城市。** 表里有 Dorchester、Roxbury、East Boston、Brighton、Allston、South Boston、Jamaica Plain、Hyde Park、Mattapan（都属于 Boston），还有 San Ysidro（属于 San Diego）。必须用人口普查局的地址解析服务（Census Geocoder，`geocoding.geo.census.gov`，免费、不用密钥、一次可批量 1 万行）查出"建制市"（incorporated place）。
2. 解析服务对不上的地址：退回用 `postal_city` 加一张手写的"街区 → 城市"小表，并把 `resolved_by` 记成 `postal_city_fallback`。**不要默默猜。**
3. 解析结果存盘缓存，现场演示时不再联网也能跑。
4. 数据缺口（题目明说了）：San Diego、Berkeley 没有建成年份；Berkeley、Jersey City、Newark、Boston 公寓行、Hoboken 大多没有单元数；**完全没有房东信息**。
5. `units_at_least`：`use_description` 里常写着"Five or more apartments""Apartment 5 to 14 Units""4-8-UNIT-APT"之类。能读出下限就填，后面判断单元数门槛时用得上（比如门槛是"2 个单元以下豁免"，下限 5 就足以判定豁免不成立）。

---

## 4. 第一阶段还欠的东西（第二阶段开工前必须知道）

这些是现有规则表的已知缺陷。第二阶段**不要假设它们是好的**。

| 欠什么 | 现状 | 第二阶段怎么办 |
|---|---|---|
| 取代关系 `overrides` | 永远是空列表 | 第二阶段自己建一张取代表，见 5.4 |
| 一些生效日期是空的 | 加州 AB 325（`r-0034`）应为 2026-01-01；新泽西 FAIR 法（`r-0072`、`r-0073`）应为 2027-07-01，却标成了已生效 | `work/overrides.json`（人工更正文件）里已经有几条更正，但**当前的 `rules_enriched.json` 是更正之前生成的旧文件**，开工前先在 `navigator/` 下跑一次 `python3 run.py ingest` 重新生成，再核对这三条的日期。还缺的更正往这个文件里加，**注明依据**；不要写死在代码里 |
| San Diego 算法条例标成"待定" | 只拿到草案 | 等正式文本补进来（见 `MISSING_LAW_TEXTS.md` P1-5） |
| 冲突标记不可靠 | 多数是格式差异造成的假冲突（同一个数字两种写法） | 第三阶段的冲突标记**不要**读规则上的 `conflict_flag`，按 6.3 自己算 |
| 适用条件不全 | 旧金山 1979-06-13 截止日有时缺失；洛杉矶的日期依据写成了建成日期（应为入住证日期）；加州"入住证未满 15 年豁免"是滚动的，没有字段表达 | 见 5.3 的补充字段 |
| Hoboken、Newark 一条市级规则都没有；Jersey City、Santa Ana 没有算法禁令 | 缺原文 | 等补文本；代码按"规则来了就能用"的方式写，不要为这几个市写特例 |
| 规则太多太碎 | 新泽西 26 条，多数来自一本手册 | 不影响查询逻辑 |

**请第二阶段的 AI 提需求而不是绕过去：** 发现规则表缺某个判断所需的事实，就记到 `navigator/work/stage1_requests.md`（哪条规则、缺什么、哪个地址因此只能答"不确定"）。

---

## 5. 第二阶段：对每个地址、每条规则给出结论

### 5.1 输出 `navigator/outputs/lookups.json`

```json
{
  "as_of": "2026-10-01",
  "lookups": {
    "A0001": [
      {"team_rule_id": "r-0022", "result": "superseded", "explanation": "……", "conflict_flag": false}
    ]
  }
}
```

- **500 个地址都要有**，哪怕是空列表。
- `result` 只有五种：`applies`（适用）、`unknown`（不确定）、`superseded`（被更严的规则取代）、`not_yet_effective`（已通过但还没生效）、`pending`（只是提案）。
- **不适用的规则不要写进去。** `failed`（已失败）的规则永远不写进去。
- 入口函数必须带查询日期参数：`lookup(address_id, as_of="2026-10-01")`。第三阶段要用别的日期调它。

### 5.2 判断顺序（每条规则对每个地址走一遍，走到第一个能下结论的就停）

1. **地区对不上** → 不写。州级规则看州；市级规则看 `legal_city`。地址的 `legal_city` 是 `null`（解析失败）时，市级规则一律 `unknown`，并说明原因。
2. `lifecycle` 是失败 / 撤回 → 不写。
3. `lifecycle` 是提案 → `pending`。
4. 已通过，但 `effective_date` 晚于查询日期 → `not_yet_effective`。
5. 已通过，`effective_date` 是空 → 当作已生效，但在解释里写"原文未载明生效日期"。
6. **适用条件**（见 5.3）：确定不满足 → 不写；缺数据判断不了 → `unknown`；满足 → 继续。
7. **取代关系**（见 5.4）：同一地址、同一类别里有更严的规则适用 → 这条写 `superseded`。
8. 以上都过了 → `applies`。

### 5.3 适用条件怎么判

| 条件 | 有数据时 | 缺数据时 |
|---|---|---|
| 建成 / 入住证日期截止 | `year_built` 明显早于或晚于截止年份 → 直接判 | 没有年份 → `unknown` |
| 截止日期按入住证算（`date_basis = certificate_of_occupancy`） | `year_built` **等于截止年份** → `unknown`（题目明确要求：旧金山 1979、洛杉矶 1978） | — |
| 滚动年限（如加州"入住证未满 15 年豁免"） | 用查询日期减年限算出截止年；同样，卡在边界年 → `unknown` | 没有年份 → `unknown` |
| 单元数门槛 | 用 `units`；没有就用 `units_at_least` | 两个都没有 → `unknown` |
| 取决于房东身份（`owner_dependent`） | — | 一律 `unknown`，除非别的事实已经让例外不可能成立（题目示例："5 个单元以上，所以自住豁免不可能成立" → `applies`） |
| `other` 里的文字条件 | 程序不解读 | 如果是豁免性质的 → `unknown`，解释里引用这句话 |

滚动年限现在规则表里没有字段。请在 `applicability` 里按下面的名字读，**读不到就当没有**；第一阶段之后会补上：

```json
"exempt_if_newer_than_years": 15      // 入住证未满 N 年的建筑豁免
```

### 5.4 取代关系（规则表里没有，第二阶段自己建）

建一个配置文件 `navigator/lookup/precedence.json`，**不要写死在代码里**：

```json
[
  {"category": "rent_increase_limits", "state": "CA",
   "rule": "市级租金管制适用于该地址时，州级上限 (Cal. Civ. Code § 1947.12) 记为 superseded",
   "yielding": {"jurisdiction": "CA", "citation_contains": "1947.12"},
   "prevailing": {"level": "city"},
   "basis_rule_id": "r-0022",
   "basis": "§ 1947.12 自己写明：受更低涨幅的地方租金管制约束的住房不适用本条"}
]
```

- 每一条取代关系都要有**原文依据**（哪条规则的哪句话），写在 `basis` 里。没有原文依据的不要加。
- 只有当"更严的那条"对这个地址的结论是 `applies` 时，才把让位的那条写成 `superseded`。更严的那条是 `unknown` → 让位的那条也写 `unknown`，解释里说明取决于市级规则是否覆盖。
- 算完以后把结果回填到 `rules.json` 的 `overrides` 字段（让位的规则编号列表），这样提交的三个文件互相对得上。

### 5.5 解释（`explanation`）怎么写

- 一两句大白话，说清"为什么是这个结论"，用到了地址的哪个事实。
- `unknown` 必须说出**缺的是哪个事实**（"数据里没有建成年份""取决于房东是否为个人，数据里没有房东信息"）。
- 不给建议，不教人规避规则。界面和导出文件都要带一句"非法律意见"。
- 用模板拼出来，不调用大模型。

---

## 6. 第三阶段：五道变更测试题

### 6.1 输出 `navigator/outputs/changes.json`

```json
{
  "T1": {"affected_address_ids": ["A0001"], "conflict_flag_address_ids": [], "notes": "……"},
  "T2": {}, "T3": {}, "T4": {}, "T5": {}
}
```

五道题都要有；`conflict_flag_address_ids` 没有就给空列表。地址编号排序后输出。

### 6.2 每道题怎么算

题目文件：`starter-pack/participant-final-no-hour16 3/dev/change_tests.json`。
里面的 `rule_ids`（如 `CA-ALG-01`）是出题方的编号，和我们的 `r-xxxx` 不一样。建一张对照表 `navigator/changes/test_rule_map.json`，按"地区 + 类别 + 引用"匹配，**不要按编号写死**。

| 题 | 类型 | 做法 | 受影响地址 |
|---|---|---|---|
| T1 | 前后两个日期 | 用 2025-12-31 和 2026-01-02 各查一次，取结论变了的地址 | 全部加州地址（之前 `not_yet_effective`，之后 `applies`） |
| T2 | 边界 | 用 2026-10-01 查；Hoboken 禁令只落在 Hoboken 地址，Jersey City 禁令只落在 Jersey City 地址，Newark 两条都没有 | Hoboken 地址 + Jersey City 地址；`notes` 里分开列出各多少个 |
| T3 | 前后两个日期 + 冲突 | 2026-10-01 → `not_yet_effective`，2027-07-02 → `applies` | 全部新泽西地址；冲突标记 = Jersey City + Hoboken 地址 |
| T4 | 待定法案 | 两条麻州法案在 2026-10-01 都是 `pending` | 全部麻州地址（Boston + Cambridge） |
| T5 | 反例 | 公投问题记为 `failed` | **空列表**。并且检查：Boston、Cambridge 的查询结果里没有任何 `rent_increase_limits` 类的 `applies` |

现在的对照情况：

| 出题方编号 | 我们的规则 | 状态 |
|---|---|---|
| CA-ALG-01 | `r-0034` | 有，缺生效日期 |
| NJ-ALG-01 | `r-0072`、`r-0073` | 有，缺生效日期，状态标错 |
| MA-ALG-P1 / P2 | `r-0046`（H.5222）、`r-0047`（S.2983） | 好的 |
| HOB-ALG-01 | 无 | **缺原文** |
| JC-ALG-01 | 无 | **缺原文** |
| MA-RENT-P1 | 无（`r-0036` 是另一个失败的法案 H.3744） | **缺原文** |

缺原文的三条见 `MISSING_LAW_TEXTS.md`。原文补进来之前，T2 和 T3 的冲突标记答不出来，`notes` 里照实写"规则缺失"，不要编造。

### 6.3 冲突标记怎么算

不读规则上的 `conflict_flag`。规则是：

> 同一个地址、同一个类别，同时有一条**州级**规则（已通过，不论是否生效）和一条**市级**规则（已通过），而两者谁优先在原文里没写清楚 → 这个地址打冲突标记，交人工复核。

**更正（实测后）：** 上面这条太宽，会把近一半答案都标上。现在改为只标 `lookup/review_pairs.json` 里列出的、有原文依据的州/市规则组合。

T3 就是这种情况：新泽西 FAIR 法（州）对 Jersey City 和 Hoboken 的禁令（市）。`lookups.json` 里这些地址上相关规则的 `conflict_flag` 也要同步设为 `true`。

---

## 7. 交付时的自查清单

第二阶段：
- [ ] `lookups.json` 有 500 个地址编号，和样本文件完全一致
- [ ] 每个 `team_rule_id` 都能在 `rules.json` 里找到
- [ ] `result` 只出现那五种值；没有 `failed` 的规则
- [ ] Dorchester、Roxbury 等地址解析成 Boston；San Ysidro 解析成 San Diego
- [ ] 旧金山 `year_built = 1979`、洛杉矶 `year_built = 1978` 的地址，对应租金管制规则是 `unknown`
- [ ] 没有建成年份的地址（San Diego、Berkeley 全部），按年份划线的规则是 `unknown`
- [ ] 取决于房东身份的规则没有被答成 `applies`（除非例外已不可能成立）
- [ ] Boston、Cambridge 地址下没有任何"适用"的涨租上限
- [ ] 同样的输入跑两次，输出逐字节相同
- [ ] 有一份记录文件（audit log）：每个地址每条规则走到了第几步、用了哪个事实

第三阶段：
- [ ] 五道题都有答案；T5 的受影响列表是空的
- [ ] T1、T3 的结果是真的用两个日期各查一次比出来的，不是按州直接列地址
- [ ] 换一个查询日期重跑，T1/T3 的结论会跟着变
- [ ] 缺原文的题，`notes` 里照实说明

测试放在 `navigator/tests/`，用 `python3 -m unittest` 能跑。

---

## 8. 评分权重（决定先做什么）

地址覆盖 20 分（**漏掉一条本该适用的规则，扣双倍**）、变更追踪 15 分、引用 15 分、大白话解释 10 分、负责任设计 10 分。
所以：拿不准的时候答 `unknown` 比不写要好；宁可多报一条 `unknown`，不要漏报。
