# 条件答案清单（供核对）

这份文件由 `eval/cond_sheet.py` 从 `eval/cond_labels.py` 生成，答案本身写在 `cond_labels.py` 里。
每条法律下面是几个**虚构的地址**，和第二阶段应该给出的结果。结果的含义：

- **适用**：规则在这个地址上适用。
- **不确定**：缺少判断所需的事实（例如不知道房东是谁），结论是“不确定”。
- **规则被排除**：规则对这个地址不适用，结果里不会出现这条规则。**最贵的错误是把本该适用的地址排除掉**，因为输出里看不出来。

每个地址有两个答案，分两项检查：

1. **不能出错的范围**：只要不把本该展示的规则藏起来就算对。这一项守住“别漏掉规则”。
2. **最准确的答案**：必须选“适用”或“不确定”，并写明依据或缺失的事实。写“待定”的是 key 还没有定死（见下面的政策问题），不计这一项。

判断“不确定”的原则（来自第二位审阅者，已采纳）：**只有缺失的事实可能改变结论才判不确定**，即房东身份、法律要求的备案或通知、横跨截止日期的年份、缺失的户数。不因为资料不全就一律不确定，也不因为没看到豁免就直接判适用。

判断的对象是**整栋楼**：本清单判断楼宇层面的覆盖，特定单元仍可能存在例外（例如业主家属居住的某个单元），这类单元层面的例外另行判断，不会把整栋楼标成“不确定”。

年份类测试的假设：测试给的是建成年份，而法条看的往往是入住证日期。按参与者指南 §4.1，只在截止年那一年判“不确定”，其他年份用建成年份代替。

核对时请看两点：**法律的理解对不对**（“说明”一行），**每个地址该得的结果对不对**。有不同意见直接在这里标出来。

## CA-1947.12 — CA

- 说明：加州租金上限法（民法典 §1947.12）：入住证发出不满 15 年的住房豁免；有更低的地方租金管制时本条让位；2030-01-01 废止。
- 来源依据（英文）：Cal. Civ. Code 1947.12(d)(4) exempts housing with a certificate of occupancy within the previous 15 years; (d)(3) yields to a lower local cap; (o) repeals the section on 2030-01-01
- 页面：`D024-01`
- 还要核对：生效日期 = 2024-04-01；有效期至 = 2030-01-01；必须有关系 `yields_to_local`；不能有关系 `preempts_local`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 2022 年建，20 个单元 | 规则被排除（结果里不出现） | 规则被排除（结果里不出现） | certificate within the previous 15 years is exempt; 2022 is far from the boundary |
| 1950 年建，20 个单元 | 适用、不确定 | **待定**（key 没有定死） | the 15-year and duplex exemptions cannot apply; housing deed-restricted as affordable, which the data does not show, is also exempt, so the strict reading says unknown |
| 没有建成年份，20 个单元 | 不确定 | 不确定 | without a year the certificate date cannot be placed |
| 2011 年建，20 个单元 | 不确定 | 不确定 | 2011 straddles the boundary 15 years before the query date |

## CA-1946.2 — CA

- 说明：加州正当理由驱逐法（民法典 §1946.2）：入住证发出不满 15 年的住房豁免；契约限制的平价住房也豁免。
- 来源依据（英文）：Cal. Civ. Code 1946.2(e)(7) exempts housing with a certificate of occupancy within the previous 15 years; (e)(9) exempts housing deed-restricted as affordable
- 页面：`D023-01`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 2022 年建，20 个单元 | 规则被排除（结果里不出现） | 规则被排除（结果里不出现） | certificate within the previous 15 years is exempt; 2022 is far from the boundary |
| 1950 年建，20 个单元 | 适用、不确定 | **待定**（key 没有定死） | the 15-year and duplex exemptions cannot apply; housing deed-restricted as affordable, which the data does not show, is also exempt, so the strict reading says unknown |
| 没有建成年份，20 个单元 | 不确定 | 不确定 | without a year the certificate date cannot be placed |

## LA-RSO — Los Angeles, CA

- 说明：洛杉矶租金稳定条例：只适用于 1978-10-01 当天或之前建成的出租房（另有“替代单元”也算）。
- 来源依据（英文）：LAHD: the RSO applies to rental properties first built on or before October 1, 1978, as well as replacement units under LAMC 151.28
- 页面：`D041-01`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 1950 年建，20 个单元 | 适用、不确定 | **待定**（key 没有定死） | built before the cutoff year, and the replacement-unit clause only adds coverage; but the page also lists a luxury exemption granted on the landlord's application, which the data cannot show, so the strict reading says unknown |
| 1990 年建，20 个单元 | 不确定、规则被排除（结果里不出现） | **待定**（key 没有定死） | after the cutoff; a replacement unit under LAMC 151.28 could still be covered, which the data cannot show |
| 1978 年建，20 个单元 | 不确定 | 不确定 | 1978 straddles the cutoff of October 1, 1978 |
| 没有建成年份，20 个单元 | 不确定 | 不确定 | without a year the cutoff cannot be applied |

## SF-allowable — San Francisco, CA

- 说明：旧金山租金委员会：2026-03-01 到 2027-02-28 的年度允许涨幅是 1.6%（这一条只核对日期，没有地址测试）。
- 来源依据（英文）：Rent Board: the allowable annual increase is 1.6% from March 1, 2026 through February 28, 2027
- 页面：`D080-01`
- 还要核对：生效日期 = 2026-03-01；有效期至 = 2027-02-28

## BK-coverage — Berkeley, CA

- 说明：伯克利：1980 年前建的多户楼大多完全受管；入住证在 1980 年 6 月之后的新建筑豁免。
- 来源依据（英文）：Rent Board table: most units in multifamily properties built before 1980 are fully covered; new construction with a certificate of occupancy after June 1980 is exempt
- 页面：`D009-01`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 1950 年建，10 个单元 | 适用、不确定 | **待定**（key 没有定死） | the table names covered and exempt kinds but not every case; the key does not settle it |
| 2005 年建，10 个单元 | 规则被排除（结果里不出现） | 规则被排除（结果里不出现） | certificate after June 1980 is exempt; 2005 is far from the cutoff |
| 1980 年建，10 个单元 | 不确定 | 不确定 | 1980 straddles the June 1980 cutoff |

## NJ-46:8-26 — NJ

- 说明：新泽西押金法适用范围：所有出租房，但“房东自住、不超过 2 个出租单元、且租客没有提前 30 天书面通知援引该法”的除外。
- 来源依据（英文）：N.J.S.A. 46:8-26: the act applies to all rental premises except owner-occupied premises with not more than two rental units where the tenant has not given 30 days written notice
- 页面：`D064-01`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，5 个单元 | 适用 | 适用 | 5 units is above the exemption's limit of 2, so who lives there no longer matters |
| 没有建成年份，2 个单元 | 不确定 | 不确定 | whether the owner lives there, and whether the tenant gave notice, would change the result |
| 没有建成年份，用途代码显示至少 5 个单元（没有准确数） | 适用 | 适用 | at least 5 units is above the limit of 2 |
| 没有建成年份，没有单元数 | 不确定 | 不确定 | the unit count decides whether the exemption can apply |

## NJ-46:8-55 — NJ

- 说明：新泽西住房筛查法：不包括“房东自住、不超过 4 个单元”的房产。
- 来源依据（英文）：N.J.S.A. 46:8-54: a rental dwelling unit is a unit other than one in owner-occupied premises of not more than four dwelling units
- 页面：`D065-01`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，5 个单元 | 适用 | 适用 | 5 units is above the exemption's limit of 4 |
| 没有建成年份，4 个单元 | 不确定 | 不确定 | whether the owner lives there would change the result |
| 没有建成年份，没有单元数 | 不确定 | 不确定 | the unit count decides whether the exemption can apply |

## NJ-46:8-18.1 — NJ

- 说明：新泽西申请费法（2025 年第 405 号法）：一户或两户住宅里的出租单元不适用。
- 来源依据（英文）：P.L. 2025, c.405: the requirements do not apply to a dwelling unit in a one-family or two-family dwelling offered for rent
- 页面：`D066-01`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，2 个单元 | 规则被排除（结果里不出现） | 规则被排除（结果里不出现） | a two-family dwelling is exempt by its unit count |
| 没有建成年份，3 个单元 | 适用、不确定 | 适用 | 3 units rules out the one- and two-family exemption; the licensee clause concerns who collects the fee, not the building |
| 没有建成年份，用途代码显示至少 5 个单元（没有准确数） | 适用、不确定 | 适用 | at least 5 units rules out the one- and two-family exemption |
| 没有建成年份，没有单元数 | 不确定 | 不确定 | the unit count decides whether the exemption applies |

## HOB-155 — Hoboken, NJ

- 说明：Hoboken 租金管制：1987-06-25 之后建的多户住宅最多豁免 30 年，但只有业主按规定备案才豁免，楼宇数据看不出有没有备案。
- 来源依据（英文）：Hoboken 155-2(H): multiple dwellings constructed after June 25, 1987 are exempt for up to 30 years (or the mortgage amortization period if shorter), but only if the landlord complied with the notice and filing requirements of N.J.S.A. 2A:42-84.1; (G) a building vacant since January 1, 1984 and registered; (B) newly constructed dwellings registered before first rental; (F) government-owned housing
- 页面：`D032-01`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 2015 年建，30 个单元 | 不确定 | 不确定 | a building from 2015 is inside the 30-year reach, the exemption depends on a filing and notices, and its length may be shorter than 30 years |
| 1950 年建，30 个单元 | 适用、不确定 | **待定**（key 没有定死） | the new-construction exemption cannot apply; the vacant-since-1984 exemption (G) needs a registration and government-owned housing (F) is not shown by the data |
| 1990 年建，30 个单元 | 适用、不确定 | **待定**（key 没有定死） | the 30-year exemption has run out; government-owned housing (F) is not shown by the data |

## JC-260 — Jersey City, NJ

- 说明：Jersey City 租金管制：4 个及以下住房单元的楼豁免；1983 年那个日期只针对“从非永久用途转成住宅”的建筑，不是所有建筑的截止日。
- 来源依据（英文）：Jersey City 260-3: dwellings with four or fewer housing spaces are exempt; the 1983 date is only for buildings converted from nonpermanent use; low-rent public housing and newly constructed dwellings of 25 or more units in a redevelopment area are also exempt
- 页面：`X002-01`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，4 个单元 | 规则被排除（结果里不出现） | 规则被排除（结果里不出现） | four or fewer housing spaces is exempt by its unit count |
| 没有建成年份，5 个单元 | 适用、不确定 | **待定**（key 没有定死） | the count rules out the small-building exemption; public housing and redevelopment-area exemptions are not shown by the data |
| 没有建成年份，用途代码显示至少 5 个单元（没有准确数） | 适用、不确定 | **待定**（key 没有定死） | the count rules out the small-building exemption; public housing and redevelopment-area exemptions are not shown by the data |
| 1990 年建，20 个单元 | 适用、不确定 | **待定**（key 没有定死） | the 1983 date must not exclude a 1990 building; whether it is a converted nonpermanent building is not shown |
| 1970 年建，20 个单元 | 适用、不确定 | **待定**（key 没有定死） | no age exemption reaches a 1970 building; public housing is not shown by the data |

## NJ-FAIR — NJ

- 说明：新泽西 FAIR 法：2026-07-20 批准，批准后第 12 个月的第一天（2027-07-01）生效；第 6 节禁止地方制定与之冲突的条例。
- 来源依据（英文）：P.L. 2026, c.43: approved July 20, 2026, takes effect the first day of the twelfth month after enactment; section 6(b): a municipality is prohibited from enacting an ordinance that conflicts with this act
- 页面：`D069-01`
- 还要核对：生效日期 = 2027-07-01；必须有关系 `preempts_local`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，50 个单元 | 尚未生效 | 尚未生效 | enacted but takes effect on 2027-07-01 |
| 没有建成年份，50 个单元，查询日期 2027-07-02 | 适用 | 适用 | in force and no building-level condition |
| 没有建成年份，没有单元数，查询日期 2027-07-02 | 适用 | 适用 | no condition depends on the unit count |

## JC-algo — Jersey City, NJ

- 说明：Jersey City 禁止算法定租：对所有楼适用；“多处房产的业主”那一句在“服务商”的定义里，不是业主豁免。
- 来源依据（英文）：Jersey City 218-12: the carve-out for owners of several properties is inside the definition of a service provider, not an owner exemption
- 页面：`D035-01`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，10 个单元 | 适用 | 适用 | no building-level condition; the carve-out concerns conduct |
| 没有建成年份，没有单元数 | 适用 | 适用 | no condition depends on the unit count |

## HOB-algo — Hoboken, NJ

- 说明：Hoboken 禁止算法定租（§158-2）：对所有楼适用；页面只写了通过日期，没写生效日期。
- 来源依据（英文）：Hoboken 158-2 bans algorithmic rent fixing; the packet states only the adoption date
- 页面：`D034-01`

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，10 个单元 | 适用 | 适用 | no building-level condition |

## SD-algo — San Diego, CA

- 说明：San Diego 禁止自动化定租（§§98.1101–98.1104）：2025-06-21 生效。
- 来源依据（英文）：San Diego Municipal Code 98.1101-98.1104, added 5-22-2025, effective 6-21-2025
- 页面：`D074-01`
- 还要核对：生效日期 = 2025-06-21

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，10 个单元 | 适用 | 适用 | no building-level condition |

## NJ-2A:18-61.1 — NJ

- 说明：新泽西驱逐法（没见过的页面）：“房东自住、不超过 2 个出租单元”的房产除外；另有信托、业主家属居住单元的例外（原文限定为家属有发育障碍的情形，且只针对单个单元，不改变整栋楼的结论）。
- 来源依据（英文）：N.J.S.A. 2A:18-61.1: no tenant may be removed from residential premises other than (1) owner-occupied premises with not more than two rental units, a hotel or seasonal rental, (2) a unit held in trust for the owner's family, (3) a unit permanently occupied by the owner's family; exceptions (2) and (3) apply only when the family member has a developmental disability
- 页面：`D062-01`（**没参与调提示词的页面**，用作没见过的测试）

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，5 个单元 | 适用、不确定 | 适用 | DECIDED: this judges coverage of the building. 5 units rules out the owner-occupied two-unit exemption; the trust and family exceptions reach single units (and only a family member with a developmental disability), so a given unit may be an exception but that does not make the building unknown |
| 没有建成年份，2 个单元 | 不确定 | 不确定 | whether the owner lives there would change the result |
| 没有建成年份，没有单元数 | 不确定 | 不确定 | the unit count decides whether the owner exemption can apply |

## CAM-14.04 — Cambridge, MA

- 说明：Cambridge 公平住房条例（没见过的页面）：房东自己住的两户住宅有豁免。
- 来源依据（英文）：Cambridge Human Rights Commission: there is an exemption for 2-family dwellings, when the owner lives there
- 页面：`D029-01`（**没参与调提示词的页面**，用作没见过的测试）

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，5 个单元 | 适用、不确定 | 适用 | the only exemption in the source, an owner-occupied two-family dwelling, is ruled out by the count |
| 没有建成年份，2 个单元 | 不确定 | 不确定 | whether the owner lives there would change the result |
| 没有建成年份，没有单元数 | 不确定 | 不确定 | the unit count decides whether the owner exemption can apply |

## SD-TPO — San Diego, CA

- 说明：San Diego 租户保护条例（正当理由驱逐，没见过的页面）：入住证发出不满 15 年的住房豁免；房东自住的两单元房产豁免；契约限制的平价住房、有补贴的住房豁免。
- 来源依据（英文）：San Diego Municipal Code 98.0703: exempt are (k) housing with a certificate of occupancy within the previous 15 years, (j) a two-unit property where the landlord lives in one unit, (c)(d) deed-restricted or subsidized affordable housing, (h) shared bathroom or kitchen with the landlord, (l) alienable units with notice
- 页面：`D073-01`（**没参与调提示词的页面**，用作没见过的测试）

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 2022 年建，20 个单元 | 规则被排除（结果里不出现） | 规则被排除（结果里不出现） | certificate within the previous 15 years is exempt; 2022 is far from the boundary |
| 1950 年建，20 个单元 | 适用、不确定 | **待定**（key 没有定死） | the 15-year and two-unit owner exemptions cannot apply; deed-restricted or subsidized affordable housing is not shown by the data, so the strict reading says unknown |
| 没有建成年份，20 个单元 | 不确定 | 不确定 | without a year the certificate date cannot be placed |
| 1950 年建，2 个单元 | 不确定 | 不确定 | whether the landlord lives in one of the two units would change the result |

## SD-source-of-income — San Diego, CA

- 说明：San Diego 收入来源歧视禁令（没见过的页面）：只有“房东或家属住在同一栋楼并和租客共用浴室或厨房”的租约例外，这是单个租约的例外。
- 来源依据（英文）：San Diego Municipal Code 98.0804: the division does not apply to a tenancy in which the owner or a family member lives in the same building and shares a bathroom or kitchen with the tenant
- 页面：`D075-01`（**没参与调提示词的页面**，用作没见过的测试）

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，20 个单元 | 适用、不确定 | 适用 | the only exception reaches a single tenancy where the owner shares a bathroom or kitchen, so it does not change building-level coverage |
| 没有建成年份，没有单元数 | 适用、不确定 | 适用 | no condition depends on the unit count |

## SA-algo — Santa Ana, CA

- 说明：Santa Ana 禁止算法定租（没见过的页面）：对所有楼适用；定义里排除的是历史汇总报告等，是行为层面的，不是楼的条件。
- 来源依据（英文）：Santa Ana Ordinance NS-3090 (adopted March 3, 2026, effective 30 days after adoption): bans algorithmic devices that use nonpublic competitor data to set rents; the carve-outs are about kinds of reports and software, not buildings
- 页面：`D086-01`（**没参与调提示词的页面**，用作没见过的测试）

| 虚构地址 | 不能出错的范围 | 最准确的答案 | 依据或缺失的事实（英文原样） |
|---|---|---|---|
| 没有建成年份，10 个单元 | 适用 | 适用 | no building-level condition; the carve-outs concern conduct |
| 没有建成年份，没有单元数 | 适用 | 适用 | no condition depends on the unit count |

## MA-IP25-21 — MA

- 说明：麻州公投 25-21（限制涨租）：法院 2026-06-23 禁止把它放上 2026 年选票，应记为“已失败”。
- 来源依据（英文）：AG listing: 25-21 An Initiative Petition to Protect Tenants by Limiting Rent Increases; SJC-13893 rescript 06/23/2026 enjoins placing it on the 2026 ballot
- 页面：`X101-01`
- 还要核对：状态 = failed

