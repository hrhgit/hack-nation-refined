"""Hand-made answer key for the coverage conditions the extraction writes (contract version 2).

Written from the law texts in the corpus, not from any model answer. Each label names a law on one packet and lists
PROBES: made-up addresses with the answer the address lookup should give for that law. A probe has two answers:

* `ok`    the results that are acceptable, i.e. do not hide a law that covers the address. The costly mistake is a wrong
          exclusion: the law silently disappears for an address it covers. A probe whose `ok` lacks "excluded" also counts
          toward the wrong-exclusion tally.
* `exact` the single best result, with the reason (`basis`): the fact that settles it, or the missing fact that could
          change it. `None` means the key does not settle it (a policy question, see CONDITIONS.md) and the probe is not
          scored for exactness. When `ok` has one element it is also the exact answer.

Rule used for `exact` (from a second reviewer of this key): "unknown" only when a fact the data lacks could change the
result: owner status, a filing or notice the law requires, a year that straddles the cutoff, or a unit count that is missing.
Not "unknown" because data is incomplete in general, and not "applies" merely because no exemption was seen.

Assumption for every year-based probe: year built stands in for the certificate-of-occupancy date except in the cutoff year,
where the answer is "unknown" (Participant Guide section 4.1).

Facts of a probe: year_built, units (exact), units_at_least (a lower bound read from a land-use code), as_of (default
2026-10-01). Results: applies / unknown / excluded (the law is left out) / not_yet_effective / pending.
"""
from __future__ import annotations

AS_OF = "2026-10-01"
AUTO = "auto"


def probe(why, ok, year=None, units=None, lower=None, as_of=AS_OF, exact=AUTO, basis=""):
    ok = set(ok)
    if exact == AUTO:
        exact = next(iter(ok)) if len(ok) == 1 else None
    assert exact is None or exact in ok, (why, exact, ok)
    return {"why": why, "ok": ok, "exact": exact, "basis": basis or why,
            "facts": {"year_built": year, "units": units, "units_at_least": lower}, "as_of": as_of}


OLD_CA = ("the 15-year and duplex exemptions cannot apply; housing deed-restricted as affordable, which the data does not show, "
          "is also exempt, so the strict reading says unknown")

COND_LABELS = [
    {"id": "CA-1947.12", "zh": "加州租金上限法（民法典 §1947.12）：入住证发出不满 15 年的住房豁免；有更低的地方租金管制时本条让位；2030-01-01 废止。",
     "packet": "D024-01", "jurisdiction": "CA", "category": "rent_increase_limits", "cite_re": r"1947\.12",
     "source": "Cal. Civ. Code 1947.12(d)(4) exempts housing with a certificate of occupancy within the previous 15 years; (d)(3) yields to a lower local cap; (o) repeals the section on 2030-01-01",
     "effective_date": "2024-04-01", "valid_through": "2030-01-01",
     "relations": {"require": ["yields_to_local"], "forbid": ["preempts_local"]},
     "probes": [probe("certificate within 15 years: exempt", {"excluded"}, year=2022, units=20,
                      basis="certificate within the previous 15 years is exempt; 2022 is far from the boundary"),
                probe("old building must not be excluded", {"applies", "unknown"}, year=1950, units=20, exact=None, basis=OLD_CA),
                probe("no year built: cannot tell", {"unknown"}, year=None, units=20, basis="without a year the certificate date cannot be placed"),
                probe("year of the 15-years-back boundary: cannot tell", {"unknown"}, year=2011, units=20,
                      basis="2011 straddles the boundary 15 years before the query date")]},
    {"id": "CA-1946.2", "zh": "加州正当理由驱逐法（民法典 §1946.2）：入住证发出不满 15 年的住房豁免；契约限制的平价住房也豁免。",
     "packet": "D023-01", "jurisdiction": "CA", "category": "just_cause_eviction", "cite_re": r"1946\.2",
     "source": "Cal. Civ. Code 1946.2(e)(7) exempts housing with a certificate of occupancy within the previous 15 years; (e)(9) exempts housing deed-restricted as affordable",
     "probes": [probe("certificate within 15 years: exempt", {"excluded"}, year=2022, units=20,
                      basis="certificate within the previous 15 years is exempt; 2022 is far from the boundary"),
                probe("old building must not be excluded", {"applies", "unknown"}, year=1950, units=20, exact=None, basis=OLD_CA),
                probe("no year built: cannot tell", {"unknown"}, year=None, units=20, basis="without a year the certificate date cannot be placed")]},
    {"id": "LA-RSO", "zh": "洛杉矶租金稳定条例：只适用于 1978-10-01 当天或之前建成的出租房（另有“替代单元”也算）。",
     "packet": "D041-01", "jurisdiction": "Los Angeles, CA", "category": "rent_increase_limits", "cite_re": r"Rent Stabilization|151",
     "source": "LAHD: the RSO applies to rental properties first built on or before October 1, 1978, as well as replacement units under LAMC 151.28",
     "probes": [probe("old building must not be excluded", {"applies", "unknown"}, year=1950, units=20, exact=None,
                      basis="built before the cutoff year, and the replacement-unit clause only adds coverage; but the page also lists a luxury exemption granted on the landlord's application, which the data cannot show, so the strict reading says unknown"),
                probe("built after the cutoff: not covered", {"excluded", "unknown"}, year=1990, units=20, exact=None,
                      basis="after the cutoff; a replacement unit under LAMC 151.28 could still be covered, which the data cannot show"),
                probe("cutoff year: cannot tell", {"unknown"}, year=1978, units=20, basis="1978 straddles the cutoff of October 1, 1978"),
                probe("no year built: cannot tell", {"unknown"}, year=None, units=20, basis="without a year the cutoff cannot be applied")]},
    {"id": "SF-allowable", "zh": "旧金山租金委员会：2026-03-01 到 2027-02-28 的年度允许涨幅是 1.6%（这一条只核对日期，没有地址测试）。",
     "packet": "D080-01", "jurisdiction": "San Francisco, CA", "category": "rent_increase_limits", "cite_re": r"37|Rent",
     "source": "Rent Board: the allowable annual increase is 1.6% from March 1, 2026 through February 28, 2027",
     "effective_date": "2026-03-01", "valid_through": "2027-02-28", "probes": []},
    {"id": "BK-coverage", "zh": "伯克利：1980 年前建的多户楼大多完全受管；入住证在 1980 年 6 月之后的新建筑豁免。",
     "packet": "D009-01", "jurisdiction": "Berkeley, CA", "category": "rent_increase_limits", "cite_re": r"13\.76|Rent",
     "source": "Rent Board table: most units in multifamily properties built before 1980 are fully covered; new construction with a certificate of occupancy after June 1980 is exempt",
     "probes": [probe("old building must not be excluded", {"applies", "unknown"}, year=1950, units=10, exact=None,
                      basis="the table names covered and exempt kinds but not every case; the key does not settle it"),
                probe("new construction: exempt", {"excluded"}, year=2005, units=10, basis="certificate after June 1980 is exempt; 2005 is far from the cutoff"),
                probe("cutoff year: cannot tell", {"unknown"}, year=1980, units=10, basis="1980 straddles the June 1980 cutoff")]},
    {"id": "NJ-46:8-26", "zh": "新泽西押金法适用范围：所有出租房，但“房东自住、不超过 2 个出租单元、且租客没有提前 30 天书面通知援引该法”的除外。",
     "packet": "D064-01", "jurisdiction": "NJ", "category": "security_deposits", "cite_re": r"46:8-26",
     "source": "N.J.S.A. 46:8-26: the act applies to all rental premises except owner-occupied premises with not more than two rental units where the tenant has not given 30 days written notice",
     "probes": [probe("5 units: the owner exemption cannot apply", {"applies"}, units=5, basis="5 units is above the exemption's limit of 2, so who lives there no longer matters"),
                probe("2 units: the owner exemption may apply", {"unknown"}, units=2, basis="whether the owner lives there, and whether the tenant gave notice, would change the result"),
                probe("land-use code says 5 or more units", {"applies"}, lower=5, basis="at least 5 units is above the limit of 2"),
                probe("no unit count at all", {"unknown"}, basis="the unit count decides whether the exemption can apply")]},
    {"id": "NJ-46:8-55", "zh": "新泽西住房筛查法：不包括“房东自住、不超过 4 个单元”的房产。",
     "packet": "D065-01", "jurisdiction": "NJ", "category": "screening_restrictions", "cite_re": r"46:8-5[5-9]|46:8-60|c\.\s?110",
     "source": "N.J.S.A. 46:8-54: a rental dwelling unit is a unit other than one in owner-occupied premises of not more than four dwelling units",
     "probes": [probe("5 units: the owner exemption cannot apply", {"applies"}, units=5, basis="5 units is above the exemption's limit of 4"),
                probe("4 units: the owner exemption may apply", {"unknown"}, units=4, basis="whether the owner lives there would change the result"),
                probe("no unit count at all", {"unknown"}, basis="the unit count decides whether the exemption can apply")]},
    {"id": "NJ-46:8-18.1", "zh": "新泽西申请费法（2025 年第 405 号法）：一户或两户住宅里的出租单元不适用。",
     "packet": "D066-01", "jurisdiction": "NJ", "category": "application_screening_fees", "cite_re": r"46:8-18\.1|c\.\s?405",
     "source": "P.L. 2025, c.405: the requirements do not apply to a dwelling unit in a one-family or two-family dwelling offered for rent",
     "probes": [probe("2 units: a two-family dwelling is exempt", {"excluded"}, units=2, basis="a two-family dwelling is exempt by its unit count"),
                probe("3 units: covered", {"applies", "unknown"}, units=3, exact="applies",
                      basis="3 units rules out the one- and two-family exemption; the licensee clause concerns who collects the fee, not the building"),
                probe("land-use code says 5 or more units", {"applies", "unknown"}, lower=5, exact="applies",
                      basis="at least 5 units rules out the one- and two-family exemption"),
                probe("no unit count at all", {"unknown"}, basis="the unit count decides whether the exemption applies")]},
    {"id": "HOB-155", "zh": "Hoboken 租金管制：1987-06-25 之后建的多户住宅最多豁免 30 年，但只有业主按规定备案才豁免，楼宇数据看不出有没有备案。",
     "packet": "D032-01", "jurisdiction": "Hoboken, NJ", "category": "rent_increase_limits", "cite_re": r"155|Rent",
     "source": "Hoboken 155-2(H): multiple dwellings constructed after June 25, 1987 are exempt for up to 30 years (or the mortgage amortization period if shorter), but only if the landlord complied with the notice and filing requirements of N.J.S.A. 2A:42-84.1; (G) a building vacant since January 1, 1984 and registered; (B) newly constructed dwellings registered before first rental; (F) government-owned housing",
     "probes": [probe("new construction: exemption depends on a filing the data does not show", {"unknown"}, year=2015, units=30,
                      basis="a building from 2015 is inside the 30-year reach, the exemption depends on a filing and notices, and its length may be shorter than 30 years"),
                probe("old building must not be excluded", {"applies", "unknown"}, year=1950, units=30, exact=None,
                      basis="the new-construction exemption cannot apply; the vacant-since-1984 exemption (G) needs a registration and government-owned housing (F) is not shown by the data"),
                probe("built more than 30 years ago: exemption has run out", {"applies", "unknown"}, year=1990, units=30, exact=None,
                      basis="the 30-year exemption has run out; government-owned housing (F) is not shown by the data")]},
    {"id": "JC-260", "zh": "Jersey City 租金管制：4 个及以下住房单元的楼豁免；1983 年那个日期只针对“从非永久用途转成住宅”的建筑，不是所有建筑的截止日。",
     "packet": "X002-01", "jurisdiction": "Jersey City, NJ", "category": "rent_increase_limits", "cite_re": r"260",
     "source": "Jersey City 260-3: dwellings with four or fewer housing spaces are exempt; the 1983 date is only for buildings converted from nonpermanent use; low-rent public housing and newly constructed dwellings of 25 or more units in a redevelopment area are also exempt",
     "probes": [probe("4 units: exempt", {"excluded"}, units=4, basis="four or fewer housing spaces is exempt by its unit count"),
                probe("5 units: covered", {"applies", "unknown"}, units=5, exact=None,
                      basis="the count rules out the small-building exemption; public housing and redevelopment-area exemptions are not shown by the data"),
                probe("land-use code says 5 or more units", {"applies", "unknown"}, lower=5, exact=None,
                      basis="the count rules out the small-building exemption; public housing and redevelopment-area exemptions are not shown by the data"),
                probe("built 1990: the 1983 date is only about conversions", {"applies", "unknown"}, year=1990, units=20, exact=None,
                      basis="the 1983 date must not exclude a 1990 building; whether it is a converted nonpermanent building is not shown"),
                probe("built 1970: covered", {"applies", "unknown"}, year=1970, units=20, exact=None,
                      basis="no age exemption reaches a 1970 building; public housing is not shown by the data")]},
    {"id": "NJ-FAIR", "zh": "新泽西 FAIR 法：2026-07-20 批准，批准后第 12 个月的第一天（2027-07-01）生效；第 6 节禁止地方制定与之冲突的条例。",
     "packet": "D069-01", "jurisdiction": "NJ", "category": "algorithmic_rent_setting", "cite_re": r"P\.L\.\s*2026|c\.\s?43|FAIR",
     "source": "P.L. 2026, c.43: approved July 20, 2026, takes effect the first day of the twelfth month after enactment; section 6(b): a municipality is prohibited from enacting an ordinance that conflicts with this act",
     "effective_date": "2027-07-01", "relations": {"require": ["preempts_local"], "forbid": []},
     "probes": [probe("before the effective date", {"not_yet_effective"}, units=50, basis="enacted but takes effect on 2027-07-01"),
                probe("after the effective date it covers every building", {"applies"}, units=50, as_of="2027-07-02", basis="in force and no building-level condition"),
                probe("after the effective date, no unit count", {"applies"}, as_of="2027-07-02", basis="no condition depends on the unit count")]},
    {"id": "JC-algo", "zh": "Jersey City 禁止算法定租：对所有楼适用；“多处房产的业主”那一句在“服务商”的定义里，不是业主豁免。",
     "packet": "D035-01", "jurisdiction": "Jersey City, NJ", "category": "algorithmic_rent_setting", "cite_re": r"218|Ord",
     "source": "Jersey City 218-12: the carve-out for owners of several properties is inside the definition of a service provider, not an owner exemption",
     "probes": [probe("covers every building", {"applies"}, units=10, basis="no building-level condition; the carve-out concerns conduct"),
                probe("no unit count at all", {"applies"}, basis="no condition depends on the unit count")]},
    {"id": "HOB-algo", "zh": "Hoboken 禁止算法定租（§158-2）：对所有楼适用；页面只写了通过日期，没写生效日期。",
     "packet": "D034-01", "jurisdiction": "Hoboken, NJ", "category": "algorithmic_rent_setting", "cite_re": r"158-2",
     "source": "Hoboken 158-2 bans algorithmic rent fixing; the packet states only the adoption date",
     "probes": [probe("covers every building", {"applies"}, units=10, basis="no building-level condition")]},
    {"id": "SD-algo", "zh": "San Diego 禁止自动化定租（§§98.1101–98.1104）：2025-06-21 生效。",
     "packet": "D074-01", "jurisdiction": "San Diego, CA", "category": "algorithmic_rent_setting", "cite_re": r"98\.11",
     "source": "San Diego Municipal Code 98.1101-98.1104, added 5-22-2025, effective 6-21-2025",
     "effective_date": "2025-06-21",
     "probes": [probe("covers every building", {"applies"}, units=10, basis="no building-level condition")]},
    # Held out: written after the prompt was last changed, from packets that none of the prompt edits looked at.
    {"id": "NJ-2A:18-61.1", "zh": "新泽西驱逐法（没见过的页面）：“房东自住、不超过 2 个出租单元”的房产除外；另有信托、业主家属居住单元的例外（原文限定为家属有发育障碍的情形，且只针对单个单元，不改变整栋楼的结论）。",
     "packet": "D062-01", "jurisdiction": "NJ", "category": "just_cause_eviction", "cite_re": r"2A:18-61\.1(?!\d)",
     "held_out": True,
     "source": "N.J.S.A. 2A:18-61.1: no tenant may be removed from residential premises other than (1) owner-occupied premises with not more than two rental units, a hotel or seasonal rental, (2) a unit held in trust for the owner's family, (3) a unit permanently occupied by the owner's family; exceptions (2) and (3) apply only when the family member has a developmental disability",
     "probes": [probe("5 units: the two-unit owner exemption cannot apply", {"applies", "unknown"}, units=5, exact="applies",
                      basis="DECIDED: this judges coverage of the building. 5 units rules out the owner-occupied two-unit exemption; the trust and family exceptions reach single units (and only a family member with a developmental disability), so a given unit may be an exception but that does not make the building unknown"),
                probe("2 units: the owner exemption may apply", {"unknown"}, units=2, basis="whether the owner lives there would change the result"),
                probe("no unit count at all", {"unknown"}, basis="the unit count decides whether the owner exemption can apply")]},
    {"id": "CAM-14.04", "zh": "Cambridge 公平住房条例（没见过的页面）：房东自己住的两户住宅有豁免。",
     "packet": "D029-01", "jurisdiction": "Cambridge, MA", "category": "screening_restrictions", "cite_re": r"14\.04|Fair Housing",
     "held_out": True,
     "source": "Cambridge Human Rights Commission: there is an exemption for 2-family dwellings, when the owner lives there",
     "probes": [probe("5 units: the two-family owner exemption cannot apply", {"applies", "unknown"}, units=5, exact="applies",
                      basis="the only exemption in the source, an owner-occupied two-family dwelling, is ruled out by the count"),
                probe("2 units: the owner exemption may apply", {"unknown"}, units=2, basis="whether the owner lives there would change the result"),
                probe("no unit count at all", {"unknown"}, basis="the unit count decides whether the owner exemption can apply")]},
    {"id": "SD-TPO", "zh": "San Diego 租户保护条例（正当理由驱逐，没见过的页面）：入住证发出不满 15 年的住房豁免；房东自住的两单元房产豁免；契约限制的平价住房、有补贴的住房豁免。",
     "packet": "D073-01", "jurisdiction": "San Diego, CA", "category": "just_cause_eviction", "cite_re": r"98\.07|Tenant",
     "held_out": True,
     "source": "San Diego Municipal Code 98.0703: exempt are (k) housing with a certificate of occupancy within the previous 15 years, (j) a two-unit property where the landlord lives in one unit, (c)(d) deed-restricted or subsidized affordable housing, (h) shared bathroom or kitchen with the landlord, (l) alienable units with notice",
     "probes": [probe("certificate within 15 years: exempt", {"excluded"}, year=2022, units=20, basis="certificate within the previous 15 years is exempt; 2022 is far from the boundary"),
                probe("old building must not be excluded", {"applies", "unknown"}, year=1950, units=20, exact=None,
                      basis="the 15-year and two-unit owner exemptions cannot apply; deed-restricted or subsidized affordable housing is not shown by the data, so the strict reading says unknown"),
                probe("no year built: cannot tell", {"unknown"}, year=None, units=20, basis="without a year the certificate date cannot be placed"),
                probe("two units, old: the owner-occupied two-unit exemption may apply", {"unknown"}, year=1950, units=2, basis="whether the landlord lives in one of the two units would change the result")]},
    {"id": "SD-source-of-income", "zh": "San Diego 收入来源歧视禁令（没见过的页面）：只有“房东或家属住在同一栋楼并和租客共用浴室或厨房”的租约例外，这是单个租约的例外。",
     "packet": "D075-01", "jurisdiction": "San Diego, CA", "category": "screening_restrictions", "cite_re": r"98\.08|Source of Income|source of income",
     "held_out": True,
     "source": "San Diego Municipal Code 98.0804: the division does not apply to a tenancy in which the owner or a family member lives in the same building and shares a bathroom or kitchen with the tenant",
     "probes": [probe("covers the building; the shared-facilities exception is per tenancy", {"applies", "unknown"}, units=20, exact="applies",
                      basis="the only exception reaches a single tenancy where the owner shares a bathroom or kitchen, so it does not change building-level coverage"),
                probe("no unit count at all", {"applies", "unknown"}, exact="applies", basis="no condition depends on the unit count")]},
    {"id": "SA-algo", "zh": "Santa Ana 禁止算法定租（没见过的页面）：对所有楼适用；定义里排除的是历史汇总报告等，是行为层面的，不是楼的条件。",
     "packet": "D086-01", "jurisdiction": "Santa Ana, CA", "category": "algorithmic_rent_setting", "cite_re": r"8-37|NS-3090|Santa Ana",
     "held_out": True,
     "source": "Santa Ana Ordinance NS-3090 (adopted March 3, 2026, effective 30 days after adoption): bans algorithmic devices that use nonpublic competitor data to set rents; the carve-outs are about kinds of reports and software, not buildings",
     "probes": [probe("covers every building", {"applies"}, units=10, basis="no building-level condition; the carve-outs concern conduct"),
                probe("no unit count at all", {"applies"}, basis="no condition depends on the unit count")]},
    {"id": "MA-IP25-21", "zh": "麻州公投 25-21（限制涨租）：法院 2026-06-23 禁止把它放上 2026 年选票，应记为“已失败”。",
     "packet": "X101-01", "jurisdiction": "MA", "category": "rent_increase_limits", "cite_re": r"25-21|Initiative",
     "source": "AG listing: 25-21 An Initiative Petition to Protect Tenants by Limiting Rent Increases; SJC-13893 rescript 06/23/2026 enjoins placing it on the 2026 ballot",
     "lifecycle": "failed", "probes": []},
]
