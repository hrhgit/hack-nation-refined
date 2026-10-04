# 给 TypeScript 迁移的行为变更清单（Python 侧，2026-10-04）

这是 Python 实现在提交 `e67acd2` 之后改过的行为。迁移时请让 TypeScript 的结果和下面一致；每一项后面列了对应的 Python 测试（`python3 -m unittest discover -s tests`），测试就是行为的准确说明。

起因：有人逐条核对了 18 条优先规则（[work/conditions_review_verified.md](../work/conditions_review_verified.md)），其中 6 条的表达有错。原文依据我都回到随包原文核对过，6 条都成立，所以改了下面这些。

## 一、会改变结果的代码改动

### `nav/facts.py`（评测脚本的一部分，改后需要用户 `--approve-harness`）

| 改动 | 行为 | 测试 |
|---|---|---|
| `unspace_numbers(text)`，在 `numbers_in` 开头调用 | 合并扫描页把数字拆开的空隙：`$ 1, 000` → `$1,000`，`( 30)` → `(30)`。否则 Santa Ana 条例的数字核对、日期核对在所有版本里都误报失败 | `test_conditions.OcrSpacingTest` |
| `RX_DAYS_AFTER` 放宽 | 除了 "takes effect … days after"，也认 "(shall be / is / becomes) effective thirty (30) days after its adoption"；括号里允许有空格 | 同上 |
| 新增 `RX_ADOPTED_DAY_OF` | "ADOPTED this 3rd day of March, 2026" 也算批准日期，和 `RX_APPROVED` 的结果取并集；`act_dates` 仍然要求恰好一个条款、一个批准日期，所以 → 2026-04-02 | 同上 |

### `nav/conditions.py`（模型写的条件 → 平铺字段）

| 改动 | 行为 | 测试 |
|---|---|---|
| 新字段 `covered_if_newer_than_years` | `built_within_years` 的 `role` 现在可以是 `covered`：规则本身是给新楼的好处（NJ 2A:42-84.5，新建多户住宅 30 年内免受地方租金管制），适用的就是 N 年内建成的楼。多个取较小的 N | `CoveredAlternativesAndMergeTests.test_covered_years_and_government_owner_note` |
| 新字段 `alternatives`（列表） | `role` 为 `covered` 的 `built` / `units` 条件可带 `"also":"…"`（最多 200 字）。有 `also` 时不写进 `built_*` / `min_units` / `max_units`，而是存成 `{"flats":{…含 date_basis},"also":"…"}` | `test_covered_limit_with_also_is_kept_apart` |
| `OWNER_KIND` 扩大 | 没有户数上限、文字里有 government / public(ly) owned / public housing / housing authority / city、county、state、municipal owned 的 `owner` + `exempt`，记成 `program_notes`，不再让整栋楼变成"不确定"（`owner_dependent` 保持 false） | `test_covered_years_and_government_owner_note` |
| `add_deferred(items, new)`（`_finish_exempt` 和 `merge` 都用它） | 同一个豁免窗口被写了两次：一份条件更全（日期 + 30 年上限），一份只有日期，则保留条件更全的那份。比较时忽略 `date_basis`；一个窗口的条件集合是另一个的真子集才替换，不相关的豁免各自保留 | `test_the_same_exemption_written_short_and_in_full_keeps_the_full_one` |
| `merge` | 键列表加了 `covered_if_newer_than_years`；`alternatives` 按并集合并 | 同上 |

### `lookup/engine.py`（第二阶段）

| 改动 | 行为 | 测试 |
|---|---|---|
| `covered_if_newer_than_years` | 边界 = 查询日期减 N 年（二月二十九日按月末处理，与 `exempt_if_newer_than_years` 相同）；用 `decide(边界, "after")`：更新 → met，更老 → excluded，边界年或缺年份 → unknown | `test_stage23.test_a_rule_that_is_a_benefit_for_new_buildings_covers_only_the_new_ones` |
| `alternatives` | 每项对 `flats` 跑同一套 `tests()`：全部 met → met；有 excluded → **unknown**，说明 "the stated limit leaves this building out, but the text also covers …, which the data cannot show"；有 unknown → unknown | `test_a_limit_with_another_covered_kind_leaves_outside_buildings_open_not_excluded` |
| 单元数矛盾 | `units` 和 `units_at_least` 同时存在且 `units < units_at_least` 时：对每个门槛分别按"准确数"和"下限"判断，两种读法结论一致才下结论，否则 unknown，解释里写 "cannot both be right"；房东例外的 `known_lower` 在矛盾时当作没有（→ unknown）。样本里只有 A0227（2 对 ≥93） | `test_conflicting_unit_counts_do_not_settle_a_threshold` |
| 校验 | `covered_if_newer_than_years` 要求非负整数 | — |

### `nav/ingest.py`（评测脚本的一部分）

- `FEDERAL_CITATION`：`citation` 拆成用分号隔开的几段，**每一段**都含联邦法条（`U.S.C.`、`C.F.R.`、`Pub. L.`）才拒收，错误信息 "…is a federal law; this program records only state and city rules…"。州条文旁边顺带提到联邦法条的不受影响。提示词本来就写着联邦法不记，这是把它变成强制检查。测试：`test_agent.test_a_record_that_cites_only_federal_law_is_rejected`。

### `changes/engine.py`（变更题 T5 的反例检查）

- 反例检查"麻州地址不能出现适用的涨租上限"现在跳过带 `preempts_local` 关系的规则：州禁止地方租金管制（40P）是禁令，不是上限。之前它因为条件写错一直是"不确定"才没触发。测试：`test_stage23.test_a_state_ban_on_local_rent_control_is_not_a_rent_cap`，并同步改了 `test_stage23_acceptance.test_actual_t1_t3_t4_and_negative_case` 里同样的断言。

### 展示类（不改结论）

`nav/agent.py: describe_conditions`、`lookup/review.py`、`lookup/cli.py`：显示 / 报告新字段；核对表里多一行 "手写补充条目"（来自 `coverage_sources`，原来看不出旧金山的日期条件是手写的）。

## 二、不用移植的语言无关改动

- 提示词：`prompts/agent/cards/building_age_and_size.md`、`owner_and_exceptions.md`，以及同样三处在 `prompts/extract_prompt.md`（单次备用版）里的对应句子。
- 答案钥匙：`eval/cond_labels.py` 新增 5 条（LA-RSO-eviction、MA-40P、NJ-2A:42-84.5、LA-relocation、LA-JCO），改了 LA-RSO 一个探针（1978 年之后建的楼，最好的答案从"不确定或排除"改为"不确定"）；`eval/CONDITIONS_LABELS.md` 由 `eval/cond_sheet.py` 重新生成。
- 数据：D048-01、D041-01、D067-02 三个文本包用新卡片重新提取（旧回答在 `work/archive_agent_run2_before_card_fix/`）；`outputs/*`、`work/*` 由 `run.py ingest` 和 `python3 -m lookup build --offline` 重新生成。

## 三、迁移时要注意的两点

1. `tests/.migration/python-*.log` 是在这些改动之前记录的，新增的测试名和部分输出（规则数 97、T1–T5 不变，但个别地址的结论变了）会和旧基线对不上；以现在的 Python 输出为准重新记录基线。
2. 模型输出有随机性：卡片改了以后，要验证行为请用 `python3 eval/agent_run.py` + `python3 eval/conditions_check.py`（探索模式，不碰评测脚本），不要拿单次 `run.py api --agent` 的差异当回归。
