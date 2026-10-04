# 第一阶段输出给第二、三阶段的约定（版本 2）

读者：做地址查询和变更追踪的人或 AI。第一阶段提取每条规则时，除了题目要求的字段，还会输出下面这些字段，程序（`nav/ingest.py`、`nav/conditions.py`）检查之后写进 `work/rules_enriched.json`。

## 为什么要改

旧格式有三个问题，都已经在真实结果里出现：

1. **方向写反。** 旧金山的原文是"入住证在 1979-06-13 之后的单元**豁免**"，模型把这个日期写进了"建成日期**晚于**才适用"，结果 71 个本该适用的旧金山地址里，这条规则全被悄悄丢掉。
2. **缺字段。** 加州"入住证未满 15 年豁免"、房东自住豁免的单元数上限，旧格式没有位置放，第二阶段只能靠人手写补充条目。
3. **没有出处。** 条件对不对，没法回到原文核对。

新格式让模型**照原文的说法抄**（"只适用于……"或"……豁免"），方向和加减一由程序处理。

## 模型写什么

每条规则的 `applicability` 是：

```json
{"conditions": [ ... ], "per_tenancy": "文字或 null", "coverage_quotes": ["原文逐字摘录", ...]}
```

`conditions` 里每一项是下面五种之一。`role` 是 `covered`（原文说只适用于这些）或 `exempt`（原文说这些豁免或不适用）。

| type | 例子（原文 → 写法） |
|---|---|
| `built` | "入住证在 1979 年 6 月 13 日之后的单元豁免" → `{"type":"built","role":"exempt","op":"after","date":"1979-06-13","basis":"certificate_of_occupancy"}`。`op` 取原文用词：`on_or_before` / `before` / `after` / `on_or_after` |
| `built_within_years` | "入住证在过去 15 年内的住房豁免" → `{"type":"built_within_years","role":"exempt","years":15,"basis":"certificate_of_occupancy"}`；"新建筑豁免 30 年" 也写成 30 |
| `units` | "4 个单元及以下豁免" → `{"type":"units","role":"exempt","op":"at_most","n":4}`。`op`：`at_least` / `more_than` / `at_most` / `fewer_than` |
| `owner` | "房东自住、不超过 4 个单元的房产豁免" → `{"type":"owner","role":"exempt","who":"owner-occupied","unit_limit":4}`；原文没写单元数就 `null` |
| `other` | 年份、单元数、房东都判断不了、但可能决定整栋楼是否覆盖的条件，例如"只适用于有补贴的住房""豁免需要向政府备案" |

任何 `built`、`built_within_years`、`units` 的豁免条件可以加 `"conditional":true`：原文说这个豁免要业主先备案、登记、通知租客才生效。楼宇数据看不出有没有备案，所以程序不会据此把楼排除掉：落在这个豁免范围里的楼答"不确定"，在范围外的楼不受影响。

`other` 里写的条件，程序按字面再分两类：**涉及"哪一类住房"的**（平价、补贴、公共住房、机构住房、单独持有的单户或公寓、已受地方租金管制的）记成 `program_notes`，**只写进解释提醒，不改变结论**；其余（要备案、房东身份说不清、缺事实）仍然判"不确定"。原因：数据里看不出哪栋楼是平价住房，若都判不确定，加州租金上限对所有加州地址都不确定，题目点名的"被取代"就一个也出不来。判断用的词表在 `nav/conditions.py` 的 `PROGRAM_NOTE`，核对表里能看到每条规则的归类。

`per_tenancy`：只影响个别租约或触发条件的说明（租约何时开始、租客年龄、什么行为触发义务），**只作提示，不改变结论**。

另外两个字段在规则层：

- `valid_through`：按期间公布的数值（每年的涨幅上限）的期间最后一天。
- `relations`：原文里写明与其他层级法律关系的句子，逐字摘录。`preempts_local` = 禁止地方政府另行规定或制定冲突条例；`yields_to_local` = 有地方规定时本条不适用。

## 程序做什么

| 步骤 | 做法 |
|---|---|
| 换算成"谁被覆盖" | 豁免换成覆盖的反面，**不做日期加减**：`exempt after D` → `built_on_or_before D`；`exempt before D` → `built_on_or_after D`；单元数只做 ±1（`exempt at_most 4` → `min_units 5`） |
| 对照原文 | 每个日期、数字必须在原文里出现（"多于 4"写成 5 也认，因为 4 在原文里）。对不上的**不采信**，改记成一条 `other`，查询时答"不确定"，不会按错误条件下结论 |
| 摘录核对 | `coverage_quotes` 和 `relations` 的引文必须逐字出现在原文里，否则丢弃并记警告 |
| 需备案才生效的豁免 | 单独存在 `applicability.deferred`（每项含换算后的条件和一句说明）。第二阶段对落在豁免范围内的楼答"不确定"，范围外照常；真正的排除条件仍然优先 |
| 出错不拒收 | 这些新字段写错只会变成警告，**不会让整条规则被拒收**，所以不影响一次通过率 |
| 多个来源合并 | 同一部法律在几份文件里出现时，按字段补全，**不覆盖**；两份来源的数值不同会记警告 |

换算后的平铺字段（第二阶段读的就是这些）：

`built_on_or_before`、`built_before`、`built_after`、`built_on_or_after`、`date_basis`、`min_units`、`max_units`、`exempt_if_newer_than_years`、`owner_dependent`、`owner_exempt_if_units_at_most`、`other`、`program_notes`、`per_tenancy`、`coverage_quotes`、`deferred`、`contract`（=2 表示按新格式提取）。

## 第二阶段怎么用

- 四个日期字段都支持；入住证日期只有年份时，**截止年份那一年一律"不确定"**（题目要求）。
- `other` 在新格式下一律判"不确定"（旧格式才按关键词区分）；`per_tenancy` 写进解释，不改变结论。
- `relations` 里有 `preempts_local` 的州级规则，和同州同类别的市级规则自动配成"需人工复核"的一对，原文句子就是依据。不再需要手写 `review_pairs.json`（现在是空列表，留给人工复核后的补充）。
- `yields_to_local` 只存档，取代关系仍由 `lookup/precedence.json` 判断（要比较州和市的上限数值，需要人确认）。

## 已知限制

- **模型会读错。** 试跑中见过：把"转换用途的建筑"的日期当成所有建筑的截止日期、把软件服务商定义里的豁免当成房东豁免。提示词里已加了针对性的规则，但不能保证没有。对策是 `coverage_quotes` 让人能核对，重新提取后会出一张条件核对表。
- **丢规则比多报更贵。** 误判成"豁免"会让规则悄悄消失，所以对照原文失败时宁可答"不确定"。
- **`other` 会让很多结论变成"不确定"**，例如加州涨租上限的"受契约限制的平价住房豁免"。这是否该算"不确定"需要你判断，见重新提取后的核对表。
