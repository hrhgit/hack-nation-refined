# 地址查询和变更追踪

非法律意见。结论仅基于所列来源和地址事实。

## 运行

在 `navigator/` 下执行，需要 Node.js 22 或更新版本。先安装并编译 TypeScript 后端：

```bash
npm ci
npm run build

# 第一次确定地址属于哪个城市，需要联网；查询全部500行，不截断
npm run lookup -- resolve

# 当前已保存全部地址的 Census 返回，下面可完全离线运行
npm run lookup -- resolve --offline
npm run lookup -- build --offline

# 按日期查看单个地址
npm run lookup -- lookup --address-id A0001 --as-of 2026-10-01
npm run lookup -- lookup --address-id A0002 --as-of 2027-07-02

# 只重新计算变更题
npm run changes --

# 原生完整流程测试，不需要 Python
npm test

# 参考实现及两种后端的完整核对；这一步另需 Python 3
npm run verify
```

`build --as-of` 改变地址查询和提交规则表的日期。变更题使用题目文件里各自的日期。要改变变更比较日期，可以传入 `--date-overrides dates.json`，例如：

```json
{
  "T1": {"as_of_before": "2026-01-02", "as_of_after": "2026-01-02"},
  "T3": {"as_of_before": "2027-07-02", "as_of_after": "2027-07-02"}
}
```

```bash
npm run changes -- --date-overrides dates.json
```

这个例子两个日期相同，T1 和 T3 的受影响列表均为空；程序实际比较规则结论，没有直接按州填写地址编号。日期覆盖不改原题文件。

## 从后两个阶段的需要设计

`LookupEngine` 接收“规则事实、已解析地址、取代关系”，它可以直接使用独立的测试规则，不依赖第一阶段代码。它需要的是规则是否通过、生效时间、覆盖条件和出处，不使用提取时的状态快照或冲突标记。当前第一阶段文件由 `loadRules` 读取，在有依据的情况下补充后续判断需要的事实。

```typescript
import {LookupEngine, lookup} from './dist/lookup/engine.js';

const first = lookup('A0001', '2026-10-01');
const engine = LookupEngine.fromFiles();
const second = engine.lookup('A0002', '2027-07-02');
```

按地区、通过状态、生效时间、覆盖条件、取代关系的顺序判断。失败的规则始终不输出。已通过但还未生效、提案和缺事实的规则分别输出对应状态。确定不满足条件才省略；未知结论逐项说明缺哪个事实。

| 地址事实 | 如何使用 |
|---|---|
| `state`、`legal_city` | 确定州、市；城市未确定时保留同州市级规则为不确定 |
| `year_built` | 按题目规定代理建筑日期；位于截止年时保留不确定 |
| `construction_date`、`certificate_of_occupancy` | 若以后有准确日期，直接判断截止日；不需要改判断程序 |
| `units` | 有准确单元数时直接判断 |
| `units_at_least` | 用明确的用途描述判断下限；不能把下限当作准确数量 |
| 房东身份 | 样本没有，通常保留不确定；只有明确的单元数上限已经使例外不可能时才排除该例外 |

`applicability` 支持交接要求的建筑日期、单元数、房东和其他条件，以及 `exempt_if_newer_than_years`（该年限内的新楼豁免）、`covered_if_newer_than_years`（规则只管该年限内的新楼）、`alternatives`（带"另一类也覆盖"的限制，限制之外是不确定而不是排除）。单元数的准确值小于用途描述的下限时视为数据矛盾，不据此下结论（见 `docs/STAGE1_CONTRACT.md`）。滚动年限按每次查询日期重算。补充字段 `owner_exempt_if_units_at_most` 表示有原文依据的房东例外单元数上限。无法表达的条件通过 `coverage_missing` 保留不确定并提出需求。纯文字条件不在程序里猜测。

只给年或月的生效日期保留一个可能区间，查询日位于区间内时答不确定，不编造某一天。已知只针对特定期间的数字用 `valid_through` 限定；过期后不继续拿旧数字回答。导出规则日期若无法写成题目允许的状态，会明确停止并要求补事实。

## 地址解析和缓存

当前默认使用 Census 的单地址查询，直接请求 Incorporated Places（建制市边界）。也提供 `--geocode-mode batch`：先批量查坐标，再查城市边界。[Census 官方说明](https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html)明确批量地址返回不包含市级边界，不能把邮寄城市当成市级边界。

本次批量入口返回 Request Rejected，因此改用明确支持的单地址入口完成查询。程序没有网络超时或自动降级限制；网络服务报错时保留已完成缓存，重新运行继续使用缓存。

- 全部500个地址已有返回缓存；476个采用 Census 城市边界，24个没有确定匹配而采用 `postal_cities.json` 对照表。
- Dorchester、Roxbury 等归到 Boston；San Ysidro 归到 San Diego。Census 确定的法律城市优先于邮寄城市。
- 没有匹配、多个匹配或匹配到了其他州时，明确记录对照表回退；没有对照项时保留未确定。
- 缓存键包含地址、数据版本和请求参数；地址改变后不能误用旧返回。建筑事实改变但地址相同，也需重新 `resolve`，该过程复用已有地址缓存。
- 批量方式的10000行是服务自身的每批限制；程序处理全部批次，不是产品总量上限。

## 输出和记录

| 文件 | 内容 |
|---|---|
| `outputs/rules.json` | 与查询一致的规则状态、结构条件、来源和取代关系；格式为 `{"rules": [...]}`，与官方模板一致 |
| `outputs/lookups.json` | 500个地址，每条规则的结论、原因和复核标记 |
| `outputs/changes.json` | T1到T5的受影响地址、需复核地址和说明 |
| `work/addresses_resolved.json` | 地址事实、法律城市、采用哪种解析方式 |
| `work/geocode_cache/` | Census 的原始返回，可离线重放 |
| `work/lookup_audit.json` | 每个地址、每条规则经过的步骤、事实、缺项和出处，包括被省略的规则 |
| `work/changes_audit.json` | 外部题号对应哪些规则、实际比较日期和变更证据 |
| `work/stage23_audit.json` | 输入、代码和输出的文件指纹，可检验重跑结果 |
| `work/stage1_requests.md` | 哪条规则缺什么事实，以及哪些地址因此不确定 |

取代关系在 `lookup/precedence.json`；必须有原文依据和来源，且只在更严的规则确实适用时判断让位。更严规则也不确定时，下层规则一并保留不确定。提交规则的 `overrides` 采用“本规则取代的让位规则编号”，方向由 `interaction` 说明。

覆盖条件补充放在 `lookup/coverage_facts.json`（现在只剩一条，旧金山的租金管制截止日，因为那句话在另一份文件里；其余十一条在模型自己能读出同样条件后已删除，每次构建的核对报告会列出补充条目改写了哪些提取值），都有依据，按地区、类别、引用或来源文档匹配。它们不新增法律记录，不绕过第一阶段的引文检查。题目编号对照在 `changes/test_rule_map.json`，按地区、类别、引用匹配；没有写死 `r-xxxx` 编号。

复核标记只给 `lookup/review_pairs.json` 里列出的州/市规则组合，每一项必须有原文依据（现在只有一项：新泽西 FAIR 法写明市政府不得制定与之冲突的条例，所以它和同类市级禁令的关系需人工复核）。不再因为“同类别里州和市都有规则”就标记。尚未生效的已通过规则也参与判断，提案和失败记录不参与。变更题只检查它指定的那组州/市关系，避免被其他规则的复核标记带偏。

## 该阶段最初运行的事实缺口（历史记录）

下面保留该阶段最初运行的结果；之后第一阶段继续更新了规则。TypeScript 迁移使用并行修改结束后的 97 条规则和 108 个分包，最新核对结果见 [迁移报告](TYPESCRIPT_MIGRATION.md)。

交接时旧文件有114条。按要求用当前第一阶段重新生成后，有91条通过检查、41条记录尚未通过，41/65个分包完成。后两个阶段使用通过检查的规则；受拒收或尚未提取的规则影响的覆盖范围还不能宣称完整。

AB 325 的2026-01-01沿用交接中的有依据更正。新泽西 FAIR 法的2027-07-01更正写入 `work/overrides.json`，依据 D069 通过日期和第9节的“通过后第12个月第一天生效”。没有改 `nav/`、`eval/` 或 `prompts/` 的实现。

| 题目 | 当前结果 | 尚缺什么 |
|---|---|---|
| T1 | 加州250个地址结论发生变化 | 当前对应规则可算 |
| T2 | 当前已提取规则无法提供完整答案，列表为空且注明缺规则 | Hoboken、Jersey City 的结构化禁令规则；Hoboken D034 原文已出现在补充语料，需要第一阶段提取 |
| T3 | 新泽西140个地址结论发生变化；当前无法给出市级冲突的完整名单 | 同上，需要市级规则才能判断和同步复核标记 |
| T4 | 麻州110个地址为提案可能影响范围 | 当前对应规则可算 |
| T5 | 受影响列表为空，实际检查没有适用的麻州涨租上限 | IP 25-21失败公投记录仍未提取，不拿另一个失败法案替代 |

样本没有旧金山1979年地址，所以该边界用独立构造的地址测试；洛杉矶1978年的两个真实地址均为不确定。缺建成年份、入住证、准确单元数、房东和租约信息的情况逐条记在需求文件中。

本次新增测试覆盖五种结论、失败规则排除、两种日期边界、滚动年限、单元数下限、房东例外、取代方向、未来州法的复核标记、五道变更题和缺规则处理。独立构造的 Hoboken/Jersey City 法规验证补齐规则后的 T2/T3行为；不把这些构造规则加入真实输出。两个完整离线生成过程，包括记录文件，逐字节相同。

最初全项目有一个测试失败：`test_explore_mode_skips_the_gate_but_never_touches_the_climb_folder` 要求 `eval/extraction/baseline` 不存在，但该目录已有实际评测结果。迁移前已将测试改为检查这些已有文件逐字节不变，没有删除评测结果；最终全项目测试通过。

> 第一阶段输出给本阶段的字段、方向规则和校验方式见 [STAGE1_CONTRACT.md](STAGE1_CONTRACT.md)（版本 2）。下面关于关键词分类的说明只适用于按旧格式提取的规则。

## 文字条件和输出语言

- 写进提交文件的解释、说明和免责声明都是英文；程序报错和本文件是中文。
- 规则里写不成结构的文字条件（`applicability.other`）分两种：说的是**建筑、单元或房东本身**的（含 exempt、owner-occupied、subsidized、certificate of occupancy 等词）判为不确定；说的是**什么情况下触发义务**的（如“搬迁少于 20 天时”“收取申请费时”）不影响是否覆盖，结论照常，条件原样写进解释。可用 `applicability.other_kind` 设为 `building` 或 `trigger` 明确指定。
- `coverage_note`：只影响个别租约的条件（如 Costa-Hawkins 下的租约状态）写成提示，不把整栋楼判为不确定。`coverage_missing` 仍然判为不确定。
- 加州 §1947.12、§1946.2 的房东类豁免：样本每一行是一个多单元公寓地块，不属于“可单独转让的单元”，所以只有“房东自住的两单元房产”这一项有单元数可比；这是一个判断，依据写在 `lookup/coverage_facts.json` 里，不同意可以删掉那两项。
