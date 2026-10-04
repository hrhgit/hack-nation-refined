# 18 条优先规则的人工核对结果

核对日期：2026-10-04。查询日期沿用原表的 **2026-10-01**。

结论：不能把这 18 条都解释成“地址资料不够”。其中 **6 条需要修正规则表达或处理资料冲突，2 条可以进一步细分，其余 10 条的当前结果有依据**。这不等于已证明每个地址在现实中适用或豁免。

本次逐条阅读来源上下文，并用当前 `LookupEngine.from_files()` 对 500 个地址重新计算。`lookup.review.render(engine)` 与原 `conditions_review.md` **逐字一致**；以下数量全部是现有程序的复算结果，不是修复后的结果，也不是官方评分。没有改动规则、地址、查询输出或程序。

原名单的入选原因是：11 条在所在地区全部不确定，另外 7 条发生过条件排除；它并不是“18 条全部不确定”。

## 逐条结论

“适用”指当前项目按建筑资料判断的结果；租客情况、具体行为以及列在备注中的房屋类型仍可能改变现实义务。“排除”指该规则从该地址的输出中消失。

| 规则 | 现有结果 | 核对结论 | 原文、缺失资料或问题 |
| --- | --- | --- | --- |
| r-0136 Berkeley 租金涨幅 | 不确定 40 | 当前不确定有依据 | 40 个地址全部缺年份，也没有入住许可证日期。D009 区分 1980 年 6 月后的新建住宅；40 个地址至少 5 户，房东自住双户例外不是本批不确定的原因。 |
| r-0125 Boston 租客筛查 | 不确定 60 | 当前不确定有依据 | D010 的范围是接受 DND 资金或土地、或有 BPDA 指定限收入住房的住房提供方。样本不含这些项目资料；不能仅因在 Boston 就判适用，也不宜简化为“只管单个受资助单元”。 |
| r-0024 CA 正当理由驱逐 | 适用 147；不确定 98；排除 5 | 当前结果有依据 | D023 明列近 15 年取得入住许可证的住房例外。98 个不确定均缺年份：Los Angeles 6 个、San Francisco 2 个、Berkeley 40 个、San Diego 50 个。5 个被排除地址年份为 2012、2016、2018、2019、2019。 |
| r-0022 CA 租金涨幅 | 适用 76；被其他规则取代 71；不确定 98；排除 5 | 当前日期条件结果有依据 | D024 的近 15 年例外与前条一致。71 个“取代”不是不确定。本次未将条件核对扩大为全部州、市优先关系审计。 |
| r-0079 Jersey City 租金涨幅 | 不确定 50 | **需修正历史豁免条件；当前仍有其他真实缺项** | 两组重复的新建豁免中，一组漏了最长 30 年期限；还把改用途、重建区及 1998 年空置认证并成一个未决条件。详见下文。 |
| r-0085 Los Angeles RSO 驱逐保护 | 适用 47；不确定 8；排除 25 | **排除依据不充分** | D041 同一句还覆盖 §151.28 的替代住宅，程序只留下 1978-10-01 截止日。25 个较新建筑不能仅凭年份一律排除；没有证据证明它们实际都是替代住宅。 |
| r-0159 Los Angeles 搬迁补偿 | 不确定 80 | **合并后的条件失真** | 记录本来同时覆盖 RSO 或 JCO 住宅，却把 JCO 不覆盖 RSO 的条件合入，并把部分政府住房例外变成不设户数上限的房东条件；80 个不确定均由该房东条件造成。 |
| r-0210 Los Angeles 拆除重建保护 | 不确定 80 | 可细分，不能直接批量改成适用 | 确需“Protected Unit”身份和拆除重建情形。D043 也明确所有 RSO 单元都是 Protected Units；可以复用已核实的 RSO 身份，再把拆除作为义务触发条件说明，详见下文。 |
| r-0035 MA 40P §4 | 不确定 110 | **把地方例外条件错误套到州级禁止规定上** | 房东名下少于 10 个出租单元、市场租金超过 $400，限制的是地方可采用的例外租控方案，不是州级禁止规定是否存在的条件。 |
| r-0065 NJ 申请费上限 | 适用 86；不确定 53；排除 1 | **法律门槛有依据，但唯一排除存在资料冲突** | D066 确实排除一户、两户住宅。被排除的 A0227 同时有 `units=2` 和 `units_at_least=93`，不能直接认可这次排除。 |
| r-0170 NJ 寄宿屋驱逐 | 不确定 140 | 当前不确定有依据 | D067 的门槛不只是至少两处居住单元，还要求无私人厨房、浴室及特定居住关系，且有类型例外。现有资料不能确认寄宿屋身份。 |
| r-0053 NJ 房东自住两户、三户住宅驱逐 | 排除 86；不确定 54 | 当前结果方向有依据 | D067 有明确小节专门讨论此类住宅，不能把它当成全州一般驱逐保护。86 个大楼排除有依据；54 个仍缺房东居住或户数资料。字段只写最多 3 户，尚未表达至少 2 户；本批没有因此产生确定适用。 |
| r-0217 NJ 1992 转换住宅保护 | 不确定 140 | 可按县缩小不确定范围 | D067 说当时合资格县只有 Hudson。Newark 属 Essex：按这一语料版本，50 个 Newark 地址应在地域上排除，余下 Jersey City 50 个、Hoboken 40 个仍缺转换及租客资格资料。 |
| r-0050 NJ 新建多户住宅租控豁免 | 适用 30；不确定 106；排除 4 | **条件方向反了** | 规则自身讲“新楼获地方租控豁免”；程序却在新楼上删掉这条豁免说明，并在老楼上标适用。 |
| r-0227 Newark 租金涨幅 | 不确定 50 | 当前不确定有依据 | 新建住宅豁免有申请、认证及期限条件；旧楼还可能涉及空置和大修豁免。48 个缺年份，另 2 个有年份也不能排除其他豁免。不是“该租控只管需要备案的新建筑”。 |
| r-0229 Newark 租客筛查 | 不确定 50 | 当前不确定有依据 | D072 的例外取决于两户住宅另一户由房东或其家庭居住，以及自住房内房间出租。50 个样本均无准确户数、无可用户数下限，也无居住资料。 |
| r-0095 San Diego 正当理由驱逐 | 不确定 50 | 当前不确定有依据 | D073 §98.0703(k) 有近 15 年入住许可证例外；50 个全部缺年份。都有至少 5 户，因此双户自住例外不是这批不确定的原因。 |
| r-0191 San Francisco 租金涨幅 | 适用 71；不确定 2；排除 7 | 当前日期条件结果有依据 | D079 写明 1979-06-13 后取得入住许可证的新建单元不受涨租限制；D080/D083 是当年的数值。两项不确定确实缺年份。该日期条件由 `coverage_facts.json` 补入，原核对表没有展示这份补充来源。 |

## 需要修正的六项

### 1. r-0035：40P 的条件作用对象错了

原文先限制市镇制定、维持或执行租控，然后列出允许地方采用例外方案的条件。“少于十个出租单元”是同一人或实体名下的出租单元总量，既不是单栋户数，也不是房产栋数；$400 说的是公平市场租金。

缺这些资料，确实不能判断某个地方方案如何覆盖某套房，但不应把整条州级禁止规定在 110 个地址上都降成不确定。应将州级禁止及其对地方规则的影响，与例外方案的资格条件分开表达。

证据：[随包 D048，第 25 行起](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D048.txt:25>)；[麻州议会现行原文](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40P/Section4)，本次联网读到的相关段落一致。

### 2. r-0050：把“给予豁免”当成“这条规则自身不适用”

随包 D067 第 964–968 行说明新建多户住宅可获地方租控豁免。当前 `exempt_if_newer_than_years=30` 的程序含义却是：最近 30 年的新楼不显示本条规则。

实际被删掉的是 A0002（2001）、A0168（2007）、A0227（2010）、A0489（2000）；它们都在 2026-10-01 的 30 年时间范围内。A0227 另有户数冲突，不能直接判已获豁免。程序同时对 30 个较老建筑显示“适用”，这也容易让读者误以为老楼享有新楼豁免。

应表达“本条给予其他租控规则的豁免”，保留多户住宅资格、期限以及需从相关法条核对的手续条件，不能简单删除年龄条件后把全部地址判适用，也不能据这段简述断言四个地址已经取得豁免。

证据：[随包 D067](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D067.txt:964>)；[NJ DCA 官方指南](https://www.nj.gov/dca/codes/publications/pdf_lti/t_i_r.pdf)。

### 3. r-0085：遗漏替代住宅这一覆盖分支

来源说 RSO 一般覆盖 1978-10-01 前建成的房屋，**以及 §151.28 的替代住宅**。这两种情况不是都必须满足日期门槛。记录只保留 `built_on_or_before=1978-10-01`，所以 25 个晚于该年的建筑直接被排除。

这证明程序丢失了覆盖分支，不证明 25 个地址现实中都适用。修正时需要保存替代住宅条件；对只因日期而被排除、但替代住宅身份未知的地址，应保留未决说明，而非静默删除。8 个现有不确定为 6 个缺年份、2 个只有边界年 1978。

证据：[随包 D041，第 21–23 行](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D041.txt:21>)。

### 4. r-0159：RSO 与 JCO 的条件被混在一起

D043 的搬迁补偿义务面向 RSO **或** JCO 住宅；D040 解释 JCO 覆盖尚未受 RSO 管制的大多数住宅。JCO 的这项范围说明，不能变成整个搬迁补偿记录对 RSO 的排除。

当前 80 个不确定的直接原因是 `owner_dependent=true` 且没有户数上限。其引用依据只是“部分 HACLA 或政府所有的住房”，不能推出“任何房屋都必须先知道房东身份”。按本项目把政府或资助住房类型例外保留为备注的口径，这里也出现了表达不一致：同一类例外写成 `other` 会成为备注，写成 `owner` 就挡住全部结果。

应分清 RSO、JCO 各自的覆盖路径，再处理相应例外。不能仅清掉房东条件就声称这 80 个地址均已核实适用。JCO 的六个月租期条件也应留在 JCO 分支，不能无差别套给 RSO。

证据：[随包 D043，第 6–11 行](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D043.txt:6>)；[随包 D040，第 22–24 行](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D040.txt:22>)；[条件解析中的两条不同处理路径](/Users/herh/MyFiles/Projects/hack-nation/navigator/nav/conditions.py:210)。

### 5. r-0079：历史豁免漏期限，并重复保存

独立补充原文 X002 §260-6(C) 同时要求：1987-06-25 至 1992-06-25 的新建窗口、非老年人用途、贷款偿还期或 30 年的较短期限，以及备案和向租客出具说明。现有记录同时保留了：

- 仅有 1987–1992 窗口和备案条件的一组；
- 同一窗口加上 30 年条件的另一组。

第一组漏期限，会使一栋 1990 年建成、即使已超过 30 年的楼仍被当作“可能因为备案而豁免”。只在内存副本暂时拿掉其他未决条件，用 1990 年、10 户、查询日 2026-10-01 检查，实际仍返回 `unknown`。这说明错误可以独立重现。

当前 50 个实际地址还缺改用途、重建区或 1998 年空置认证资料，所以修掉这一重复条件并不保证它们立即变成适用。按该历史窗口与 30 年上限，期限本身还可用于排除已经失效的豁免可能性，无需一直索要旧备案。

证据：[独立补充 X002，第 118–122 行](/Users/herh/MyFiles/Projects/hack-nation/navigator/corpus_extra/text/X002.txt:118)。**此依据属于独立研究材料，不自动计入比赛引用评分。**

### 6. r-0065：唯一被排除的地址户数冲突

法律确实有一户、两户住宅例外，问题出在地址 A0227：

- 官方样本 CSV 的 `units` 是 2，用途描述是 `13B-93U-2C-G`。
- 本地地址整理从描述读出 `units_at_least=93`。
- 查询程序优先使用 `units=2`，因而从申请费上限规则中排除它。

当前材料不足以证明 2 或 93 哪一个代表本次法律判断所需的整栋住宅户数。应先标记资料冲突、核对字段含义及对应建筑范围；不能直接接受排除，也不能擅自把准确户数改成 93。全部 500 个地址中，此类“准确户数小于已解析下限”的冲突只发现这一条。

证据：[随包 D066，一户两户例外](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D066.txt:33>)；[随包样本 CSV 第 228 行](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/data/sample_addresses.csv:228>)；[用途描述解析](/Users/herh/MyFiles/Projects/hack-nation/navigator/lookup/addresses.py:34)。

## 两项可以继续细分

**r-0217：按县区分。** D067 的合资格县说明可与已确认的法律城市相结合。按本次语料版本，Newark 的 50 个地址在 Essex，不能一直与 Hudson 的 90 个地址一同保持地域未决。应保留来源时间，不能把“当前只有 Hudson”的指南文字当作永远不会变化的规定。

证据：[随包 D067，第 2137–2144 行](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D067.txt:2137>)；[NJ 官方城市、县目录](https://www.nj.gov/cgi-bin/infobank/localsearch.pl)；[Hudson County 官方登记机构目录](https://www.nj.gov/cgi-bin/dhss/vital/registrars.pl?county=Hudson)。后两项是研究核验，不是新增比赛计分语料。

**r-0210：把住宅资格和发生拆除分开。** D043 把 Protected Units 分为几类，明确包括所有 RSO 单元。因此它不是一个完全无法从现有规则推导的陌生身份。但不能直接把现有 r-0085 的 47 个“适用”无条件当作法律上确认的 RSO 身份；应先处理上面的覆盖分支与例外问题。对已确认身份的住宅，可将“为新建而拆除”列为义务触发情形；收入、历史用途等仍需补充。

证据：[随包 D043，第 260–265 行](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D043.txt:260>)，以及第 281–282 行。

## 其余原文定位与边界

- Berkeley：[D009 覆盖表](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D009.txt:15>)。Golden Duplex 还要求 1979-12-31 自住及目前自住；不能以后把它简化为所有自住双户住宅。当前至少五户的样本不受这一细节影响。
- Boston：[D010 政策范围](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D010.txt:14>)；[Boston 官网仍列出该政策链接](https://content.boston.gov/departments/housing/affirmative-fair-housing-marketing)。本次没有取得逐栋资助名册。
- California：[D023](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D023.txt:203>)、[D024](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D024.txt:128>)。程序在非边界年份用建成年份判断入住许可证日期，这是当前项目的近似口径，不等于拿到了每栋楼真实证书；移动住房及个别租期例外仍需说明。
- NJ 两户、三户住宅及寄宿屋：[D067 对应小节](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D067.txt:1935>)。r-0053 引用的节号来自指南该段，但不能据此说整部 §2A:18-61.2 只适用于小楼。
- Newark 租控：[独立补充 D070 §19:2-18.1](/Users/herh/MyFiles/Projects/hack-nation/navigator/corpus_extra/text/D070.txt:1120>)、[备案要求 §19:2-24.1](/Users/herh/MyFiles/Projects/hack-nation/navigator/corpus_extra/text/D070.txt:1488>)；[当前城市法典](https://ecode360.com/36623772)。期限取贷款偿还期与 30 年中较短者；不能把“新楼”直接等同于已取得豁免。独立补充材料不自动计入比赛引用评分。
- Newark 筛查：[独立补充 D072](/Users/herh/MyFiles/Projects/hack-nation/navigator/corpus_extra/text/D072.txt:13>)；[城市法典 §2:31-1](https://ecode360.com/36642000)。
- San Diego：[随包 D073 §98.0703](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D073.txt:119>)；[市政府原文](https://docs.sandiego.gov/municode/municodechapter09/ch09art08division07.pdf)。
- San Francisco：[随包 D079 第 48 行](</Users/herh/MyFiles/Projects/hack-nation/starter-pack/participant-final-no-hour16 3/corpus/text/D079.txt:48>)；[实际使用的覆盖补充](/Users/herh/MyFiles/Projects/hack-nation/navigator/lookup/coverage_facts.json:1>)。这里只核对涨租覆盖条件，不把它推广成驱逐保护也有同一建成年份门槛。

联网核验用于对照研究。部分页面（LA 搬迁补偿 PDF、LA JCO、CA §1946.2、NJ 申请费法案）本次网页读取失败，对这些条目的结论依据随包原文，不声称已确认网页最新全文。其他网页也不用于追溯替代 2026-10-01 的比赛语料。

## 复算与版本记录

核对使用 97 条规则、500 个地址。首次重新生成原表完全一致；另读取每个地址的条件检查结果，确认每类不确定和排除的直接原因；只做一次内存副本的 Jersey City 隔离检查，没有调用模型，也没有重新生成正式输出。

收尾复查时，工作区其他工作更新了日期处理，整表仅出现名单之外 r-0198 的生效日期从空值变为 2026-04-02；本次 18 条优先规则的完整区块保持一致。以下四个输入文件的指纹也保持不变。本报告未覆盖、撤销或纳入那项独立修改。

| 输入文件 | SHA-256 |
| --- | --- |
| `work/conditions_review.md` | `1814acf86152f9fe6a72271b05259e738941275d8faff8297bd507ff112f3411` |
| `work/rules_enriched.json` | `c09aa022b6e38edab059194f28dcd2a182d976245f93d59b0a2dc8cf6c0a67b8` |
| `work/addresses_resolved.json` | `2993a4c0392f8cf0a4b2c9ba9a028221a64316141b1e54eddca76a12ed2e6625` |
| `lookup/coverage_facts.json` | `41d281f5a9710404ed7283d8d3182ee9cc2ce4af588e66ef5448f70809f4e6dd` |

后续优先处理会把规则直接隐藏的 r-0085、r-0050 和 A0227 资料冲突，再处理 r-0035、r-0159 的条件对象与分支，以及 r-0079 的期限重复。未知数量下降只能算表达改进；不能代替对真实房屋资格的核实。
