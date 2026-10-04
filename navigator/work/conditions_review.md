# 条件核对表（第一阶段提取的条件对 500 个地址的影响）

条件由模型从原文读出，请抽查。最贵的错误是**误判豁免**：规则会在本该适用的地址上悄悄消失。
下面先列需要优先看的规则，再列全部规则。查询日期 2026-10-01。

## 优先核对（26 条）

### r-0136 — Berkeley, CA — rent_increase_limits — Berkeley Mun. Code ch. 13.76
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：covered if built on or before 1980-06；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): most condominiums and units with certain government subsidies are not rent-controlled；note: Applies to fully covered units; most single-family homes and most condominiums are only partially covered.; Single family homes and rooming houses: rent control only where the tenancy began before 1996; ADU tenancies started after November 7, 2018 with an owner-occupied unit are exempt.
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> Most units in multifamily properties built before 1980
- 原文：> New Construction Units (units with a certificate of occupancy issued after 1980)
- 原文：> Most units in multifamily properties built before 1980** Fully Covered Yes Yes Yes Yes
- 原文：> New construction: units that were built and received a Certificate of Occupancy after June 1980**

### r-0138 — Berkeley, CA — rent_increase_limits — Berkeley Mun. Code §13.76.110
- 状态：enacted；生效日期：2026-01-01；有效期至：2026-12-31
- 条件：covered if built on or before 1980-06；owner-dependent, no size limit (unknown for every address)；date basis: certificate_of_occupancy；note: The 2026 AGA may not adjust rents for tenancies that began on or after January 1, 2025 and whose rents were set pursuant to the Costa-Hawkins Rental Housing Act.
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> The 2026 AGA may not adjust tenants’ rents when their tenancy began on or after January 1, 2025, and who had their rents set pursuant to the Costa-Hawkins Rental Housing Act.

### r-0024 — CA — just_cause_eviction — Cal. Civ. Code §1946.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：exempt if newer than 15 years；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): deed- or agreement-restricted affordable housing for very low, low or moderate income；note: Just cause applies only after all tenants have continuously occupied 12 months, or one tenant 24 months; excludes a tenancy sharing bathroom or kitchen with the owner.
- 地址结果（共 250 个在范围内）：applies 147，omitted: a condition excludes it 5，unknown 98
- **注意：条件使它在 5 个地址上消失**
- 原文：> (7) Housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome.
- 原文：> (A) A residence in which the owner-occupant rents or leases no more than two units or bedrooms, including, but not limited to, an accessory dwelling unit or a junior accessory dwelling unit.
- 原文：> (9) Housing restricted by deed, regulatory restriction contained in an agreement with a government agency, or other recorded document as affordable housing for persons and families of very low, low, or moderate income, as defined in Section 50093 of the Health and Safety Code
- 关系 `yields_to_local`：> (A) Residential real property subject to a local ordinance requiring just cause for termination of a residential tenancy adopted on or before September 1, 2019, in which case the local ordinance shall apply.
- 关系 `yields_to_local`：> (2) A residential real property shall not be subject to both a local ordinance requiring just cause for termination of a residential tenancy and this section.

### r-0022 — CA — rent_increase_limits — Cal. Civ. Code §1947.12
- 状态：enacted；生效日期：2024-04-01；有效期至：2030-01-01
- 条件：exempt if newer than 15 years；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): housing restricted by deed or government agreement as affordable or subsidized housing; housing under a local rent control ordinance restricting annual increases below the state cap; single-family or condominium property alienable separate from other titles, owned by a non-corporate owner, with written notice given; Units restricted by deed or recorded document limiting affordability to low- or moderate-income households; Units already subject to the City's Rent Stabilization Ordinance; Single-family homes and condominiums not owned by a trust, corporation or corporate LLC, where the tenant got the required written notice；note: The initial rental rate for a new tenancy in which no tenant from the prior tenancy remains in lawful possession is not subject to the cap.
- 地址结果（共 250 个在范围内）：applies 76，omitted: a condition excludes it 5，superseded 71，unknown 98
- **注意：条件使它在 5 个地址上消失**
- 原文：> (4) Housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome.
- 原文：> (6) A property containing two separate dwelling units within a single structure in which the owner occupied one of the units as the owner’s principal place of residence at the beginning of the tenancy, so long as the owner continues in occupancy, and neither unit is an accessory dwelling unit or a junior accessory dwelling unit.
- 原文：> (1) Housing restricted by deed, regulatory restriction contained in an agreement with a government agency, or other recorded document as affordable housing for persons and families of very low, low, or moderate income, as defined in Section 50093 of the Health and Safety Code
- 原文：> may regulate the rent amount in buildings that are older than 15 years old.
- 关系 `yields_to_local`：> Housing subject to rent or price control through a public entity’s valid exercise of its police power consistent with Chapter 2.7 (commencing with Section 1954.50) that restricts annual increases in the rental rate to an amount less than that provided in subdivision (a).

### r-0143 — Hoboken, NJ — rent_increase_limits — Hoboken City Code §155-4
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner-dependent, no size limit (unknown for every address)；exemption only if the owner filed (open question inside its reach): built within the last 30 years；UNRESOLVED: building completely vacant on or before and since January 1, 1984；note: Newly constructed dwellings are exempt for their initial rent or lease agreement; all subsequent rents are subject.
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> This chapter shall apply to all dwelling units as defined in § 155-1 above, except that the following shall be exempt:
- 原文：> In accordance with N.J.S.A. 2A:42-84.1 et seq., the provisions of this chapter shall not apply to multiple dwellings, as defined in the statute, constructed after June 25, 1987, for a period not to exceed the period of amortization of any initial mortgage loan obtained for the multiple dwelling or for 30 years following completion of construction, whichever is less.
- 原文：> Housing owned and operated by other government agencies, such as the state or federal government.

### r-0151 — Hoboken, NJ — rent_increase_limits — Hoboken, N.J., Code §155-13
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: newly constructed dwellings eligible for exemption; buildings completely vacant since January 1, 1984 eligible for exemption
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> The Regulation Officer shall make all determinations regarding the eligibility of a newly constructed dwelling for an exemption as defined above.
- 原文：> The Rent Regulation Officer shall make all determinations regarding the eligibility of a building completely vacant since January 1, 1984, for an exemption as defined above.

### r-0152 — Hoboken, NJ — rent_increase_limits — Hoboken, N.J., Code §155-14
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: newly constructed dwellings eligible for exemption; buildings completely vacant since January 1, 1984 eligible for exemption
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> The Regulation Officer shall make all determinations regarding the eligibility of a newly constructed dwelling for an exemption as defined above.
- 原文：> The Rent Regulation Officer shall make all determinations regarding the eligibility of a building completely vacant since January 1, 1984, for an exemption as defined above.

### r-0145 — Hoboken, NJ — rent_increase_limits — Hoboken, N.J., Code §155-37
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner-dependent, no size limit (unknown for every address)；note: Decontrol applies only on vacancy by a bona fide CCOO and only for establishing the initial rent.
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> In the event that an owner of a condo/co-op unit has continuously occupied said unit as his/ her principal residence for the previous two years, the owner may file an affidavit with, and on the form provided by, the Rent Regulation Officer documenting his/her use.
- 原文：> In the event that an individual who qualifies as a bona fide CCOO vacates his/her condo/co-op unit and offers it for rental, said unit is decontrolled solely for the purpose of establishing the initial rent subsequent to the bona fide CCOO vacating.

### r-0079 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code ch. 260
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at least 5 units；exemption only if the owner filed (open question inside its reach): built on or after 1987-06-25；exemption only if the owner filed (open question inside its reach): built on or before 1992-06-25
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> the provisions of this chapter which limit the periodic or regular increases in base rentals of dwelling units shall not apply to a newly constructed dwelling which is constructed between June 25, 1987, through June 25, 1992
- 原文：> no dwelling, landlord, or owner, regardless of rent control status, is exempt from any other provision of Chapter 260.
- 原文：> (Please Note: All 1-4 Unit Properties are exempt from rent control)
- 原文：> The Rent Control Ordinance provides certain exemptions from rent regulation.

### r-0197 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code §260-3
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at least 5 units；UNRESOLVED: newly constructed dwellings with 25 or more units in a city-approved redevelopment area; buildings converted from nonpermanent dwelling use to dwelling use on or after October 1, 1983；note, does not change the answer (kinds of housing the data cannot show): low rent public housing developments；note: New dwellings or housing spaces rented for the first time are exempt for the initial rental only.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> Dwellings with four or less housing spaces; provided, however, that this exemption shall be suspended for non-owner occupied dwellings with four or less housing spaces until the end of the state of emergency or six months from adoption of these amendments whichever comes first.
- 原文：> Newly constructed dwellings with 25 or more dwelling units located within a redevelopment area as defined in Section 5 of the Redevelopment Agencies Law, N.J.S.A. 40:55C-5(o), for which the City Council has approved a redevelopment plan, in accordance with Section 17 of the Redevelopment Agencies Law, N.J.S.A. 40:55C-17.
- 原文：> All buildings or structures, hotels, motels or guesthouses which are converted from any previous use as a nonpermanent dwelling to use as a dwelling on or after October 1, 1983.

### r-0203 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code §260-6
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：exemption only if the owner filed (open question inside its reach): built on or after 1987-06-25；exemption only if the owner filed (open question inside its reach): built on or before 1992-06-25；UNRESOLVED: dwellings certified by the Division of Tenant/Landlord Relations as vacant as of July 1, 1998 are permanently exempt；note: The initial rent for newly constructed housing space rented for the first time is not restricted.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> the provisions of this chapter shall not apply to a new dwelling which is constructed between June 25, 1987, through June 25, 1992, and which is not constructed for occupation by senior citizens, for a period of time not to exceed the period of amortization of any initial mortgage loan obtained for the dwelling, or for 30 years following completion of construction, whichever is less

### r-0155 — Los Angeles, CA — just_cause_eviction — Los Angeles Rent Stabilization Ordinance (L.A.M.C. §151.00 et seq.)
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：covered if built on or before 1978-10-01；date basis: construction_date
- 地址结果（共 80 个在范围内）：applies 47，omitted: a condition excludes it 25，unknown 8
- **注意：条件使它在 25 个地址上消失**
- 原文：> Generally, the RSO applies to rental properties that were first built on or before October 1, 1978

### r-0035 — MA — rent_increase_limits — G.L. c. 40P, §4
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner-dependent, no size limit (unknown for every address)；note: Local rent control regulation may not apply to a rental unit that has a fair market rent exceeding $400.
- 地址结果（共 110 个在范围内）：unknown 110
- **注意：所有 110 个地址都是不确定**
- 原文：> nor may such regulation apply to any rental unit that is owned by a person or entity owning less than ten rental units or that has a fair market rent exceeding $400
- 关系 `preempts_local`：> No city or town may enact, maintain or enforce rent control of any kind

### r-0065 — NJ — application_screening_fees — N.J.S.A. 46:8-18.1
- 状态：enacted；生效日期：2026-05-01；有效期至：—
- 条件：at least 3 units；note: Exemption for a licensee of the New Jersey Real Estate Commission unless the licensee is the landlord of the property.
- 地址结果（共 140 个在范围内）：applies 86，omitted: a condition excludes it 1，unknown 53
- **注意：条件使它在 1 个地址上消失**
- 原文：> a dwelling unit located in a one-family or two-family dwelling that is offered for rent
- 原文：> a licensee of the New Jersey Real Estate Commission, unless the licensee is the landlord of the residential rental property

### r-0053 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner-dependent, no size limit (unknown for every address)
- 地址结果（共 140 个在范围内）：unknown 140
- **注意：所有 140 个地址都是不确定**
- 原文：> Tenants of landlord-occupied two- and three-family dwellings can be removed only when a court issues an order for eviction.

### r-0048 — NJ — rent_increase_limits — N.J.S.A. 2A:18-61.1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at least 3 units；owner exemption up to 3 units
- 地址结果（共 140 个在范围内）：applies 86，omitted: a condition excludes it 1，unknown 53
- **注意：条件使它在 1 个地址上消失**
- 原文：> This law may not apply to two - or three-unit owner-occupied premises with two (2) or fewer rental units.

### r-0050 — NJ — rent_increase_limits — N.J.S.A. 2A:42-84.5
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：exempt if newer than 30 years；date basis: construction_date
- 地址结果（共 140 个在范围内）：applies 30，omitted: a condition excludes it 4，unknown 106
- **注意：条件使它在 4 个地址上消失**
- 原文：> newly constructed multiple dwellings shall be exempt from any local rent control ordinances for a period of 30 years following completion of construction of the building

### r-0067 — NJ — screening_restrictions — N.J.S.A. 10:5-12
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units；UNRESOLVED: rooms in an owner- or resident-occupied single home; residences planned exclusively for and occupied by one sex
- 地址结果（共 140 个在范围内）：unknown 140
- **注意：所有 140 个地址都是不确定**
- 原文：> The law applies to all landlord -tenant relationships, except those involving two -family owner occupied dwellings, rooms in an owner or resident -occupied single home, and residences planned exclusively for and occupied by one sex, i.e. YMCA and age -restricted housing, as it pertains to familial status (N.J.S.A. 10:5-5(n)).

### r-0177 — Newark, NJ — rent_increase_limits — Newark Mun. Code §19:2-18
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：exemption only if the owner filed (open question inside its reach): built within the last 30 years；UNRESOLVED: dwellings vacant at least 18 months or already vacant on the effective date of the section; reconstruction or rehabilitation cost during twelve months exceeds 50% of fair market value
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> The provisions of the Rent Control Ordinance, which limit the periodic or regular increases in base rentals of dwelling units shall not apply to newly constructed multiple dwellings for a period of time not to exceed the period of amortization of any initial mortgage loan obtained for the multiple dwelling, or for 30 years following completion of construction, whichever is less.
- 原文：> Dwellings which become vacant and remain vacant for a minimum of 18 months or dwellings which are already vacant on the effective date of this section shall be exempt for a period of five years from any restrictions in the rent that the landlord may charge
- 原文：> Substantially reconstructed or rehabilitated dwellings shall not be restricted in initial rent charged, if the Rent Control Board has made the following determinations:

### r-0180 — Newark, NJ — rent_increase_limits — Newark Mun. Code §19:2-3
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: newly constructed multiple dwellings (see § 19:2-18.1); vacant dwellings (see § 19:2-18.2)；note, does not change the answer (kinds of housing the data cannot show): public housing; units rehabilitated under federal/state Rental Rehabilitation Programs receiving Section 8 subsidies or housing vouchers; units under a government contract that regulates rent (preempted during the contract)
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> All multiple dwellings, as defined in subsection 19:2-2, are subject to Rent Control pursuant to this Title XIX Rent Control
- 原文：> EXEMPTIONS — Shall mean dwellings to which this chapter shall not apply.
- 原文：> if the authority of that governmental agency supersedes the authority of the City of Newark to regulate such rents, then the application of this chapter shall be preempted during the period of governmental agency regulation specified in the contract.

### r-0181 — Newark, NJ — rent_increase_limits — Newark, N.J., Code §2:10-1.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: only HOME-assisted units receiving HOME Program funds are covered
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> The DHA must review and approve rents proposed by the owner for units subject to the maximum rent limitations

### r-0182 — Newark, NJ — screening_restrictions — Newark, N.J., Code §2:10-1.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: only HOME-assisted units receiving HOME Program funds are covered
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> The owner cannot refuse to lease HOME-assisted units to a certificate or voucher holder under 24 CFR part 982

### r-0186 — Newark, NJ — screening_restrictions — Newark, NJ, Rev. Gen. Ordinances ch. 2:31, art. 1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> the provisions of this Article shall not apply to the rental:
- 原文：> Of a single apartment or flat in a two family dwelling, the other occupancy unit of which is occupied by the owner as his/her residence
- 原文：> Of a room or rooms to another person or persons by the owner or occupant of one-family dwelling occupied by him/her as his/her residence

### r-0095 — San Diego, CA — just_cause_eviction — San Diego Mun. Code §98.0704
- 状态：enacted；生效日期：2023-06-24；有效期至：—
- 条件：exempt if newer than 15 years；owner-dependent, no size limit (unknown for every address)；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): housing restricted by deed or government agreement as affordable to very low, low or moderate income; property alienable separate from title to other units, landlord not a corporation, REIT or LLC with corporate member, giving written notice；note: Fixed-term lease of three months or less; occupancy of 30 days or less; tenant sharing bathroom or kitchen with owner-occupant landlord.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> (k) housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome; and
- 原文：> (j) a property containing two separate dwelling units within a single structure in which the landlord occupies one of the dwelling units as the landlord’s principal place of residence at the beginning of the tenancy, so long as the landlord continues in occupancy;
- 原文：> (h) residential rental property in which the tenant shares bathroom or kitchen facilities with the landlord who maintains their principal residence at the residential rental property;

### r-0103 — San Francisco, CA — just_cause_eviction — S.F. Admin. Code §37.9
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: rental unit covered by the Rent Ordinance；note: Applies to tenancies in covered rental units, including tenancies exempt from the Ordinance's rent increase limits.
- 地址结果（共 80 个在范围内）：unknown 80
- **注意：所有 80 个地址都是不确定**
- 原文：> In order to evict a tenant from a rental unit covered by the Rent Ordinance, a landlord must have a "just cause" reason that is the dominant motive for pursuing the eviction.

### r-0191 — San Francisco, CA — rent_increase_limits — S.F. Admin. Code ch. 37
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：covered if built on or before 1979-06-13；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): rent regulated by another government agency；note: Tenancies eligible for a rent increase under the Costa-Hawkins Rental Housing Act.
- 地址结果（共 80 个在范围内）：applies 71，omitted: a condition excludes it 7，unknown 2
- **注意：条件使它在 7 个地址上消失**
- 原文：> For rent-controlled units, the annual allowable increase amount effective March 1, 2026 through February 28, 2027 is 1.6%.
- 原文：> This includes tenancies in newly constructed rental units that first obtained a Certificate of Occupancy after June 13, 1979, tenancies that are eligible for a rent increase under the Costa-Hawkins Rental Housing Act, and some tenancies where the rent is regulated by another government agency.

## 全部规则（120 条）

### r-0021 — Berkeley, CA — algorithmic_rent_setting — Berkeley Mun. Code ch. 13.63
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 40 个在范围内）：applies 40
- 原文：> It shall be unlawful for a landlord to use a coordinated pricing algorithm described in subsection A when setting rents or occupancy levels for residential dwelling units in the City of Berkeley.

### r-0135 — Berkeley, CA — application_screening_fees — Berkeley Mun. Code ch. 13.78
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Applies to all residential rental agreements regardless of contrary lease terms; the disclosure duty attaches when an owner charges a screening fee.
- 地址结果（共 40 个在范围内）：applies 40

### r-0134 — Berkeley, CA — just_cause_eviction — Berkeley Mun. Code ch. 13.76
- 状态：enacted；生效日期：2026-01-01；有效期至：2026
- 条件：owner exemption up to 2 units；note: Relocation assistance owed for owner move-in and Ellis Act evictions; Units where the tenant shares a kitchen or bath with a landlord who lived on the same property at the start of the tenancy are exempt from the Ordinance.; Exempt: a unit where the owner shares a kitchen or bath with the tenant; tenancies started after November 7, 2018 on properties where one unit is an ADU and either unit is owner-occupied.
- 地址结果（共 40 个在范围内）：applies 40
- 原文：> New construction: units that were built and received a Certificate of Occupancy after June 1980** Partially Covered Yes No Yes Yes
- 原文：> Most condominiums** Partially Covered Yes No Yes Yes

### r-0136 — Berkeley, CA — rent_increase_limits — Berkeley Mun. Code ch. 13.76
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：covered if built on or before 1980-06；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): most condominiums and units with certain government subsidies are not rent-controlled；note: Applies to fully covered units; most single-family homes and most condominiums are only partially covered.; Single family homes and rooming houses: rent control only where the tenancy began before 1996; ADU tenancies started after November 7, 2018 with an owner-occupied unit are exempt.
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> Most units in multifamily properties built before 1980
- 原文：> New Construction Units (units with a certificate of occupancy issued after 1980)
- 原文：> Most units in multifamily properties built before 1980** Fully Covered Yes Yes Yes Yes
- 原文：> New construction: units that were built and received a Certificate of Occupancy after June 1980**

### r-0138 — Berkeley, CA — rent_increase_limits — Berkeley Mun. Code §13.76.110
- 状态：enacted；生效日期：2026-01-01；有效期至：2026-12-31
- 条件：covered if built on or before 1980-06；owner-dependent, no size limit (unknown for every address)；date basis: certificate_of_occupancy；note: The 2026 AGA may not adjust rents for tenancies that began on or after January 1, 2025 and whose rents were set pursuant to the Costa-Hawkins Rental Housing Act.
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> The 2026 AGA may not adjust tenants’ rents when their tenancy began on or after January 1, 2025, and who had their rents set pursuant to the Costa-Hawkins Rental Housing Act.

### r-0020 — Berkeley, CA — screening_restrictions — Berkeley Mun. Code ch. 13.106
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 3 units；note: Exemptions for units under a rental agreement allowing owners to move back (BMC 13.76.130 A.9), units occupied by existing tenants seeking to sublet or add/replace roommates, lifetime sex offenders, and public housing/Section 8 properties.
- 地址结果（共 40 个在范围内）：applies 40
- 原文：> Owner-occupied properties (between 1-3 units) in which an owner of record resides in one of the units as their primary residence
- 原文：> Units occupied by existing tenant(s) seeking to sublet or add/replace roommates
- 原文：> Units under a rental agreement allowing owners to move back to their home in accordance with BMC 13.76.130 A.9

### r-0137 — Berkeley, CA — security_deposits — Berkeley Mun. Code ch. 13.76
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units；note: Exempt: a unit where the owner shares a kitchen or bath with the tenant; tenancies started after November 7, 2018 on properties where one unit is an ADU and either unit is owner-occupied.
- 地址结果（共 40 个在范围内）：applies 40
- 原文：> For tenancies in units fully or partially covered by Berkeley's Rent Ordinance, landlords must pay tenants interest on their security deposit at the end of each year and a prorated amount if the tenant moves out before the end of the year.
- 原文：> Single family homes with current tenancies that began before 1996** Fully Covered Yes Yes Yes Yes
- 原文：> Most condominiums** Partially Covered Yes No Yes Yes

### r-0074 — Boston, MA — just_cause_eviction — Boston Mun. Code §10-11.7
- 状态：enacted；生效日期：2020-11-06；有效期至：—
- 条件：note: Applies when a landlord plans to end a tenancy by notice to quit or notice of non-renewal of lease.; Duty applies when a landlord serves a Notice to Quit or decides not to renew a lease, or a foreclosing owner ends post-foreclosure occupancy.
- 地址结果（共 60 个在范围内）：applies 60
- 原文：> The Ordinance applies to all landlords/foreclosing owners intending to end a tenancy or post-foreclosure occupancy of a unit in the City of Boston.

### r-0125 — Boston, MA — screening_restrictions — Boston Fair Chance Tenant Selection Policy
- 状态：enacted；生效日期：2017-02；有效期至：—
- 条件：note, does not change the answer (kinds of housing the data cannot show): Only housing providers receiving DND funding or land or with BPDA Inclusionary Development Policy income-restricted units；note: Exceptions where a conviction has a direct relationship to the housing sought or an unreasonable risk of substantial harm; does not apply to current criminal behavior.
- 地址结果（共 60 个在范围内）：applies 60
- 原文：> Housing providers receiving Department of Neighborhood Development (DND) funding and/or land, or that have income restricted units created under the Boston Planning and Development Agency (BPDA) Inclusionary Development Policy will not impose a blanket policy that denies housing to anyone with arrests and or convictions.

### r-0126 — Boston, MA — screening_restrictions — Boston Fair Housing Regulations
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Covered for any renter or buyer in Boston who uses rental assistance, including Section 8 vouchers, social security disability vouchers, and veterans vouchers.
- 地址结果（共 60 个在范围内）：applies 60
- 原文：> In the City of Boston, it’s illegal to discriminate when renting, buying, selling, or securing financing for any housing.

### r-0034 — CA — algorithmic_rent_setting — AB 325 (Cal. Bus. & Prof. Code §16729)
- 状态：enacted；生效日期：2026-01-01；有效期至：—
- 条件：无
- 地址结果（共 250 个在范围内）：applies 250
- 原文：> (5) “Person” has the same meaning as defined in Section 16702 and does not include the end consumer of a product or service.

### r-0005 — CA — application_screening_fees — Cal. Civ. Code §1950.6
- 状态：enacted；生效日期：2026-01-01；有效期至：2026
- 条件：note: A screening fee may be charged when a rental unit is actually available; an unselected applicant must be refunded, or applications are reviewed in the order received and the first qualified applicant gets the unit.
- 地址结果（共 250 个在范围内）：applies 250

### r-0024 — CA — just_cause_eviction — Cal. Civ. Code §1946.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：exempt if newer than 15 years；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): deed- or agreement-restricted affordable housing for very low, low or moderate income；note: Just cause applies only after all tenants have continuously occupied 12 months, or one tenant 24 months; excludes a tenancy sharing bathroom or kitchen with the owner.
- 地址结果（共 250 个在范围内）：applies 147，omitted: a condition excludes it 5，unknown 98
- **注意：条件使它在 5 个地址上消失**
- 原文：> (7) Housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome.
- 原文：> (A) A residence in which the owner-occupant rents or leases no more than two units or bedrooms, including, but not limited to, an accessory dwelling unit or a junior accessory dwelling unit.
- 原文：> (9) Housing restricted by deed, regulatory restriction contained in an agreement with a government agency, or other recorded document as affordable housing for persons and families of very low, low, or moderate income, as defined in Section 50093 of the Health and Safety Code
- 关系 `yields_to_local`：> (A) Residential real property subject to a local ordinance requiring just cause for termination of a residential tenancy adopted on or before September 1, 2019, in which case the local ordinance shall apply.
- 关系 `yields_to_local`：> (2) A residential real property shall not be subject to both a local ordinance requiring just cause for termination of a residential tenancy and this section.

### r-0025 — CA — just_cause_eviction — Cal. Civ. Code §1947.9
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：无
- 地址结果（共 250 个在范围内）：applies 250

### r-0022 — CA — rent_increase_limits — Cal. Civ. Code §1947.12
- 状态：enacted；生效日期：2024-04-01；有效期至：2030-01-01
- 条件：exempt if newer than 15 years；owner exemption up to 2 units；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): housing restricted by deed or government agreement as affordable or subsidized housing; housing under a local rent control ordinance restricting annual increases below the state cap; single-family or condominium property alienable separate from other titles, owned by a non-corporate owner, with written notice given; Units restricted by deed or recorded document limiting affordability to low- or moderate-income households; Units already subject to the City's Rent Stabilization Ordinance; Single-family homes and condominiums not owned by a trust, corporation or corporate LLC, where the tenant got the required written notice；note: The initial rental rate for a new tenancy in which no tenant from the prior tenancy remains in lawful possession is not subject to the cap.
- 地址结果（共 250 个在范围内）：applies 76，omitted: a condition excludes it 5，superseded 71，unknown 98
- **注意：条件使它在 5 个地址上消失**
- 原文：> (4) Housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome.
- 原文：> (6) A property containing two separate dwelling units within a single structure in which the owner occupied one of the units as the owner’s principal place of residence at the beginning of the tenancy, so long as the owner continues in occupancy, and neither unit is an accessory dwelling unit or a junior accessory dwelling unit.
- 原文：> (1) Housing restricted by deed, regulatory restriction contained in an agreement with a government agency, or other recorded document as affordable housing for persons and families of very low, low, or moderate income, as defined in Section 50093 of the Health and Safety Code
- 原文：> may regulate the rent amount in buildings that are older than 15 years old.
- 关系 `yields_to_local`：> Housing subject to rent or price control through a public entity’s valid exercise of its police power consistent with Chapter 2.7 (commencing with Section 1954.50) that restricts annual increases in the rental rate to an amount less than that provided in subdivision (a).

### r-0030 — CA — screening_restrictions — Cal. Civ. Code §1950.6
- 状态：enacted；生效日期：2026-01-01；有效期至：—
- 条件：note: Applies when an applicant provides a reusable screening report, or when a screening fee is used to obtain a consumer credit report.
- 地址结果（共 250 个在范围内）：applies 250

### r-0031 — CA — screening_restrictions — Cal. Gov. Code §12955
- 状态：enacted；生效日期：2024-01-01；有效期至：—
- 条件：无
- 地址结果（共 250 个在范围内）：applies 250

### r-0139 — CA — screening_restrictions — California's Fair Employment and Housing Act (FEHA)
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: An owner occupying a home and renting to one additional person may exclude applicants based on protected characteristics; a shared single dwelling may be limited to one sex; housing for seniors or homeless youth may be limited by age.
- 地址结果（共 250 个在范围内）：applies 250

### r-0001 — CA — security_deposits — AB 12
- 状态：enacted；生效日期：2024-07-01；有效期至：—
- 条件：owner exemption up to 4 units
- 地址结果（共 250 个在范围内）：applies 250
- 原文：> Starting July 1, 2024, landlords who own only two rental properties with no more than four residential units total can charge up to two months' rent for furnished and unfurnished units if ownership is held by a natural person, family trust, or limited liability company (LLC) where all members are natural persons

### r-0029 — CA — security_deposits — Cal. Civ. Code §1950.5
- 状态：enacted；生效日期：2024-07-01；有效期至：—
- 条件：note: The two-month higher-security option does not apply if the prospective tenant is a service member; the one-month cap does not apply to security collected or demanded before July 1, 2024.
- 地址结果（共 250 个在范围内）：applies 250

### r-0078 — Cambridge, MA — screening_restrictions — Cambridge Mun. Code ch. 14.04
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units
- 地址结果（共 50 个在范围内）：applies 50
- 原文：> NOTE: there is an exemption for 2-family dwellings, when the owner lives there

### r-0148 — Hoboken, NJ — algorithmic_rent_setting — Hoboken Mun. Code §158-2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 40 个在范围内）：applies 40

### r-0144 — Hoboken, NJ — just_cause_eviction — Hoboken City Code §155-1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 40 个在范围内）：applies 40

### r-0143 — Hoboken, NJ — rent_increase_limits — Hoboken City Code §155-4
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner-dependent, no size limit (unknown for every address)；exemption only if the owner filed (open question inside its reach): built within the last 30 years；UNRESOLVED: building completely vacant on or before and since January 1, 1984；note: Newly constructed dwellings are exempt for their initial rent or lease agreement; all subsequent rents are subject.
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> This chapter shall apply to all dwelling units as defined in § 155-1 above, except that the following shall be exempt:
- 原文：> In accordance with N.J.S.A. 2A:42-84.1 et seq., the provisions of this chapter shall not apply to multiple dwellings, as defined in the statute, constructed after June 25, 1987, for a period not to exceed the period of amortization of any initial mortgage loan obtained for the multiple dwelling or for 30 years following completion of construction, whichever is less.
- 原文：> Housing owned and operated by other government agencies, such as the state or federal government.

### r-0141 — Hoboken, NJ — rent_increase_limits — Hoboken Mun. Code §155-25
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 40 个在范围内）：applies 40

### r-0142 — Hoboken, NJ — rent_increase_limits — Hoboken Mun. Code §155-31
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Decontrol applies upon vacancy of a registered unit; requires voluntary vacancy without harassment or a legal eviction; limited to once per three years.
- 地址结果（共 40 个在范围内）：applies 40

### r-0140 — Hoboken, NJ — rent_increase_limits — Hoboken Mun. Code §155-5
- 状态：enacted；生效日期：2023-02-01；有效期至：—
- 条件：无
- 地址结果（共 40 个在范围内）：applies 40

### r-0147 — Hoboken, NJ — rent_increase_limits — Hoboken Mun. Code §158-1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: increase of more than 10% upon renewal of a lease with a current tenant year over year
- 地址结果（共 40 个在范围内）：applies 40

### r-0151 — Hoboken, NJ — rent_increase_limits — Hoboken, N.J., Code §155-13
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: newly constructed dwellings eligible for exemption; buildings completely vacant since January 1, 1984 eligible for exemption
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> The Regulation Officer shall make all determinations regarding the eligibility of a newly constructed dwelling for an exemption as defined above.
- 原文：> The Rent Regulation Officer shall make all determinations regarding the eligibility of a building completely vacant since January 1, 1984, for an exemption as defined above.

### r-0152 — Hoboken, NJ — rent_increase_limits — Hoboken, N.J., Code §155-14
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: newly constructed dwellings eligible for exemption; buildings completely vacant since January 1, 1984 eligible for exemption
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> The Regulation Officer shall make all determinations regarding the eligibility of a newly constructed dwelling for an exemption as defined above.
- 原文：> The Rent Regulation Officer shall make all determinations regarding the eligibility of a building completely vacant since January 1, 1984, for an exemption as defined above.

### r-0145 — Hoboken, NJ — rent_increase_limits — Hoboken, N.J., Code §155-37
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner-dependent, no size limit (unknown for every address)；note: Decontrol applies only on vacancy by a bona fide CCOO and only for establishing the initial rent.
- 地址结果（共 40 个在范围内）：unknown 40
- **注意：所有 40 个地址都是不确定**
- 原文：> In the event that an owner of a condo/co-op unit has continuously occupied said unit as his/ her principal residence for the previous two years, the owner may file an affidavit with, and on the form provided by, the Rent Regulation Officer documenting his/her use.
- 原文：> In the event that an individual who qualifies as a bona fide CCOO vacates his/her condo/co-op unit and offers it for rental, said unit is decontrolled solely for the purpose of establishing the initial rent subsequent to the bona fide CCOO vacating.

### r-0146 — Hoboken, NJ — rent_increase_limits — Hoboken, N.J., Code §155-38
- 状态：enacted；生效日期：2020-04-01；有效期至：2022-05-07
- 条件：无
- 地址结果（共 40 个在范围内）：omitted: outside its valid period 40
- 原文：> A moratorium shall be in effect to prevent any increase in the amount paid in rent or any additional charges whatsoever by tenants covered by this chapter.

### r-0149 — Jersey City, NJ — algorithmic_rent_setting — Jersey City Mun. Code §218-12
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Exempts owners of multiple properties for actions related exclusively to properties they control, and licensed real estate agents operating under state regulations.; A sworn disclosure statement must accompany each lease and each written notice of rent increase.
- 地址结果（共 50 个在范围内）：applies 50
- 原文：> Any landlord must include, with any lease or written notice of rent increase for a residential dwelling unit, a sworn disclosure statement, executed under penalty of perjury

### r-0079 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code ch. 260
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at least 5 units；exemption only if the owner filed (open question inside its reach): built on or after 1987-06-25；exemption only if the owner filed (open question inside its reach): built on or before 1992-06-25
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> the provisions of this chapter which limit the periodic or regular increases in base rentals of dwelling units shall not apply to a newly constructed dwelling which is constructed between June 25, 1987, through June 25, 1992
- 原文：> no dwelling, landlord, or owner, regardless of rent control status, is exempt from any other provision of Chapter 260.
- 原文：> (Please Note: All 1-4 Unit Properties are exempt from rent control)
- 原文：> The Rent Control Ordinance provides certain exemptions from rent regulation.

### r-0200 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code §260-10
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50

### r-0199 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code §260-15
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50

### r-0197 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code §260-3
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at least 5 units；UNRESOLVED: newly constructed dwellings with 25 or more units in a city-approved redevelopment area; buildings converted from nonpermanent dwelling use to dwelling use on or after October 1, 1983；note, does not change the answer (kinds of housing the data cannot show): low rent public housing developments；note: New dwellings or housing spaces rented for the first time are exempt for the initial rental only.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> Dwellings with four or less housing spaces; provided, however, that this exemption shall be suspended for non-owner occupied dwellings with four or less housing spaces until the end of the state of emergency or six months from adoption of these amendments whichever comes first.
- 原文：> Newly constructed dwellings with 25 or more dwelling units located within a redevelopment area as defined in Section 5 of the Redevelopment Agencies Law, N.J.S.A. 40:55C-5(o), for which the City Council has approved a redevelopment plan, in accordance with Section 17 of the Redevelopment Agencies Law, N.J.S.A. 40:55C-17.
- 原文：> All buildings or structures, hotels, motels or guesthouses which are converted from any previous use as a nonpermanent dwelling to use as a dwelling on or after October 1, 1983.

### r-0201 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code §260-4
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50

### r-0202 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code §260-5
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50

### r-0203 — Jersey City, NJ — rent_increase_limits — Jersey City Mun. Code §260-6
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：exemption only if the owner filed (open question inside its reach): built on or after 1987-06-25；exemption only if the owner filed (open question inside its reach): built on or before 1992-06-25；UNRESOLVED: dwellings certified by the Division of Tenant/Landlord Relations as vacant as of July 1, 1998 are permanently exempt；note: The initial rent for newly constructed housing space rented for the first time is not restricted.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> the provisions of this chapter shall not apply to a new dwelling which is constructed between June 25, 1987, through June 25, 1992, and which is not constructed for occupation by senior citizens, for a period of time not to exceed the period of amortization of any initial mortgage loan obtained for the dwelling, or for 30 years following completion of construction, whichever is less

### r-0153 — Los Angeles, CA — algorithmic_rent_setting — Los Angeles City Council Motion (Sept. 3, 2024)
- 状态：pending_bill；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 80 个在范围内）：pending 80

### r-0156 — Los Angeles, CA — just_cause_eviction — L.A.M.C. §§151.09, 165.03
- 状态：enacted；生效日期：2026-07-01；有效期至：2027-06-30
- 条件：note, does not change the answer (kinds of housing the data cannot show): units covered by the Rent Stabilization Ordinance (RSO) or the Just Cause Ordinance (JCO)；note: Mom and Pop properties (4 or fewer rental units) and single-family dwellings owned by a natural person may pay reduced relocation; reduced amount only for owner, eligible relative or resident manager occupancy.
- 地址结果（共 80 个在范围内）：applies 80
- 原文：> All tenant not- at-fault evictions require payment of relocation assistance and the filing of a Declaration of Intent to Evict form with the Los Angeles Housing Department (LAHD) before evicting tenants from units covered by the Rent Stabilization Ordinance (RSO) or the Just Cause Ordinance (JCO).
- 原文：> Mom and Pop properties may pay reduced relocation assistance payments to their tenants for a good faith eviction for occupancy by the owner or eligible relative, provided that requirements in Section 151.30 of the LAMC are met.

### r-0159 — Los Angeles, CA — just_cause_eviction — Los Angeles Just Cause Ordinance (L.A.M.C. §165.00 et seq.)
- 状态：enacted；生效日期：2026-07-01；有效期至：2027-06-30
- 条件：note, does not change the answer (kinds of housing the data cannot show): Units already regulated by the City's Rent Stabilization Ordinance；note: Amount depends on tenant status (eligible or qualified) and length of tenancy; single-family dwellings owned by a natural person with four or fewer units receive one month's rent; paid per unit, not per tenant.; Tenant has lived in the same unit at least six months or the original lease expired, whichever comes first.
- 地址结果（共 80 个在范围内）：applies 80
- 原文：> The JCO covers most residential properties in the City of Los Angeles that are not regulated by the City’s Rent Stabilization Ordinance (RSO).
- 原文：> In order to apply to a tenancy, it requires that the tenant either has lived in the same unit for at least six months or that their original lease expired, whichever comes first.

### r-0155 — Los Angeles, CA — just_cause_eviction — Los Angeles Rent Stabilization Ordinance (L.A.M.C. §151.00 et seq.)
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：covered if built on or before 1978-10-01；date basis: construction_date
- 地址结果（共 80 个在范围内）：applies 47，omitted: a condition excludes it 25，unknown 8
- **注意：条件使它在 25 个地址上消失**
- 原文：> Generally, the RSO applies to rental properties that were first built on or before October 1, 1978

### r-0157 — Los Angeles, CA — just_cause_eviction — Resident Protections Ordinance (RPO)
- 状态：enacted；生效日期：2026-07-01；有效期至：2027-06-30
- 条件：note: Only low, very low and extremely low income households displaced by demolition for new construction; above low income tenants use the RSO or JCO amounts in Chart A.
- 地址结果（共 80 个在范围内）：applies 80

### r-0154 — Los Angeles, CA — rent_increase_limits — Los Angeles Rent Stabilization Ordinance (L.A.M.C. §151.00 et seq.)
- 状态：enacted；生效日期：2025-07-01；有效期至：2026-06-30
- 条件：covered if built on or before 1978-10-01；date basis: certificate_of_occupancy；note: In condominiums and townhomes the rent amount is not regulated for tenancies that commenced after December 31, 1995.
- 地址结果（共 80 个在范围内）：omitted: outside its valid period 80
- 原文：> Generally, the RSO applies to rental properties that were first built on or before October 1, 1978

### r-0150 — Los Angeles, CA — screening_restrictions — Los Angeles Municipal Code §45.67
- 状态：enacted；生效日期：2020-01-01；有效期至：—
- 条件：无
- 地址结果（共 80 个在范围内）：applies 80
- 原文：> All dwelling units, efficiency dwelling units, guest rooms, and suites, as defined in Section 12.03 of this Code; all housing accommodations as defined in Government Code Section 12927; and duplexes, condominiums, and single family residences in the City of Los Angeles, rented or offered for rent for living or dwelling purposes

### r-0158 — Los Angeles, CA — security_deposits — L.A. Mun. Code §151.06.02
- 状态：enacted；生效日期：2003-01-01；有效期至：—
- 条件：note: Interest accrues only on deposits held at least one year; on termination only a tenant whose deposit was held one year or more may collect unpaid interest.
- 地址结果（共 80 个在范围内）：applies 80

### r-0046 — MA — algorithmic_rent_setting — H.5222
- 状态：pending_bill；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：pending 110

### r-0047 — MA — algorithmic_rent_setting — S.2983
- 状态：pending_bill；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：pending 110

### r-0160 — MA — application_screening_fees — 803 CMR 5.18
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Only where a veterans organization requests the CORI or self-audit for employees, volunteers, or veterans it houses.
- 地址结果（共 110 个在范围内）：applies 110

### r-0044 — MA — application_screening_fees — G.L. c. 186, §15B
- 状态：enacted；生效日期：2025-08-01；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110

### r-0043 — MA — application_screening_fees — Mass. Gen. Laws ch. 112, §87DDD1/2
- 状态：enacted；生效日期：2025-08-01；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110
- 原文：> No person shall engage in the business of finding dwelling accommodations for prospective tenants for a fee unless such person is a licensed broker or salesman as defined in section eighty-seven PP of chapter one hundred and twelve.

### r-0037 — MA — just_cause_eviction — G.L. c. 186, §11
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Nonpayment of rent under a written lease
- 地址结果（共 110 个在范围内）：applies 110
- 原文：> Upon the neglect or refusal to pay the rent due under a written lease, fourteen days' notice to quit, given in writing by the landlord to the tenant, shall be sufficient to determine the lease

### r-0038 — MA — just_cause_eviction — G.L. c. 186, §12
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Notice period depends on the rent-payment interval; for nonpayment, the tenant may cure within ten days.
- 地址结果（共 110 个在范围内）：applies 110

### r-0039 — MA — just_cause_eviction — G.L. c. 186, §18
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110

### r-0040 — MA — just_cause_eviction — G.L. c. 186, §31
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110

### r-0041 — MA — just_cause_eviction — H.3744
- 状态：failed；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：omitted: failed measure 110

### r-0035 — MA — rent_increase_limits — G.L. c. 40P, §4
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner-dependent, no size limit (unknown for every address)；note: Local rent control regulation may not apply to a rental unit that has a fair market rent exceeding $400.
- 地址结果（共 110 个在范围内）：unknown 110
- **注意：所有 110 个地址都是不确定**
- 原文：> nor may such regulation apply to any rental unit that is owned by a person or entity owning less than ten rental units or that has a fair market rent exceeding $400
- 关系 `preempts_local`：> No city or town may enact, maintain or enforce rent control of any kind

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
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110

### r-0161 — MA — screening_restrictions — 803 CMR 5.17
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110

### r-0045 — MA — screening_restrictions — G.L. c. 151B, §4
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110

### r-0163 — MA — screening_restrictions — G.L. c. 186, §15B
- 状态：enacted；生效日期：2025-08-01；有效期至：—
- 条件：note: a lessor who offers a fee in lieu of a security deposit to an approved applicant
- 地址结果（共 110 个在范围内）：applies 110

### r-0042 — MA — security_deposits — G.L. c. 186, §15B
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 110 个在范围内）：applies 110

### r-0175 — NJ — algorithmic_rent_setting — P.L. 2026, c.043
- 状态：enacted；生效日期：2027-07-01；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：not_yet_effective 140
- 关系 `preempts_local`：> A municipality shall be prohibited from enacting an ordinance that conflicts with this act.

### r-0173 — NJ — application_screening_fees — 15 U.S.C.A. §1681m
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：applies 140

### r-0065 — NJ — application_screening_fees — N.J.S.A. 46:8-18.1
- 状态：enacted；生效日期：2026-05-01；有效期至：—
- 条件：at least 3 units；note: Exemption for a licensee of the New Jersey Real Estate Commission unless the licensee is the landlord of the property.
- 地址结果（共 140 个在范围内）：applies 86，omitted: a condition excludes it 1，unknown 53
- **注意：条件使它在 1 个地址上消失**
- 原文：> a dwelling unit located in a one-family or two-family dwelling that is offered for rent
- 原文：> a licensee of the New Jersey Real Estate Commission, unless the licensee is the landlord of the residential rental property

### r-0166 — NJ — application_screening_fees — P.L. 2021, c. 110
- 状态：enacted；生效日期：2022-01-01；有效期至：—
- 条件：owner exemption up to 4 units
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> other than a dwelling unit in an owner-occupied premises of not more than four dwelling units

### r-0170 — NJ — just_cause_eviction — N.J.A.C. 5:27-3.3
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at least 2 units
- 地址结果（共 140 个在范围内）：applies 89，unknown 51
- 原文：> Any building having at least two (2) living units occupied by persons unrelated to each other without private kitchens and bathro oms is a rooming or boarding house if it does not meet one (1) of the exceptions in the Rooming and Boarding House Act

### r-0052 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units；note: A dwelling unit held in trust for, or permanently occupied by, an immediate family member of the owner who has a developmental disability.
- 地址结果（共 140 个在范围内）：applies 86，unknown 54

### r-0053 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner-dependent, no size limit (unknown for every address)
- 地址结果（共 140 个在范围内）：unknown 140
- **注意：所有 140 个地址都是不确定**
- 原文：> Tenants of landlord-occupied two- and three-family dwellings can be removed only when a court issues an order for eviction.

### r-0054 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.28
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Tenant age (62+), permanent disability or qualifying disabled-veteran status, at least one year of residency before the conversion recording date, and family income within the limit (up to 3 times the county average per-person income or $50,000, whichever is greater).
- 地址结果（共 140 个在范围内）：applies 140
- 原文：> To qualify, tenants must : (1) be at least 62 years of age before the d ate of the conversion recording of the condominium or cooperative; or (2) be permanently disabled; or (3) be honorably discharged from any military service under certain circumstances from any branch of the U.S. Armed Forces and disabled at 60% or higher resulting from said service and, (4) live in a building being converted to a condominium, coo

### r-0171 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.40
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Tenants in a qualified county (currently only Hudson County) in a building converted or being converted who were not eligible under the Senior Citizens and Disabled Protected Tenancy Act of 1981.
- 地址结果（共 140 个在范围内）：applies 140
- 原文：> The Tenant Protection Law of 1992 amendment extends protections to qualified tenants in qualified counties in buildings converted or being converted who were not eligible for Protected Tenancy as either Senior Citizens or Disabled Persons under the “Senior Citizens and Disabled Protected Tenancy Act of 1981”

### r-0055 — NJ — just_cause_eviction — N.J.S.A. 2A:18-61.6
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：applies 140

### r-0168 — NJ — just_cause_eviction — N.J.S.A. 2A:39-1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：applies 140
- 原文：> “Self-help” eviction is entry into a dwelling unit and removal of tenants without their consent or without a judgment from a court, are not permitted in New Jersey under any circumstances.

### r-0056 — NJ — just_cause_eviction — N.J.S.A. 2A:42-10.10
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 3 units
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> The law against reprisal applies to all rental properties used for dwelling purposes, including mobile homes, except owner-occupied two- or three-family dwellings.

### r-0172 — NJ — just_cause_eviction — N.J.S.A. 2A:50-69
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Foreclosure as the triggering event; the 90-day notice applies where a buyer wants to personally occupy the property as a primary residence.
- 地址结果（共 140 个在范围内）：applies 140
- 关系 `yields_to_local`：> the federal law does not preempt any State or local law that provides longer time periods or other additional protections for tenants in foreclosure proceedings

### r-0165 — NJ — just_cause_eviction — P.L. 2021, c. 110
- 状态：enacted；生效日期：2022-01-01；有效期至：—
- 条件：owner exemption up to 4 units
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> other than a dwelling unit in an owner-occupied premises of not more than four dwelling units

### r-0048 — NJ — rent_increase_limits — N.J.S.A. 2A:18-61.1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：at least 3 units；owner exemption up to 3 units
- 地址结果（共 140 个在范围内）：applies 86，omitted: a condition excludes it 1，unknown 53
- **注意：条件使它在 1 个地址上消失**
- 原文：> This law may not apply to two - or three-unit owner-occupied premises with two (2) or fewer rental units.

### r-0049 — NJ — rent_increase_limits — N.J.S.A. 2A:18-61.31
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：applies 140

### r-0050 — NJ — rent_increase_limits — N.J.S.A. 2A:42-84.5
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：exempt if newer than 30 years；date basis: construction_date
- 地址结果（共 140 个在范围内）：applies 30，omitted: a condition excludes it 4，unknown 106
- **注意：条件使它在 4 个地址上消失**
- 原文：> newly constructed multiple dwellings shall be exempt from any local rent control ordinances for a period of 30 years following completion of construction of the building

### r-0174 — NJ — screening_restrictions — 15 U.S.C.A. §1681m
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：applies 140

### r-0067 — NJ — screening_restrictions — N.J.S.A. 10:5-12
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units；UNRESOLVED: rooms in an owner- or resident-occupied single home; residences planned exclusively for and occupied by one sex
- 地址结果（共 140 个在范围内）：unknown 140
- **注意：所有 140 个地址都是不确定**
- 原文：> The law applies to all landlord -tenant relationships, except those involving two -family owner occupied dwellings, rooms in an owner or resident -occupied single home, and residences planned exclusively for and occupied by one sex, i.e. YMCA and age -restricted housing, as it pertains to familial status (N.J.S.A. 10:5-5(n)).

### r-0169 — NJ — screening_restrictions — New Jersey Law Against Discrimination
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units；note: Rental of a room or rooms in an owner-occupied one-family dwelling; religious-organization preference; familial-status provision not applied to housing for older persons.
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> The rental of a single apartment or flat in a two-family dwelling, the other occupancy unit of which is occupied by the owner as his/her residence at the time of such rentals
- 原文：> The rental of a room or rooms to another person or persons by the owner or occupant of a one-family dwelling occupied by him/her as his/her residence at the time of such rental

### r-0167 — NJ — screening_restrictions — P.L. 2021, c. 110
- 状态：enacted；生效日期：2022-01-01；有效期至：—
- 条件：owner exemption up to 4 units
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> other than a dwelling unit in an owner-occupied premises of not more than four dwelling units

### r-0058 — NJ — security_deposits — N.J.S.A. 46:8-19 et seq.
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Security deposits for seasonal use or rental (term of not more than 125 consecutive days) are excluded from the deposit-account rules.
- 地址结果（共 140 个在范围内）：applies 140

### r-0059 — NJ — security_deposits — N.J.S.A. 46:8-21
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Higher penalties apply when the tenant receives State or federal financial or rental assistance.
- 地址结果（共 140 个在范围内）：applies 140

### r-0061 — NJ — security_deposits — N.J.S.A. 46:8-21.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 140 个在范围内）：applies 140
- 原文：> real property used for dwelling purposes

### r-0164 — NJ — security_deposits — N.J.S.A. 46:8-26
- 状态：enacted；生效日期：1979-02-22；有效期至：—
- 条件：owner exemption up to 2 units；note: Exemption does not apply where the tenant has given the landlord 30 days written notice invoking the act.
- 地址结果（共 140 个在范围内）：applies 86，unknown 54
- 原文：> The provisions of this act shall apply to all rental premises or units used for dwelling purposes except owner-occupied premises with not more than two rental units where the tenant has failed to provide 30 days written notice to the landlord invoking the provisions of this act.

### r-0064 — NJ — security_deposits — N.J.S.A. 46:8-9.6
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: Applies when a tenant terminates the lease under the Safe Housing Act (domestic violence); does not apply to transient or seasonal rentals.
- 地址结果（共 140 个在范围内）：applies 140

### r-0178 — Newark, NJ — just_cause_eviction — Newark Mun. Code §19:2-11
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：note: senior citizen or disabled tenants in condominium or cooperative conversions
- 地址结果（共 50 个在范围内）：applies 50

### r-0179 — Newark, NJ — just_cause_eviction — Newark Mun. Code §19:2-14
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50

### r-0177 — Newark, NJ — rent_increase_limits — Newark Mun. Code §19:2-18
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：exemption only if the owner filed (open question inside its reach): built within the last 30 years；UNRESOLVED: dwellings vacant at least 18 months or already vacant on the effective date of the section; reconstruction or rehabilitation cost during twelve months exceeds 50% of fair market value
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> The provisions of the Rent Control Ordinance, which limit the periodic or regular increases in base rentals of dwelling units shall not apply to newly constructed multiple dwellings for a period of time not to exceed the period of amortization of any initial mortgage loan obtained for the multiple dwelling, or for 30 years following completion of construction, whichever is less.
- 原文：> Dwellings which become vacant and remain vacant for a minimum of 18 months or dwellings which are already vacant on the effective date of this section shall be exempt for a period of five years from any restrictions in the rent that the landlord may charge
- 原文：> Substantially reconstructed or rehabilitated dwellings shall not be restricted in initial rent charged, if the Rent Control Board has made the following determinations:

### r-0180 — Newark, NJ — rent_increase_limits — Newark Mun. Code §19:2-3
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: newly constructed multiple dwellings (see § 19:2-18.1); vacant dwellings (see § 19:2-18.2)；note, does not change the answer (kinds of housing the data cannot show): public housing; units rehabilitated under federal/state Rental Rehabilitation Programs receiving Section 8 subsidies or housing vouchers; units under a government contract that regulates rent (preempted during the contract)
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> All multiple dwellings, as defined in subsection 19:2-2, are subject to Rent Control pursuant to this Title XIX Rent Control
- 原文：> EXEMPTIONS — Shall mean dwellings to which this chapter shall not apply.
- 原文：> if the authority of that governmental agency supersedes the authority of the City of Newark to regulate such rents, then the application of this chapter shall be preempted during the period of governmental agency regulation specified in the contract.

### r-0185 — Newark, NJ — rent_increase_limits — Newark Mun. Code §2:10-11
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50
- 原文：> UNCONSCIONABLE RENT — Shall mean any rental increase for residential properties

### r-0181 — Newark, NJ — rent_increase_limits — Newark, N.J., Code §2:10-1.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: only HOME-assisted units receiving HOME Program funds are covered
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> The DHA must review and approve rents proposed by the owner for units subject to the maximum rent limitations

### r-0183 — Newark, NJ — rent_increase_limits — Newark, NJ Mun. Code §19:2-18.4
- 状态：enacted；生效日期：2024-09-18；有效期至：—
- 条件：note: Applies where a landlord rehabilitates a vacant apartment unit spending at least 12 months of actual monthly rent per unit.
- 地址结果（共 50 个在范围内）：applies 50

### r-0184 — Newark, NJ — rent_increase_limits — Newark, NJ Mun. Code §19:2-22
- 状态：enacted；生效日期：2024-09-18；有效期至：—
- 条件：note: Applies to any tenant; covers rent increases granted by the Rent Control Board.
- 地址结果（共 50 个在范围内）：applies 50

### r-0176 — Newark, NJ — rent_increase_limits — Newark, NJ Mun. Code §19:2-8
- 状态：enacted；生效日期：2024-09-18；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50

### r-0182 — Newark, NJ — screening_restrictions — Newark, N.J., Code §2:10-1.2
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: only HOME-assisted units receiving HOME Program funds are covered
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> The owner cannot refuse to lease HOME-assisted units to a certificate or voucher holder under 24 CFR part 982

### r-0187 — Newark, NJ — screening_restrictions — Newark, NJ, Code §2:31-15
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50

### r-0186 — Newark, NJ — screening_restrictions — Newark, NJ, Rev. Gen. Ordinances ch. 2:31, art. 1
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：owner exemption up to 2 units
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> the provisions of this Article shall not apply to the rental:
- 原文：> Of a single apartment or flat in a two family dwelling, the other occupancy unit of which is occupied by the owner as his/her residence
- 原文：> Of a room or rooms to another person or persons by the owner or occupant of one-family dwelling occupied by him/her as his/her residence

### r-0188 — San Diego, CA — algorithmic_rent_setting — San Diego Mun. Code §§98.1101–98.1104
- 状态：enacted；生效日期：2025-06-21；有效期至：—
- 条件：无
- 地址结果（共 50 个在范围内）：applies 50
- 原文：> It is unlawful for a landlord to use an algorithmic device to set rental rates or occupancy levels for residential rental property.

### r-0189 — San Diego, CA — just_cause_eviction — San Diego Mun. Code §98.0701 et seq.
- 状态：enacted；生效日期：2023-06-24；有效期至：—
- 条件：note: A senior or disabled tenant is entitled to three months' actual rent as relocation assistance instead of two months.
- 地址结果（共 50 个在范围内）：applies 50

### r-0095 — San Diego, CA — just_cause_eviction — San Diego Mun. Code §98.0704
- 状态：enacted；生效日期：2023-06-24；有效期至：—
- 条件：exempt if newer than 15 years；owner-dependent, no size limit (unknown for every address)；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): housing restricted by deed or government agreement as affordable to very low, low or moderate income; property alienable separate from title to other units, landlord not a corporation, REIT or LLC with corporate member, giving written notice；note: Fixed-term lease of three months or less; occupancy of 30 days or less; tenant sharing bathroom or kitchen with owner-occupant landlord.
- 地址结果（共 50 个在范围内）：unknown 50
- **注意：所有 50 个地址都是不确定**
- 原文：> (k) housing that has been issued a certificate of occupancy within the previous 15 years, unless the housing is a mobilehome; and
- 原文：> (j) a property containing two separate dwelling units within a single structure in which the landlord occupies one of the dwelling units as the landlord’s principal place of residence at the beginning of the tenancy, so long as the landlord continues in occupancy;
- 原文：> (h) residential rental property in which the tenant shares bathroom or kitchen facilities with the landlord who maintains their principal residence at the residential rental property;

### r-0190 — San Diego, CA — screening_restrictions — San Diego Mun. Code §98.0803
- 状态：enacted；生效日期：2018-10-18；有效期至：—
- 条件：note: Excepted where the owner or a family member resides in the same residential building as the tenant and shares a bathroom or kitchen facility with the tenant or prospective tenant.
- 地址结果（共 50 个在范围内）：applies 50
- 原文：> Nothing in this Division shall apply to any tenancy in which the owner or any member of his or her family resides within the same residential building as the tenant and the owner or family member share a bathroom or a kitchen facility with the tenant or prospective tenant.

### r-0109 — San Francisco, CA — algorithmic_rent_setting — S.F. Admin. Code §37.10C
- 状态：enacted；生效日期：2024-10-14；有效期至：—
- 条件：无
- 地址结果（共 80 个在范围内）：applies 80
- 原文：> The law prohibits the sale or use of algorithmic devices to set rents or manage occupancy levels for residential units in San Francisco.

### r-0194 — San Francisco, CA — just_cause_eviction — S.F. Admin. Code ch. 37
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：无
- 地址结果（共 80 个在范围内）：applies 80

### r-0103 — San Francisco, CA — just_cause_eviction — S.F. Admin. Code §37.9
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：UNRESOLVED: rental unit covered by the Rent Ordinance；note: Applies to tenancies in covered rental units, including tenancies exempt from the Ordinance's rent increase limits.
- 地址结果（共 80 个在范围内）：unknown 80
- **注意：所有 80 个地址都是不确定**
- 原文：> In order to evict a tenant from a rental unit covered by the Rent Ordinance, a landlord must have a "just cause" reason that is the dominant motive for pursuing the eviction.

### r-0105 — San Francisco, CA — just_cause_eviction — S.F. Admin. Code §37.9C
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：note: Relocation is owed for owner/relative move-in, demolition, temporary capital improvement, substantial rehabilitation and Ellis Act evictions; the amount depends on the notice service date, with an extra amount for elderly (60+ or 62+) or disabled tenants.
- 地址结果（共 80 个在范围内）：applies 80

### r-0191 — San Francisco, CA — rent_increase_limits — S.F. Admin. Code ch. 37
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：covered if built on or before 1979-06-13；date basis: certificate_of_occupancy；note, does not change the answer (kinds of housing the data cannot show): rent regulated by another government agency；note: Tenancies eligible for a rent increase under the Costa-Hawkins Rental Housing Act.
- 地址结果（共 80 个在范围内）：applies 71，omitted: a condition excludes it 7，unknown 2
- **注意：条件使它在 7 个地址上消失**
- 原文：> For rent-controlled units, the annual allowable increase amount effective March 1, 2026 through February 28, 2027 is 1.6%.
- 原文：> This includes tenancies in newly constructed rental units that first obtained a Certificate of Occupancy after June 13, 1979, tenancies that are eligible for a rent increase under the Costa-Hawkins Rental Housing Act, and some tenancies where the rent is regulated by another government agency.

### r-0195 — San Francisco, CA — security_deposits — S.F. Admin. Code ch. 37
- 状态：enacted；生效日期：2026-03-01；有效期至：2027-02-28
- 条件：无
- 地址结果（共 80 个在范围内）：applies 80

### r-0198 — Santa Ana, CA — algorithmic_rent_setting — Santa Ana Mun. Code ch. 9, art. XXIV
- 状态：enacted；生效日期：原文未载明；有效期至：—
- 条件：无
- 地址结果（共 0 个在范围内）：—

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
- 条件：exempt if newer than 15 years；date basis: construction_date；note, does not change the answer (kinds of housing the data cannot show): deed-restricted affordable housing；note: Applies to tenancies after 30 days
- 地址结果（共 0 个在范围内）：—
- 原文：> The Just Cause Ordinance shall not apply to certain types of residential property, including housing produced in the last 15 years; deed-restricted affordable housing; hotel and transient occupancy; hospital and care facilities; dormitories; and other shared living quarters.
- 原文：> After 30 days, an owner shall not terminate a tenancy without just cause, which shall be stated in a written notice.

### r-0192 — Santa Ana, CA — rent_increase_limits — Rent Stabilization and Just Cause Eviction Ordinance
- 状态：enacted；生效日期：2026-09-01；有效期至：2027-08-31
- 条件：无
- 地址结果（共 0 个在范围内）：—

### r-0110 — Santa Ana, CA — rent_increase_limits — Santa Ana Rent Stabilization Ordinance
- 状态：enacted；生效日期：2021-11-19；有效期至：—
- 条件：covered if built on or before 1995-02-01；date basis: construction_date
- 地址结果（共 0 个在范围内）：—
- 原文：> The rent cap does not apply to residential buildings constructed after February 1, 1995, or to mobile home spaces offered for rent after January 1, 1990.

