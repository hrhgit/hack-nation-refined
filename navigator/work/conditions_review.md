# 条件核对表（第一阶段提取的条件对 500 个地址的影响）

条件由模型从原文读出，请抽查。最贵的错误是**误判豁免**：规则会在本该适用的地址上悄悄消失。
下面先列需要优先看的规则，再列全部规则。查询日期 2026-10-01。

## 优先核对（14 条）

### r-0136 — Berkeley, CA — rent_increase_limits — Berkeley Mun. Code ch. 13.76
- 状态：enacted；生效日期：2026-01-01；有效期至：2026
- 条件：covered if built on or before 1980-06；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): most condominiums; units with Section 202 or Section 811 subsidies, or project-based Section 8 in a project with a HUD-insured mortgage；note: The 2026 AGA may not adjust tenants' rents when their tenancy began on or after January 1, 2025 and their rents were set pursuant to the Costa-Hawkins Rental Housing Act.; Single-family home tenancies beginning on or after January 1, 1996; tenancy where the owner shares a kitchen or bath; tenancies started after Nov 7, 2018 where one unit is an ADU and either unit is owner-occupied.
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> New construction: units that were built and received a Certificate of Occupancy after June 1980** Partially Covered Yes No Yes Yes
- 原文：> Golden Duplex”: duplex that was owner-occupied on December 31, 1979, and currently has an owner living in one of the units Exempt No No No No
- 原文：> Unit where the owner shares a kitchen or bath with the tenant if the owner lived on the property at the time the tenancy started Exempt No No No No

### r-0125 — Boston, MA — screening_restrictions — Boston Fair Chance Tenant Selection Policy
- 状态：enacted；生效日期：2017-02；有效期至：—
- 条件：UNRESOLVED: Housing providers receiving DND funding or land, or with income-restricted units created under the BPDA Inclusionary Development Policy；note: Does not apply where there is a direct relationship between the conviction and the housing sought or an unreasonable risk of substantial harm, or to current criminal behavior.
- 地址结果（共 60 个在范围内）：unknown 60
- **注意：所有 60 个地址都是不确定**
- 原文：> Housing providers receiving Department of Neighborhood Development (DND) funding and/or land, or that have income restricted units created under the Boston Planning and Development Agency (BPDA) Inclusionary Development Policy will not impose a blanket policy that denies housing to anyone with arrests and or convictions.

### r-0024 — CA — just_cause_eviction — Cal. Civ. Code §1946.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：exempt if newer than 15 years；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): owner of separately alienable property who is not a real estate investment trust, corporation, or LLC with a corporate member; Housing restricted by deed or government agreement as affordable for very low, low or moderate income, or receiving housing subsidies；note: Tenant must have continuously and lawfully occupied for 12 months or more (24 months or more for one tenant if additional adult tenants are added earlier); tenant sharing bathroom or kitchen with the owner-occupant is exempt; transient hotel occupancy is exempt.
- 地址结果（共 250 个在范围内）：applies 147，omitted: a condition excludes it 5，unknown 98
- **注意：条件使它在 5 个地址上消失**
- 原文：> Housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome.
- 原文：> A property containing two separate dwelling units within a single structure in which the owner occupied one of the units as the owner’s principal place of residence at the beginning of the tenancy, so long as the owner continues in occupancy, and neither unit is an accessory dwelling unit or a junior accessory dwelling unit.
- 原文：> Residential real property, including a mobilehome, that is alienable separate from the title to any other dwelling unit, provided that both of the following apply:
- 关系 `yields_to_local`：> Residential real property subject to a local ordinance requiring just cause for termination of a residential tenancy adopted on or before September 1, 2019, in which case the local ordinance shall apply.
- 关系 `yields_to_local`：> Residential real property subject to a local ordinance requiring just cause for termination of a residential tenancy adopted or amended after September 1, 2019, that is more protective than this section, in which case the local ordinance shall apply.

### r-0022 — CA — rent_increase_limits — Cal. Civ. Code §1947.12
- 状态：enacted；生效日期：2024-04-01；有效期至：2030-01-01
- 条件：exempt if newer than 15 years；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): Affordable housing restricted by deed or government agreement for very low, low, or moderate income; Housing under local rent or price control restricting annual increases below the state cap; Separately alienable property (condo or single-family home) with a non-corporate owner and the required tenant notice; units restricted by a deed or recorded document limiting affordability to low- or moderate-income households; single-family homes and condominiums not owned by a trust, corporation or corporate LLC, where the landlord gave written notice；note: New tenancy with no holdover tenant: initial rate is not capped. Mobilehome tenancies are covered only for increases on or after February 18, 2021. The separate-property exemption requires the written notice to tenants.
- 地址结果（共 250 个在范围内）：applies 76，omitted: a condition excludes it 5，superseded 71，unknown 98
- **注意：条件使它在 5 个地址上消失**
- 原文：> Housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome.
- 原文：> A property containing two separate dwelling units within a single structure in which the owner occupied one of the units as the owner’s principal place of residence at the beginning of the tenancy, so long as the owner continues in occupancy, and neither unit is an accessory dwelling unit or a junior accessory dwelling unit.
- 原文：> Housing subject to rent or price control through a public entity’s valid exercise of its police power consistent with Chapter 2.7 (commencing with Section 1954.50) that restricts annual increases in the rental rate to an amount less than that provided in subdivision (a).
- 原文：> The JCO does not regulate rent increases, however, state law AB 1482, the California Tenant Protection Act of 2019 , may regulate the rent amount in buildings that are older than 15 years old.
- 关系 `yields_to_local`：> Housing subject to rent or price control through a public entity’s valid exercise of its police power consistent with Chapter 2.7 (commencing with Section 1954.50) that restricts annual increases in the rental rate to an amount less than that provided in subdivision (a).
- 关系 `yields_to_local`：> Units that are already subject to the City’s RSO.

### r-0079 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code ch. 260
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at least 5 units；exemption only if the owner filed (open question inside its reach): built on or after 1987-06-25 and built on or before 1992-06-25 and built within the last 30 years；UNRESOLVED: newly constructed dwellings with 25 or more units in a City-approved redevelopment area; buildings converted from nonpermanent dwelling use on or after October 1, 1983; multifamily dwellings certified vacant as of July 1, 1998；note, does not change the answer (kinds of housing the data cannot show): licensed hotels or motels and commercial and industrial space; low rent public housing developments；note: Any new dwelling or housing space being rented for the first time is exempt for the initial rental only.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> Dwellings with four or less housing spaces; provided, however, that this exemption shall be suspended for non-owner occupied dwellings with four or less housing spaces until the end of the state of emergency or six months from adoption of these amendments whichever comes first.
- 原文：> Licensed hotels or motels and commercial and industrial space.
- 原文：> Low rent public housing developments.
- 原文：> the provisions of this chapter which limit the periodic or regular increases in base rentals of dwelling units shall not apply to a newly constructed dwelling which is constructed between June 25, 1987, through June 25, 1992

### r-0210 — Los Angeles, CA — just_cause_eviction — Los Angeles Resident Protections Ordinance (L.A. Ordinances #188481, #188482)
- 状态：enacted；生效日期：2025-02-11；有效期至：—
- 条件：UNRESOLVED: only Protected Units demolished for the purpose of new construction；note: Applies to demolition of a Protected Unit that is occupied; lower income tenants get enhanced amounts.
- 地址结果（共 80 个在范围内）：unknown 80
- **注意：所有 80 个地址都是不确定**
- 原文：> The RPO only applies to Protected Units that will be demolished for the purpose of new construction.

### r-0170 — NJ — just_cause_eviction — N.J.A.C. 5:27-3.3
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at least 2 units；UNRESOLVED: buildings occupied by unrelated persons, without private kitchens and bathrooms
- 地址结果（共 140 个在范围内）：unknown 140
- **注意：所有 140 个地址都是不确定**
- 原文：> Any building having at least two (2) living units occupied by persons unrelated to each other without private kitchens and bathro oms is a rooming or boarding house if it does not meet one (1) of the exceptions in the Rooming and Boarding House Act (N.J.S.A. 55:13B-3).

### r-0053 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at most 3 units；owner-dependent, no size limit (unknown for every address)
- 地址结果（共 140 个在范围内）：omitted: a condition excludes it 86，unknown 54
- **注意：条件使它在 86 个地址上消失**
- 原文：> Tenants of landlord-occupied two- and three-family dwellings can be removed only when a court issues an order for eviction.

### r-0217 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.40 to -61.59
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: buildings converted or being converted in qualified counties, currently only Hudson County；note: Tenant must not be eligible for protected tenancy as a senior citizen or disabled person under the 1981 Act; must be in a qualified county.
- 地址结果（共 140 个在范围内）：unknown 140
- **注意：所有 140 个地址都是不确定**
- 原文：> At the present time, the only qualified county is Hudson County (N.J.A.C. 5:24-3.2(b)).

### r-0050 — NJ — rent_increase_limits — N.J.S.A. 2A:42-84.5
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：covered only if built within the last 30 years；date basis: construction_date
- 地址结果（共 140 个在范围内）：applies 4，omitted: a condition excludes it 30，unknown 106
- **注意：条件使它在 30 个地址上消失**
- 原文：> newly constructed multiple dwellings shall be exempt from any local rent control ordinances for a period of 30 years following completion of construction of the building

### r-0227 — Newark, NJ — rent_increase_limits — Newark Mun. Code ch. 19:2
- 状态：enacted；生效日期：2024-09-18；有效期至：—
- 条件：exemption only if the owner filed (open question inside its reach): built within the last 30 years；UNRESOLVED: Newly constructed multiple dwellings and vacant dwellings (subsections 19:2-18.1, 19:2-18.2); Dwellings vacant at least 18 months or already vacant, substantially rehabilitated; Substantially reconstructed or rehabilitated dwellings (rehab cost over 50% of fair market value)；note, does not change the answer (kinds of housing the data cannot show): All public housing; Units rehabilitated under Federal/State Rental Rehabilitation Programs receiving Section 8 subsidies or vouchers; Dwellings under a government agency contract regulating rent；note: A 10% rent increase is allowed only where the landlord rehabilitates a vacant apartment unit spending at least 12 months of actual monthly rent per unit and applies with a supporting affidavit.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> All multiple dwellings, as defined in subsection 19:2-2, are subject to Rent Control pursuant to this Title XIX Rent Control,
- 原文：> EXEMPTIONS — Shall mean dwellings to which this chapter shall not apply. Exempt dwellings include:
- 原文：> d. Newly constructed multiple dwellings and vacant dwellings as set forth in this chapter at Subsections 19:2-18.1 and 19:2-18.2, respectively;
- 原文：> The provisions of the Rent Control Ordinance, which limit the periodic or regular increases in base rentals of dwelling units shall not apply to newly constructed multiple dwellings for a period of time not to exceed the period of amortization of any initial mortgage loan obtained for the multiple dwelling, or for 30 years following completion of construction, whichever is less.

### r-0229 — Newark, NJ — screening_restrictions — Newark, N.J., Rev. Gen. Ords. ch. 2:31 et seq.
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units；note: Excludes rental of a room or rooms in an owner-occupied one-family dwelling.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> Of a single apartment or flat in a two family dwelling, the other occupancy unit of which is occupied by the owner as his/her residence or the household of his/her family at the time of such rental
- 原文：> Of a room or rooms to another person or persons by the owner or occupant of one-family dwelling occupied by him/her as his/her residence or the household of his/her family at the time of such rental.

### r-0095 — San Diego, CA — just_cause_eviction — San Diego Mun. Code §98.0704
- 状态：enacted；生效日期：2023-06-24；有效期至：—
- 条件：exempt if newer than 15 years；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): landlord-occupied single-family residence; deed-restricted or subsidized affordable housing for very low, low or moderate income; property alienable separate from title owned by a non-corporate landlord who gave the required notice；note: Tenancy is lawful occupancy for more than 30 days; excludes fixed-term leases of three months or less and a tenancy where the tenant shares bathroom or kitchen with the landlord.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome; and
- 原文：> single-family residence occupied by the landlord as the landlord’s principal place of residence, including both of the following:
- 原文：> a property containing two separate dwelling units within a single structure in which the landlord occupies one of the dwelling units as the landlord’s principal place of residence at the beginning of the tenancy, so long as the landlord continues in occupancy;

### r-0191 — San Francisco, CA — rent_increase_limits — S.F. Admin. Code ch. 37
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：covered if built on or before 1979-06-13；date basis: certificate_of_occupancy
- 地址结果（共 80 个在范围内）：applies 71，omitted: a condition excludes it 7，unknown 2
- **注意：条件使它在 7 个地址上消失**
- 手写补充条目 `sf-rent-cap-cutoff`（不是模型提取）：This includes tenancies in newly constructed rental units that first obtained a Certificate of Occupancy after June 13, 1979, tenancies that are eligible for a rent increase under the Costa-Hawkins Rental Housing Act, and some tenancies where the rent is regulated by another government agency. Parti；来源：starter-pack/participant-final-no-hour16 3/corpus/text/D079.txt; D080.txt: For rent-controlled units, the annual allowable increase amount effective March 1, 2026 through February 28, 2027 is 1.6%.

## 全部规则（97 条）

### r-0021 — Berkeley, CA — algorithmic_rent_setting — Berkeley Mun. Code ch. 13.63
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 40 个在范围内）：applies 40

### r-0135 — Berkeley, CA — application_screening_fees — Berkeley Mun. Code ch. 13.78
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Applies to owners or agents charging applicants a screening fee, and to fees charged to existing tenants for renewals or roommate changes.
- 地址结果（共 40 个在范围内）：applies 40

### r-0134 — Berkeley, CA — just_cause_eviction — Berkeley Mun. Code ch. 13.76
- 状态：enacted；生效日期：2026-01-01；有效期至：—
- 条件：owner exemption up to 2 units；note: Tenancy ended by an owner move-in eviction; Tenancy where the owner shares a kitchen or bath and lived on the property when the tenancy started; tenancies started after Nov 7, 2018 where one unit is an ADU and either unit is owner-occupied; university rental units such as dormitories.
- 地址结果（共 40 个在范围内）：applies 40
- 原文：> New construction: units that were built and received a Certificate of Occupancy after June 1980** Partially Covered Yes No Yes Yes
- 原文：> University rental units such as dormitories. Exempt No No No No

### r-0205 — Berkeley, CA — just_cause_eviction — Ellis Implementation Ordinance
- 状态：enacted；生效日期：2026-01-01；有效期至：—
- 条件：note: Tenancy ended by an Ellis Act eviction
- 地址结果（共 40 个在范围内）：applies 40

### r-0136 — Berkeley, CA — rent_increase_limits — Berkeley Mun. Code ch. 13.76
- 状态：enacted；生效日期：2026-01-01；有效期至：2026
- 条件：covered if built on or before 1980-06；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): most condominiums; units with Section 202 or Section 811 subsidies, or project-based Section 8 in a project with a HUD-insured mortgage；note: The 2026 AGA may not adjust tenants' rents when their tenancy began on or after January 1, 2025 and their rents were set pursuant to the Costa-Hawkins Rental Housing Act.; Single-family home tenancies beginning on or after January 1, 1996; tenancy where the owner shares a kitchen or bath; tenancies started after Nov 7, 2018 where one unit is an ADU and either unit is owner-occupied.
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> New construction: units that were built and received a Certificate of Occupancy after June 1980** Partially Covered Yes No Yes Yes
- 原文：> Golden Duplex”: duplex that was owner-occupied on December 31, 1979, and currently has an owner living in one of the units Exempt No No No No
- 原文：> Unit where the owner shares a kitchen or bath with the tenant if the owner lived on the property at the time the tenancy started Exempt No No No No

### r-0020 — Berkeley, CA — screening_restrictions — Berkeley Mun. Code ch. 13.106
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 3 units；note, does not change the answer (kinds of housing the data cannot show): public housing and Section 8 properties (limited exemptions)；note: Lifetime sex offenders; units under a rental agreement allowing owners to move back under BMC 13.76.130 A.9; units occupied by existing tenants seeking to sublet or add/replace roommates.
- 地址结果（共 40 个在范围内）：applies 40
- 原文：> Owner-occupied properties (between 1-3 units) in which an owner of record resides in one of the units as their primary residence
- 原文：> Public housing/Section 8 properties limited exemptions

### r-0137 — Berkeley, CA — security_deposits — Berkeley Mun. Code ch. 13.76
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units；note: Tenancy where the owner shares a kitchen or bath and lived on the property when the tenancy started; tenancies started after Nov 7, 2018 where one unit is an ADU and either unit is owner-occupied; university rental units such as dormitories.
- 地址结果（共 40 个在范围内）：applies 40
- 原文：> Single-family home with a tenancy that began on or after January 1, 1996** Partially Covered Yes No Yes Yes
- 原文：> University rental units such as dormitories. Exempt No No No No

### r-0074 — Boston, MA — just_cause_eviction — Boston Mun. Code §10-11.7
- 状态：enacted；生效日期：2020-11-06；有效期至：—
- 条件：note: Applies when a landlord is planning to end a tenancy agreement.
- 地址结果（共 60 个在范围内）：applies 60

### r-0125 — Boston, MA — screening_restrictions — Boston Fair Chance Tenant Selection Policy
- 状态：enacted；生效日期：2017-02；有效期至：—
- 条件：UNRESOLVED: Housing providers receiving DND funding or land, or with income-restricted units created under the BPDA Inclusionary Development Policy；note: Does not apply where there is a direct relationship between the conviction and the housing sought or an unreasonable risk of substantial harm, or to current criminal behavior.
- 地址结果（共 60 个在范围内）：unknown 60
- **注意：所有 60 个地址都是不确定**
- 原文：> Housing providers receiving Department of Neighborhood Development (DND) funding and/or land, or that have income restricted units created under the Boston Planning and Development Agency (BPDA) Inclusionary Development Policy will not impose a blanket policy that denies housing to anyone with arrests and or convictions.

### r-0126 — Boston, MA — screening_restrictions — Boston Fair Housing Regulations
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 60 个在范围内）：applies 60
- 原文：> In the City of Boston, it’s illegal to discriminate when renting, buying, selling, or securing financing for any housing.

### r-0034 — CA — algorithmic_rent_setting — AB 325 (Cal. Bus. & Prof. Code §16729)
- 状态：enacted；生效日期：2026-01-01；有效期至：—
- 条件：无
- 地址结果（共 250 个在范围内）：applies 250
- 原文：> It shall be unlawful for a person to use or distribute a common pricing algorithm as part of a contract, combination in the form of a trust, or conspiracy to restrain trade or commerce in violation of this chapter.

### r-0005 — CA — application_screening_fees — Cal. Civ. Code §1950.6
- 状态：enacted；生效日期：2026-01-01；有效期至：2026
- 条件：note: Duty attaches when a landlord charges an application screening fee to an applicant.; Applies when a landlord charges a screening fee to a prospective tenant.
- 地址结果（共 250 个在范围内）：applies 250

### r-0024 — CA — just_cause_eviction — Cal. Civ. Code §1946.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：exempt if newer than 15 years；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): owner of separately alienable property who is not a real estate investment trust, corporation, or LLC with a corporate member; Housing restricted by deed or government agreement as affordable for very low, low or moderate income, or receiving housing subsidies；note: Tenant must have continuously and lawfully occupied for 12 months or more (24 months or more for one tenant if additional adult tenants are added earlier); tenant sharing bathroom or kitchen with the owner-occupant is exempt; transient hotel occupancy is exempt.
- 地址结果（共 250 个在范围内）：applies 147，omitted: a condition excludes it 5，unknown 98
- **注意：条件使它在 5 个地址上消失**
- 原文：> Housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome.
- 原文：> A property containing two separate dwelling units within a single structure in which the owner occupied one of the units as the owner’s principal place of residence at the beginning of the tenancy, so long as the owner continues in occupancy, and neither unit is an accessory dwelling unit or a junior accessory dwelling unit.
- 原文：> Residential real property, including a mobilehome, that is alienable separate from the title to any other dwelling unit, provided that both of the following apply:
- 关系 `yields_to_local`：> Residential real property subject to a local ordinance requiring just cause for termination of a residential tenancy adopted on or before September 1, 2019, in which case the local ordinance shall apply.
- 关系 `yields_to_local`：> Residential real property subject to a local ordinance requiring just cause for termination of a residential tenancy adopted or amended after September 1, 2019, that is more protective than this section, in which case the local ordinance shall apply.

### r-0025 — CA — just_cause_eviction — Cal. Civ. Code §1947.9
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：note: Applies to temporary displacement of less than 20 days.
- 地址结果（共 250 个在范围内）：applies 250

### r-0022 — CA — rent_increase_limits — Cal. Civ. Code §1947.12
- 状态：enacted；生效日期：2024-04-01；有效期至：2030-01-01
- 条件：exempt if newer than 15 years；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): Affordable housing restricted by deed or government agreement for very low, low, or moderate income; Housing under local rent or price control restricting annual increases below the state cap; Separately alienable property (condo or single-family home) with a non-corporate owner and the required tenant notice; units restricted by a deed or recorded document limiting affordability to low- or moderate-income households; single-family homes and condominiums not owned by a trust, corporation or corporate LLC, where the landlord gave written notice；note: New tenancy with no holdover tenant: initial rate is not capped. Mobilehome tenancies are covered only for increases on or after February 18, 2021. The separate-property exemption requires the written notice to tenants.
- 地址结果（共 250 个在范围内）：applies 76，omitted: a condition excludes it 5，superseded 71，unknown 98
- **注意：条件使它在 5 个地址上消失**
- 原文：> Housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome.
- 原文：> A property containing two separate dwelling units within a single structure in which the owner occupied one of the units as the owner’s principal place of residence at the beginning of the tenancy, so long as the owner continues in occupancy, and neither unit is an accessory dwelling unit or a junior accessory dwelling unit.
- 原文：> Housing subject to rent or price control through a public entity’s valid exercise of its police power consistent with Chapter 2.7 (commencing with Section 1954.50) that restricts annual increases in the rental rate to an amount less than that provided in subdivision (a).
- 原文：> The JCO does not regulate rent increases, however, state law AB 1482, the California Tenant Protection Act of 2019 , may regulate the rent amount in buildings that are older than 15 years old.
- 关系 `yields_to_local`：> Housing subject to rent or price control through a public entity’s valid exercise of its police power consistent with Chapter 2.7 (commencing with Section 1954.50) that restricts annual increases in the rental rate to an amount less than that provided in subdivision (a).
- 关系 `yields_to_local`：> Units that are already subject to the City’s RSO.

### r-0030 — CA — screening_restrictions — Cal. Civ. Code §1950.6
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Applies when a prospective tenant provides a reusable screening report.
- 地址结果（共 250 个在范围内）：applies 250

### r-0031 — CA — screening_restrictions — Cal. Gov. Code §12955
- 状态：enacted；生效日期：2024-01-01；有效期至：—
- 条件：note: Applies to each rental application and tenancy; the credit-history and rent-share limits apply where there is a government rent subsidy, such as a Section 8 voucher.
- 地址结果（共 250 个在范围内）：applies 250

### r-0206 — CA — screening_restrictions — California Fair Employment and Housing Act (FEHA)
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: An owner occupying the home and renting to one additional person may exclude applicants based on protected characteristics.
- 地址结果（共 250 个在范围内）：applies 250

### r-0001 — CA — security_deposits — AB 12
- 状态：enacted；生效日期：2024-07-01；有效期至：—
- 条件：owner exemption up to 4 units
- 地址结果（共 250 个在范围内）：applies 250
- 原文：> Starting July 1, 2024, landlords who own only two rental properties with no more than four residential units total can charge up to two months' rent for furnished and unfurnished units if ownership is held by a natural person, family trust, or limited liability company (LLC) where all members are natural persons

### r-0029 — CA — security_deposits — Cal. Civ. Code §1950.5
- 状态：enacted；生效日期：2024-07-01；有效期至：—
- 条件：note: Does not apply to security collected or demanded before July 1, 2024.
- 地址结果（共 250 个在范围内）：applies 250

### r-0207 — Cambridge, MA — just_cause_eviction — Cambridge Mun. Code ch. 8.71
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50

### r-0078 — Cambridge, MA — screening_restrictions — Cambridge Mun. Code ch. 14.04
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units
- 地址结果（共 50 个在范围内）：applies 50
- 原文：> NOTE: there is an exemption for 2-family dwellings, when the owner lives there

### r-0148 — Hoboken, NJ — algorithmic_rent_setting — Hoboken Mun. Code §158-2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 40 个在范围内）：applies 40

### r-0147 — Hoboken, NJ — rent_increase_limits — Hoboken Mun. Code §158-1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Rent increase of more than 10% on renewal of a lease with a current tenant year over year
- 地址结果（共 40 个在范围内）：applies 40

### r-0208 — Hoboken, NJ — rent_increase_limits — Hoboken, N.J., Code ch. 155
- 状态：enacted；生效日期：2023-02-01；有效期至：2022-05-07
- 条件：exemption only if the owner filed (open question inside its reach): built after 1987-06-25 and built within the last 30 years；UNRESOLVED: dwellings newly constructed, as defined in the chapter; buildings completely vacant since January 1, 1984; condo/co-op units owned and occupied by a bona fide owner-occupant for two years; newly constructed dwellings, eligibility determined by the Regulation Officer; buildings completely vacant since January 1, 1984；note, does not change the answer (kinds of housing the data cannot show): government agencies (state or federal)；note: For a periodic tenant or a lease term under one year, the cap is 5% or the CPI differential and no more than one increase in any 12-month period.; Newly constructed dwellings and buildings vacant since January 1, 1984 are exempt only for the initial rent or lease; commercial units in mixed-use buildings are exempt while residential units remain covered.; Decontrol is not available where the court order dispossesses a tenant for holding over after the lease term.; Decontrol applies only where the owner vacates the unit and offers it for rental.
- 地址结果（共 40 个在范围内）：omitted: outside its valid period 40
- 原文：> The Regulation Officer shall make all determinations regarding the eligibility of a newly constructed dwelling for an exemption as defined above.
- 原文：> The Rent Regulation Officer shall make all determinations regarding the eligibility of a building completely vacant since January 1, 1984, for an exemption as defined above.
- 原文：> This chapter shall apply to all dwelling units as defined in § 155-1 above, except that the following shall be exempt:
- 原文：> Housing owned and operated by other government agencies, such as the state or federal government.

### r-0149 — Jersey City, NJ — algorithmic_rent_setting — Jersey City Mun. Code §218-12
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Exempts an owner's actions related exclusively to properties controlled by the same owner; licensed real estate agents operating under state regulations are not service providers.; Duty attaches with any lease or written notice of rent increase for a residential dwelling unit.
- 地址结果（共 50 个在范围内）：applies 50

### r-0079 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code ch. 260
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at least 5 units；exemption only if the owner filed (open question inside its reach): built on or after 1987-06-25 and built on or before 1992-06-25 and built within the last 30 years；UNRESOLVED: newly constructed dwellings with 25 or more units in a City-approved redevelopment area; buildings converted from nonpermanent dwelling use on or after October 1, 1983; multifamily dwellings certified vacant as of July 1, 1998；note, does not change the answer (kinds of housing the data cannot show): licensed hotels or motels and commercial and industrial space; low rent public housing developments；note: Any new dwelling or housing space being rented for the first time is exempt for the initial rental only.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> Dwellings with four or less housing spaces; provided, however, that this exemption shall be suspended for non-owner occupied dwellings with four or less housing spaces until the end of the state of emergency or six months from adoption of these amendments whichever comes first.
- 原文：> Licensed hotels or motels and commercial and industrial space.
- 原文：> Low rent public housing developments.
- 原文：> the provisions of this chapter which limit the periodic or regular increases in base rentals of dwelling units shall not apply to a newly constructed dwelling which is constructed between June 25, 1987, through June 25, 1992

### r-0094 — Los Angeles, CA — algorithmic_rent_setting — Los Angeles City Council Motion, C.F. 24-1031
- 状态：pending_bill；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 80 个在范围内）：pending 80

### r-0085 — Los Angeles, CA — just_cause_eviction — L.A.M.C. §151.09
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：covered if built_on_or_before=1978-10-01, or also (open question outside the limit): replacement units under LAMC Section 151.28
- 地址结果（共 80 个在范围内）：applies 47，unknown 33
- 原文：> Generally, the RSO applies to rental properties that were first built on or before October 1, 1978

### r-0087 — Los Angeles, CA — just_cause_eviction — L.A.M.C. §165.06
- 状态：enacted；生效日期：2026-07-01；有效期至：2027-06-30
- 条件：note: Paid per unit, not per tenant; RPO Chart B amounts only for low, very low and extremely low income households displaced by new construction.
- 地址结果（共 80 个在范围内）：applies 80

### r-0159 — Los Angeles, CA — just_cause_eviction — Los Angeles Just Cause Ordinance (L.A.M.C. §165.00 et seq.)
- 状态：enacted；生效日期：2026-07-01；有效期至：2027-06-30
- 条件：note, does not change the answer (kinds of housing the data cannot show): residential properties regulated by the City's Rent Stabilization Ordinance (RSO); owned by HACLA or the government；note: Amount depends on tenant status (qualified, eligible or low income) and length of tenancy; applies on a no-fault termination.; Tenant has lived in the same unit at least six months or their original lease expired, whichever comes first.
- 地址结果（共 80 个在范围内）：applies 80
- 原文：> All tenant not- at-fault evictions require payment of relocation assistance and the filing of a Declaration of Intent to Evict form with the Los Angeles Housing Department (LAHD) before evicting tenants from units covered by the Rent Stabilization Ordinance (RSO) or the Just Cause Ordinance (JCO).
- 原文：> The JCO covers most residential properties in the City of Los Angeles that are not regulated by the City’s Rent Stabilization Ordinance (RSO).
- 原文：> In order to apply to a tenancy, it requires that the tenant either has lived in the same unit for at least six months or that their original lease expired, whichever comes first.
- 原文：> some properties owned by HACLA or the government

### r-0210 — Los Angeles, CA — just_cause_eviction — Los Angeles Resident Protections Ordinance (L.A. Ordinances #188481, #188482)
- 状态：enacted；生效日期：2025-02-11；有效期至：—
- 条件：UNRESOLVED: only Protected Units demolished for the purpose of new construction；note: Applies to demolition of a Protected Unit that is occupied; lower income tenants get enhanced amounts.
- 地址结果（共 80 个在范围内）：unknown 80
- **注意：所有 80 个地址都是不确定**
- 原文：> The RPO only applies to Protected Units that will be demolished for the purpose of new construction.

### r-0154 — Los Angeles, CA — rent_increase_limits — Los Angeles Rent Stabilization Ordinance (L.A.M.C. §151.00 et seq.)
- 状态：enacted；生效日期：2026-02-02；有效期至：2026-06-30
- 条件：covered if built_on_or_before=1978-10-01, or also (open question outside the limit): replacement units under LAMC Section 151.28；note: Rent amount is not regulated for condominium or townhome tenancies that commenced after December 31, 1995.
- 地址结果（共 80 个在范围内）：omitted: outside its valid period 80
- 原文：> Generally, the RSO applies to rental properties that were first built on or before October 1, 1978
- 原文：> Condominium (Rent amount is not regulated for tenancies that commenced after December 31, 1995)

### r-0226 — Los Angeles, CA — screening_restrictions — L.A.M.C. §45.42
- 状态：enacted；生效日期：2018-11-25；有效期至：—
- 条件：无
- 地址结果（共 80 个在范围内）：applies 80

### r-0150 — Los Angeles, CA — screening_restrictions — Los Angeles Mun. Code §45.67
- 状态：enacted；生效日期：2020-01-01；有效期至：—
- 条件：无
- 地址结果（共 80 个在范围内）：applies 80
- 原文：> duplexes, condominiums, and single family residences in the City of Los Angeles, rented or offered for rent for living or dwelling purposes

### r-0158 — Los Angeles, CA — security_deposits — L.A.M.C. §151.06.02
- 状态：enacted；生效日期：2003-01-01；有效期至：—
- 条件：note: Interest is owed only on security deposits held for at least one year.
- 地址结果（共 80 个在范围内）：applies 80

### r-0046 — MA — algorithmic_rent_setting — H.5222
- 状态：pending_bill；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：pending 110

### r-0047 — MA — algorithmic_rent_setting — S.2983
- 状态：pending_bill；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：pending 110

### r-0212 — MA — application_screening_fees — G.L. c. 112, §87DDD 1/2
- 状态：enacted；生效日期：2025-08-01；有效期至：—
- 条件：note: Fee only payable by the party (lessor or tenant) who originally engaged the broker; broker contracts solely with tenant or solely with landlord.
- 地址结果（共 110 个在范围内）：applies 110

### r-0044 — MA — application_screening_fees — G.L. c. 186, §15B
- 状态：enacted；生效日期：2025-08-01；有效期至：—
- 条件：note: The cap applies to amounts a lessor or its agent requires a tenant or applicant to pay at or prior to the commencement of a tenancy.
- 地址结果（共 110 个在范围内）：applies 110

### r-0037 — MA — just_cause_eviction — G.L. c. 186, §11
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Tenancies under a written lease; relief where nonpayment was caused by a federal, state or municipal failure or delay in mailing a rental or subsistence payment, check or voucher.
- 地址结果（共 110 个在范围内）：applies 110

### r-0038 — MA — just_cause_eviction — G.L. c. 186, §12
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110

### r-0039 — MA — just_cause_eviction — G.L. c. 186, §18
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Any tenancy of residential premises
- 地址结果（共 110 个在范围内）：applies 110
- 原文：> Any person or agent thereof who threatens to or takes reprisals against any tenant of residential premises

### r-0041 — MA — just_cause_eviction — H.3744
- 状态：failed；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：omitted: failed measure 110

### r-0040 — MA — just_cause_eviction — Mass. Gen. Laws ch. 186, §31
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110

### r-0035 — MA — rent_increase_limits — G.L. c. 40P, §4
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Limits listed for local opt-in regulation: units of an owner of fewer than ten rental units, and units with fair market rent above $400, may not be regulated.
- 地址结果（共 110 个在范围内）：applies 110
- 关系 `preempts_local`：> No city or town may enact, maintain or enforce rent control of any kind, except that any city or town that accepts this chapter may adopt rent control regulation that provides:

### r-0036 — MA — rent_increase_limits — H.3744
- 状态：failed；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：omitted: failed measure 110

### r-0204 — MA — rent_increase_limits — Initiative Petition 25-21
- 状态：failed；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：omitted: failed measure 110

### r-0162 — MA — screening_restrictions — 803 CMR 5.00
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: For subsidized housing applicants, screening only as provided by state and federal law; CORI only as the final step.
- 地址结果（共 110 个在范围内）：applies 110
- 原文：> 803 CMR 5.00 applies to landlords, real estate agents, public housing authorities, and property management companies that request CORI for the purpose of screening applicants for the rental or lease of housing.

### r-0213 — MA — screening_restrictions — 803 CMR 5.16
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110
- 原文：> Any landlord, property management company, real estate agent, or public housing authority that obtains CORI from DCJIS shall be subject to audit as described in 803 CMR 2.23: Audits by DCJIS.

### r-0045 — MA — screening_restrictions — G.L. c. 151B, §4
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110
- 原文：> For any person furnishing credit, services or rental accommodations to discriminate against any individual who is a recipient of federal, state, or local public assistance, including medical assistance, or who is a tenant receiving federal, state, or local housing subsidies, including rental assistance or rental supplements, because the individual is such a recipient, or because of any requirement of such public assi

### r-0163 — MA — screening_restrictions — G.L. c. 186, §15B
- 状态：enacted；生效日期：2025-08-01；有效期至：—
- 条件：note: Applies only where a lessor offers, and a tenant agrees to, a fee in lieu of a security deposit.
- 地址结果（共 110 个在范围内）：applies 110

### r-0042 — MA — security_deposits — G.L. c. 186, §15B
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note, does not change the answer (kinds of housing the data cannot show): city or town acquiring title under chapter 60, or a foreclosing mortgagee or financial-institution mortgagee in possession；note: Section does not apply to a lease, rental, occupancy or tenancy of 100 days or less for a vacation or recreational purpose.
- 地址结果（共 110 个在范围内）：applies 110
- 原文：> The liability imposed by this subsection shall not apply to a city or town which acquires title to property pursuant to chapter sixty or to a foreclosing mortgagee or a mortgagee in possession which is a financial institution chartered by the commonwealth or by the United States.
- 原文：> The provisions of this section shall not apply to any lease, rental, occupancy or tenancy of one hundred days or less in duration which lease or rental is for a vacation or recreational purpose.

### r-0218 — NJ — algorithmic_rent_setting — P.L. 2026, c. 43 (N.J.S.A. 56:9-20)
- 状态：enacted；生效日期：2027-07-01；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：not_yet_effective 140
- 关系 `preempts_local`：> A municipality shall be prohibited from enacting an ordinance that conflicts with this act.

### r-0065 — NJ — application_screening_fees — N.J.S.A. 46:8-18.1
- 状态：enacted；生效日期：2026-05-01；有效期至：—
- 条件：at least 3 units；note: A licensee of the New Jersey Real Estate Commission who is not the landlord of the property.
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> The requirements of subsection a. of this section shall not apply to: (1) a dwelling unit located in a one-family or two-family dwelling that is offered for rent; or (2) a licensee of the New Jersey Real Estate Commission, unless the licensee is the landlord of the residential rental property.

### r-0166 — NJ — application_screening_fees — P.L. 2021, c. 110
- 状态：enacted；生效日期：2022-01-01；有效期至：—
- 条件：owner exemption up to 4 units
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> “Rental dwelling unit” means a dwelling unit offered for rent by a housing provider for residential purposes, other than a dwelling unit in an owner-occupied premises of not more than four dwelling units.

### r-0170 — NJ — just_cause_eviction — N.J.A.C. 5:27-3.3
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at least 2 units；UNRESOLVED: buildings occupied by unrelated persons, without private kitchens and bathrooms
- 地址结果（共 140 个在范围内）：unknown 140
- **注意：所有 140 个地址都是不确定**
- 原文：> Any building having at least two (2) living units occupied by persons unrelated to each other without private kitchens and bathro oms is a rooming or boarding house if it does not meet one (1) of the exceptions in the Rooming and Boarding House Act (N.J.S.A. 55:13B-3).

### r-0052 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units；note, does not change the answer (kinds of housing the data cannot show): hotel, motel or other guest house, or part thereof, rented to a transient guest or seasonal tenant；note: Units held in trust for, or permanently occupied by, an immediate family member of the owner or trust grantor who has a developmental disability
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> owner-occupied premises with not more than two rental units or a hotel, motel or other guest house or part thereof rented to a transient guest or seasonal tenant;
- 原文：> a dwelling unit which is held in trust on behalf of a member of the immediate family of the person or persons establishing the trust, provided that the member of the immediate family on whose behalf the trust is established permanently occupies the unit;
- 原文：> a dwelling unit which is permanently occupied by a member of the immediate family of the owner of that unit, provided, however, that exception (2) or (3) shall apply only in cases in which the member of the immediate family has a developmental disability
- 原文：> No residential landlord may evict or fail to renew a lease, whether it is a written or an oral lease without good cause.

### r-0053 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at most 3 units；owner-dependent, no size limit (unknown for every address)
- 地址结果（共 140 个在范围内）：omitted: a condition excludes it 86，unknown 54
- **注意：条件使它在 86 个地址上消失**
- 原文：> Tenants of landlord-occupied two- and three-family dwellings can be removed only when a court issues an order for eviction.

### r-0216 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.22 to -61.39
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Tenant must be 62+ before the conversion recording, or permanently disabled, or a qualifying disabled veteran; must have lived in the building at least one year before conversion; family income limits apply.
- 地址结果（共 140 个在范围内）：applies 140

### r-0217 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.40 to -61.59
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: buildings converted or being converted in qualified counties, currently only Hudson County；note: Tenant must not be eligible for protected tenancy as a senior citizen or disabled person under the 1981 Act; must be in a qualified county.
- 地址结果（共 140 个在范围内）：unknown 140
- **注意：所有 140 个地址都是不确定**
- 原文：> At the present time, the only qualified county is Hudson County (N.J.A.C. 5:24-3.2(b)).

### r-0055 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.6
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Applies when the landlord evicted the tenant on a stated owner-occupancy or demolition/withdrawal-from-residential-use ground.
- 地址结果（共 140 个在范围内）：applies 140

### r-0168 — NJ — just_cause_eviction — N.J.S.A. 2A:39-1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：applies 140

### r-0056 — NJ — just_cause_eviction — N.J.S.A. 2A:42-10.10
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 3 units
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> The law against reprisal applies to all rental properties used for dwelling purposes, including mobile homes, except owner-occupied two- or three-family dwellings.

### r-0172 — NJ — just_cause_eviction — N.J.S.A. 2A:50-69
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：applies 140

### r-0165 — NJ — just_cause_eviction — P.L. 2021, c. 110
- 状态：enacted；生效日期：2022-01-01；有效期至：—
- 条件：owner exemption up to 4 units；note: Eviction of a former applicant placed in the unit by a director's order later overturned on the housing provider's successful appeal.
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> “Rental dwelling unit” means a dwelling unit offered for rent by a housing provider for residential purposes, other than a dwelling unit in an owner-occupied premises of not more than four dwelling units.

### r-0048 — NJ — rent_increase_limits — N.J.S.A. 2A:18-61.1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：applies 140

### r-0049 — NJ — rent_increase_limits — N.J.S.A. 2A:18-61.31
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：applies 140
- 原文：> This prohibition applies to all tenants in the building regardless of whether they are eligible for protected tenancy as senior citizens or disabled persons.

### r-0050 — NJ — rent_increase_limits — N.J.S.A. 2A:42-84.5
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：covered only if built within the last 30 years；date basis: construction_date
- 地址结果（共 140 个在范围内）：applies 4，omitted: a condition excludes it 30，unknown 106
- **注意：条件使它在 30 个地址上消失**
- 原文：> newly constructed multiple dwellings shall be exempt from any local rent control ordinances for a period of 30 years following completion of construction of the building

### r-0067 — NJ — screening_restrictions — N.J.S.A. 10:5-12
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units；note: rooms in an owner- or resident-occupied single home
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> For any person, including, but not limited to, any owner, lessee, sublessee, assignee, or managing agent of, or other person having the right of ownership or possession of or the right to sell, rent, lease, assign, or sublease any real property or part or portion thereof, or any agent or employee of any of these
- 原文：> The law applies to all landlord -tenant relationships, except those involving two -family owner occupied dwellings, rooms in an owner or resident -occupied single home, and residences planned exclusively for and occupied by one sex, i.e. YMCA and age -restricted housing, as it pertains to familial status (N.J.S.A. 10:5-5(n)).

### r-0215 — NJ — screening_restrictions — New Jersey Law Against Discrimination (LAD)
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Rental of a single apartment or flat in an owner-occupied two-family dwelling; rental of a room in an owner-occupied one-family dwelling; preference given by a religious organization to persons of the same religion.
- 地址结果（共 140 个在范围内）：applies 140

### r-0167 — NJ — screening_restrictions — P.L. 2021, c. 110
- 状态：enacted；生效日期：2022-01-01；有效期至：—
- 条件：owner exemption up to 4 units
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> “Rental dwelling unit” means a dwelling unit offered for rent by a housing provider for residential purposes, other than a dwelling unit in an owner-occupied premises of not more than four dwelling units.

### r-0059 — NJ — security_deposits — N.J.S.A. 46:8-21
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：applies 140

### r-0061 — NJ — security_deposits — N.J.S.A. 46:8-21.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Security deposits for seasonal use or rental of not more than 125 consecutive days are excluded from the deposit-account provisions.
- 地址结果（共 140 个在范围内）：applies 140
- 原文：> as a security for the use or rental of real property used for dwelling purposes

### r-0164 — NJ — security_deposits — N.J.S.A. 46:8-26
- 状态：enacted；生效日期：1979-02-22；有效期至：—
- 条件：owner exemption up to 2 units；exemption only if the owner filed (open question inside its reach): at most 2 units；note: Exemption applies only where the tenant has failed to provide 30 days written notice to the landlord invoking the provisions of this act.
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> The provisions of this act shall apply to all rental premises or units used for dwelling purposes except owner-occupied premises with not more than two rental units where the tenant has failed to provide 30 days written notice to the landlord invoking the provisions of this act.

### r-0064 — NJ — security_deposits — N.J.S.A. 46:8-9.6
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Applies only where a tenant terminates the lease early under the Safe Housing Act; does not apply to transient or seasonal rentals.
- 地址结果（共 140 个在范围内）：applies 140

### r-0228 — Newark, NJ — just_cause_eviction — Newark Rent Control Ordinance ch. 19:2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Landlord's eviction action is a reprisal for the tenant's efforts to secure or enforce rights under the chapter.; Tenant is a senior citizen or disabled tenant; the eviction results from a condominium or cooperative conversion.
- 地址结果（共 50 个在范围内）：applies 50

### r-0227 — Newark, NJ — rent_increase_limits — Newark Mun. Code ch. 19:2
- 状态：enacted；生效日期：2024-09-18；有效期至：—
- 条件：exemption only if the owner filed (open question inside its reach): built within the last 30 years；UNRESOLVED: Newly constructed multiple dwellings and vacant dwellings (subsections 19:2-18.1, 19:2-18.2); Dwellings vacant at least 18 months or already vacant, substantially rehabilitated; Substantially reconstructed or rehabilitated dwellings (rehab cost over 50% of fair market value)；note, does not change the answer (kinds of housing the data cannot show): All public housing; Units rehabilitated under Federal/State Rental Rehabilitation Programs receiving Section 8 subsidies or vouchers; Dwellings under a government agency contract regulating rent；note: A 10% rent increase is allowed only where the landlord rehabilitates a vacant apartment unit spending at least 12 months of actual monthly rent per unit and applies with a supporting affidavit.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> All multiple dwellings, as defined in subsection 19:2-2, are subject to Rent Control pursuant to this Title XIX Rent Control,
- 原文：> EXEMPTIONS — Shall mean dwellings to which this chapter shall not apply. Exempt dwellings include:
- 原文：> d. Newly constructed multiple dwellings and vacant dwellings as set forth in this chapter at Subsections 19:2-18.1 and 19:2-18.2, respectively;
- 原文：> The provisions of the Rent Control Ordinance, which limit the periodic or regular increases in base rentals of dwelling units shall not apply to newly constructed multiple dwellings for a period of time not to exceed the period of amortization of any initial mortgage loan obtained for the multiple dwelling, or for 30 years following completion of construction, whichever is less.

### r-0185 — Newark, NJ — rent_increase_limits — Newark, N.J., Code §2:10-11
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50

### r-0229 — Newark, NJ — screening_restrictions — Newark, N.J., Rev. Gen. Ords. ch. 2:31 et seq.
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units；note: Excludes rental of a room or rooms in an owner-occupied one-family dwelling.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> Of a single apartment or flat in a two family dwelling, the other occupancy unit of which is occupied by the owner as his/her residence or the household of his/her family at the time of such rental
- 原文：> Of a room or rooms to another person or persons by the owner or occupant of one-family dwelling occupied by him/her as his/her residence or the household of his/her family at the time of such rental.

### r-0188 — San Diego, CA — algorithmic_rent_setting — San Diego Mun. Code §§98.1101–98.1104
- 状态：enacted；生效日期：2025-06-21；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50

### r-0095 — San Diego, CA — just_cause_eviction — San Diego Mun. Code §98.0704
- 状态：enacted；生效日期：2023-06-24；有效期至：—
- 条件：exempt if newer than 15 years；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): landlord-occupied single-family residence; deed-restricted or subsidized affordable housing for very low, low or moderate income; property alienable separate from title owned by a non-corporate landlord who gave the required notice；note: Tenancy is lawful occupancy for more than 30 days; excludes fixed-term leases of three months or less and a tenancy where the tenant shares bathroom or kitchen with the landlord.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome; and
- 原文：> single-family residence occupied by the landlord as the landlord’s principal place of residence, including both of the following:
- 原文：> a property containing two separate dwelling units within a single structure in which the landlord occupies one of the dwelling units as the landlord’s principal place of residence at the beginning of the tenancy, so long as the landlord continues in occupancy;

### r-0097 — San Diego, CA — just_cause_eviction — San Diego Mun. Code §98.0706
- 状态：enacted；生效日期：2023-06-24；有效期至：—
- 条件：note: Relocation is three months' rent for a senior or disabled tenant and two months otherwise; the duty triggers on a no-fault just cause termination.
- 地址结果（共 50 个在范围内）：applies 50

### r-0190 — San Diego, CA — screening_restrictions — San Diego Mun. Code §98.0803
- 状态：enacted；生效日期：2018-10-18；有效期至：—
- 条件：note: Applies to any tenancy except where the owner or a family member resides in the same residential building and shares a bathroom or kitchen with the tenant or prospective tenant.
- 地址结果（共 50 个在范围内）：applies 50

### r-0109 — San Francisco, CA — algorithmic_rent_setting — S.F. Admin. Code §37.10C
- 状态：enacted；生效日期：2024-10-14；有效期至：—
- 条件：无
- 地址结果（共 80 个在范围内）：applies 80
- 原文：> The law prohibits the sale or use of algorithmic devices to set rents or manage occupancy levels for residential units in San Francisco.

### r-0194 — San Francisco, CA — just_cause_eviction — S.F. Admin. Code ch. 37
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：note: Amounts depend on the date the eviction notice is served and on whether the tenant is 62 or older or disabled.; Applies to evictions based on the stated no-fault grounds and to Ellis Act evictions.
- 地址结果（共 80 个在范围内）：applies 80
- 原文：> Relocation payments for tenants evicted under the Ellis Act

### r-0103 — San Francisco, CA — just_cause_eviction — S.F. Admin. Code §37.9
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 80 个在范围内）：applies 80

### r-0105 — San Francisco, CA — just_cause_eviction — S.F. Admin. Code §37.9C
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：note: Amounts depend on the type of eviction notice served and on whether the tenant is 60 or older, disabled, or a household with minor children.
- 地址结果（共 80 个在范围内）：applies 80
- 原文：> Relocation Payments for Evictions based on Owner/Relative Move-in OR Demolition/Permanent Removal of Unit from Housing Use OR Temporary Capital Improvement Work* OR Substantial Rehabilitation
- 原文：> The amount of relocation payments for temporary capital improvement evictions for less than 20 days is governed by California Civil Code Section 1947.9 and not by Rent Ordinance Section 37.9C.

### r-0191 — San Francisco, CA — rent_increase_limits — S.F. Admin. Code ch. 37
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：covered if built on or before 1979-06-13；date basis: certificate_of_occupancy
- 地址结果（共 80 个在范围内）：applies 71，omitted: a condition excludes it 7，unknown 2
- **注意：条件使它在 7 个地址上消失**
- 手写补充条目 `sf-rent-cap-cutoff`（不是模型提取）：This includes tenancies in newly constructed rental units that first obtained a Certificate of Occupancy after June 13, 1979, tenancies that are eligible for a rent increase under the Costa-Hawkins Rental Housing Act, and some tenancies where the rent is regulated by another government agency. Parti；来源：starter-pack/participant-final-no-hour16 3/corpus/text/D079.txt; D080.txt: For rent-controlled units, the annual allowable increase amount effective March 1, 2026 through February 28, 2027 is 1.6%.

### r-0224 — San Francisco, CA — screening_restrictions — San Francisco's Fair Chance Ordinance
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 80 个在范围内）：applies 80
- 原文：> San Francisco's Fair Chance Ordinance protects residents with arrest or conviction history in affordable housing decisions.

### r-0195 — San Francisco, CA — security_deposits — S.F. Admin. Code ch. 37
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：无
- 地址结果（共 80 个在范围内）：applies 80

### r-0198 — Santa Ana, CA — algorithmic_rent_setting — Santa Ana Mun. Code ch. 9, art. XXIV (Ordinance No. NS-3090)
- 状态：enacted；生效日期：2026-04-02；有效期至：—
- 条件：无
- 地址结果（共 0 个在范围内）：—
- 原文：> use an Algorithmic Device to set rental rates or occupancy levels for Residential Real Property

### r-0196 — Santa Ana, CA — algorithmic_rent_setting — Santa Ana Mun. Code §8-3702
- 状态：enacted；生效日期：2026-04-02；有效期至：—
- 条件：无
- 地址结果（共 0 个在范围内）：—

### r-0193 — Santa Ana, CA — just_cause_eviction — Rent Stabilization and Just Cause Eviction Ordinance
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 0 个在范围内）：—

### r-0113 — Santa Ana, CA — just_cause_eviction — Santa Ana Just Cause Eviction Ordinance
- 状态：enacted；生效日期：2021-11-19；有效期至：—
- 条件：exempt if newer than 15 years；date basis: construction_date；note, does not change the answer (kinds of housing the data cannot show): deed-restricted affordable housing；note: Owner may not terminate a tenancy without just cause after 30 days of tenancy.
- 地址结果（共 0 个在范围内）：—
- 原文：> After 30 days, an owner shall not terminate a tenancy without just cause, which shall be stated in a written notice.
- 原文：> The Just Cause Ordinance shall not apply to certain types of residential property, including housing produced in the last 15 years; deed-restricted affordable housing; hotel and transient occupancy; hospital and care facilities; dormitories; and other shared living quarters.

### r-0192 — Santa Ana, CA — rent_increase_limits — Rent Stabilization and Just Cause Eviction Ordinance
- 状态：enacted；生效日期：2026-09-01；有效期至：2027-08-31
- 条件：无
- 地址结果（共 0 个在范围内）：—

### r-0110 — Santa Ana, CA — rent_increase_limits — Santa Ana Rent Stabilization Ordinance
- 状态：enacted；生效日期：2021-11-19；有效期至：—
- 条件：covered if built on or before 1995-02-01；date basis: construction_date；note, does not change the answer (kinds of housing the data cannot show): mobile home spaces offered for rent after January 1, 1990
- 地址结果（共 0 个在范围内）：—
- 原文：> The rent cap does not apply to residential buildings constructed after February 1, 1995, or to mobile home spaces offered for rent after January 1, 1990.

