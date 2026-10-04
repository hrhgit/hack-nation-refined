# Extraction report

- as of **2026-10-01**
- answer files read: 15 | records parsed: 152 | accepted: 111 | rejected and still open: 41 (+0 rejected earlier and since fixed) | rules after merging: **91**
- packets done: **41 / 65**

## Packets still open (24)

States: needs_fix 24

| packet | state | detail |
|---|---|---|
| D006-01 | needs_fix | 4 record(s) rejected |
| D007-01 | needs_fix | 2 record(s) rejected |
| D010-01 | needs_fix | 1 record(s) rejected |
| D013-01 | needs_fix | 1 record(s) rejected |
| D014-01 | needs_fix | 1 record(s) rejected |
| D016-01 | needs_fix | 1 record(s) rejected |
| D023-01 | needs_fix | 1 record(s) rejected |
| D024-01 | needs_fix | 1 record(s) rejected |
| D025-01 | needs_fix | 4 record(s) rejected |
| D025-02 | needs_fix | 1 record(s) rejected |
| D026-01 | needs_fix | 3 record(s) rejected |
| D027-01 | needs_fix | 2 record(s) rejected |
| D040-01 | needs_fix | 2 record(s) rejected |
| D041-01 | needs_fix | 2 record(s) rejected |
| D042-01 | needs_fix | 1 record(s) rejected |
| D043-01 | needs_fix | 2 record(s) rejected |
| D043-02 | needs_fix | 2 record(s) rejected |
| D049-02 | needs_fix | 1 record(s) rejected |
| D051-01 | needs_fix | 1 record(s) rejected |
| D052-01 | needs_fix | 4 record(s) rejected |
| D053-01 | needs_fix | 1 record(s) rejected |
| D067-03 | needs_fix | 1 record(s) rejected |
| D084-01 | needs_fix | 1 record(s) rejected |
| D085-01 | needs_fix | 1 record(s) rejected |

Run `python run.py bundle` to get paste files for exactly these packets.

## Rejected records (41)

These did not enter rules.json. `bundle` asks the model to fix them.

- **D006-01** `Berkeley Rent Ordinance, Measure BB: coverage of s` Measure BB coverage of shared-facility and governm: one record per law and category: you also wrote 'Measure BB 5% cap on Annual General Adjustments' for Berkeley Rent Ordinance, Measure BB (rent_increase_limits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D006-01** `Berkeley Rent Ordinance, Measure BB: just cause, f` Measure BB bar on eviction for refusing a new leas: one record per law and category: you also wrote 'Measure BB nonpayment eviction threshold' for Berkeley Rent Ordinance, Measure BB (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D006-01** `Berkeley Rent Ordinance, Measure BB: just cause, l` Measure BB limits on lease-breach evictions: one record per law and category: you also wrote 'Measure BB nonpayment eviction threshold' for Berkeley Rent Ordinance, Measure BB (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D006-01** `Berkeley Rent Ordinance, Measure BB: eviction noti` Measure BB eviction notice content and Rent Board : one record per law and category: you also wrote 'Measure BB nonpayment eviction threshold' for Berkeley Rent Ordinance, Measure BB (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D007-01** `California state law, photographs after regaining ` California photographs before deposit deductions: one record per law and category: you also wrote 'California security deposit return and itemization' for California state law (security_deposits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D007-01** `California state law, photographs at start of tena` California move-in photographs of the unit: one record per law and category: you also wrote 'California security deposit return and itemization' for California state law (security_deposits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D010-01** `Boston Fair Chance Tenant Selection Policy: credit` Boston Fair Chance Tenant Selection Policy credit : one record per law and category: you also wrote 'Boston Fair Chance Tenant Selection Policy criminal-history ' for Boston Fair Chance Tenant Selection Policy (screening_restrictions). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D013-01** `Housing Stability Notification Act, Sec. 10-11.7: ` Housing Stability Notification Act notice to tenan: one record per law and category: you also wrote 'Housing Stability Notification Act landlord filing with the ' for Housing Stability Notification Act, §10-11.7 (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D014-01** `Housing Stability Notification Act, Sec. 10-11.7: ` Housing Stability Notification Act notice copy to : one record per law and category: you also wrote 'Housing Stability Notification Act tenant notice, coverage a' for Housing Stability Notification Act, §10-11.7 (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D016-01** `California Fair Employment and Housing Act: crimin` Criminal-history screening limits: one record per law and category: you also wrote 'Source-of-income and voucher protection' for California Fair Employment and Housing Act (screening_restrictions). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D023-01** `Cal. Civ. Code § 1946.2: relocation assistance or ` Relocation assistance or rent waiver for no-fault : one record per law and category: you also wrote 'California statewide just cause for termination of tenancy' for Cal. Civ. Code §1946.2 (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D024-01** `Cal. Civ. Code § 1947.12: no more than two increas` Limit of two rent increases in any 12-month period: one record per law and category: you also wrote 'Tenant Protection Act annual rent increase cap' for Cal. Civ. Code §1947.12 (rent_increase_limits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D025-01** `Cal. Civ. Code § 1950.5: two months’ rent cap, sma` California two months' rent security cap for small: one record per law and category: you also wrote 'California security deposit cap, one month's rent' for Cal. Civ. Code §1950.5 (security_deposits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D025-01** `Cal. Civ. Code § 1950.5: service member higher sec` California service member higher security, stateme: one record per law and category: you also wrote 'California security deposit cap, one month's rent' for Cal. Civ. Code §1950.5 (security_deposits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D025-01** `Cal. Civ. Code § 1950.5: photographs of the unit, ` California photographs of the unit for security de: one record per law and category: you also wrote 'California security deposit cap, one month's rent' for Cal. Civ. Code §1950.5 (security_deposits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D025-01** `Cal. Civ. Code § 1950.5: return of security, 21 ca` California security return and itemization, 21 cal: one record per law and category: you also wrote 'California security deposit cap, one month's rent' for Cal. Civ. Code §1950.5 (security_deposits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D025-02** `Cal. Civ. Code § 1950.5: nonrefundable security ch` California ban on nonrefundable security provision: one record per law and category: you also wrote 'California bad faith retention of security, statutory damage' for Cal. Civ. Code §1950.5 (security_deposits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D026-01** `Cal. Civ. Code § 1950.6: screening fee refund requ` California application screening fee refund condit: one record per law and category: you also wrote 'California application screening fee cap' for Cal. Civ. Code §1950.6 (application_screening_fees). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D026-01** `Cal. Civ. Code § 1950.6: screening fee receipt and` California screening fee receipt and credit report: one record per law and category: you also wrote 'California application screening fee cap' for Cal. Civ. Code §1950.6 (application_screening_fees). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D026-01** `Cal. Civ. Code § 1950.6: screening fee prohibited ` California bar on screening fees when no unit is a: one record per law and category: you also wrote 'California application screening fee cap' for Cal. Civ. Code §1950.6 (application_screening_fees). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D027-01** `Cal. Gov. Code § 12955: credit history, alternativ` California credit history alternative evidence wit: one record per law and category: you also wrote 'California source of income housing discrimination ban' for Cal. Gov. Code §12955 (screening_restrictions). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D027-01** `Cal. Gov. Code § 12955: income standard, aggregate` California income standard, aggregate income of co: one record per law and category: you also wrote 'California source of income housing discrimination ban' for Cal. Gov. Code §12955 (screening_restrictions). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D040-01** `Los Angeles Just Cause Ordinance: just cause evict` LA Just Cause Ordinance: just cause and relocation: one record per law and category: you also wrote 'LA non-payment eviction threshold, Fair Market Rent' for Los Angeles Just Cause Ordinance (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D040-01** `Los Angeles Just Cause Ordinance: eviction notice ` LA eviction notices must be filed with LAHD: one record per law and category: you also wrote 'LA non-payment eviction threshold, Fair Market Rent' for Los Angeles Just Cause Ordinance (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D041-01** `Los Angeles Rent Stabilization Ordinance: addition` RSO additional tenant and dependent increase: one record per law and category: you also wrote 'RSO utility percentage increase prohibited' for Los Angeles Rent Stabilization Ordinance (rent_increase_limits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D041-01** `Los Angeles Rent Stabilization Ordinance: allowabl` RSO allowable rent increase, once every 12 months: one record per law and category: you also wrote 'RSO utility percentage increase prohibited' for Los Angeles Rent Stabilization Ordinance (rent_increase_limits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D042-01** `Los Angeles Rent Stabilization Ordinance: utility ` LA RSO utility percentage increase barred: one record per law and category: you also wrote 'LA RSO annual allowable rent increase 2025-26' for Los Angeles Rent Stabilization Ordinance (rent_increase_limits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D043-01** `LAMC § 165.06, single-family dwelling owned by nat` LA JCO relocation for single-family dwelling owned: one record per law and category: you also wrote 'LA RSO/JCO relocation assistance amounts 2026-27' for LAMC §165.06 (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D043-01** `LAMC § 165.06, relocation assistance payment timin` LA relocation assistance payment timing: one record per law and category: you also wrote 'LA RSO/JCO relocation assistance amounts 2026-27' for LAMC §165.06 (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D043-02** `LAMC § 165.06, single-family dwelling owned by nat` LA JCO relocation for single-family dwelling owned: one record per law and category: you also wrote 'LA RSO/JCO relocation assistance amounts 2026-27' for LAMC §165.06 (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D043-02** `LAMC § 165.06, relocation assistance payment timin` LA relocation assistance payment timing: one record per law and category: you also wrote 'LA RSO/JCO relocation assistance amounts 2026-27' for LAMC §165.06 (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D049-02** `G.L. c. 151B, § 4: prohibited inquiries and record` No inquiries or records on protected traits, other: one record per law and category: you also wrote 'Source-of-income protection for public assistance and housin' for G.L. c. 151B, §4 (screening_restrictions). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D051-01** `G.L. c. 186, § 12, fourteen-day notice to quit for` Fourteen days' notice to quit for nonpayment by a : one record per law and category: you also wrote 'Three months' notice to determine an estate at will' for G.L. c. 186, §12 (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D052-01** `G.L. c. 186, § 15B: security deposit maximum` Security deposit cap equal to one month's rent: one record per law and category: you also wrote 'Fee in lieu of a security deposit capped at one month's rent' for G.L. c. 186, §15B (security_deposits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D052-01** `G.L. c. 186, § 15B: security deposit account and i` Security deposit held in a separate interest-beari: one record per law and category: you also wrote 'Fee in lieu of a security deposit capped at one month's rent' for G.L. c. 186, §15B (security_deposits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D052-01** `G.L. c. 186, § 15B: return of security deposit and` Return of security deposit within thirty days of t: one record per law and category: you also wrote 'Fee in lieu of a security deposit capped at one month's rent' for G.L. c. 186, §15B (security_deposits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D052-01** `G.L. c. 186, § 15B: transfer of security deposit t` Transfer of security deposit to a successor landlo: one record per law and category: you also wrote 'Fee in lieu of a security deposit capped at one month's rent' for G.L. c. 186, §15B (security_deposits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D053-01** `G.L. c. 186, § 18: reprisals against tenants` Damages for reprisals against a tenant: one record per law and category: you also wrote 'Rebuttable presumption of reprisal for termination or rent i' for G.L. c. 186, §18 (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D067-03** `N.J.S.A. 2A:18-61.1` New Jersey Anti-Eviction Act grounds for eviction: one record per law and category: you also wrote 'Relocation assistance for certain Anti-Eviction Act eviction' for N.J.S.A. 2A:18-61.1 (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D084-01** `Santa Ana Rent Stabilization Ordinance: maximum re` Santa Ana maximum rent increase cap: one record per law and category: you also wrote 'Santa Ana annual allowable rent increase 2026-27' for Santa Ana Rent Stabilization Ordinance (rent_increase_limits). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date
- **D085-01** `Santa Ana Just Cause Eviction Ordinance: relocatio` Santa Ana no-fault relocation assistance: one record per law and category: you also wrote 'Santa Ana just cause termination requirement' for Santa Ana Just Cause Eviction Ordinance (just_cause_eviction). Merge this record into it: put the extra details in requirement, exemptions or penalty and keep a single headline key_value and effective_date

## Rules to check by hand (6 of 91)

- **r-0022** CA | rent_increase_limits | Cal. Civ. Code §1947.12
    - warning: key_value numbers not found in D040: 7
    - conflict: Subdivision (h) applies the cap to increases occurring on or after March 15, 2019, while subdivision (n) states the section became operative April 1, 2024. | Sources disagree: effective_date: D024 says 2024-04-01, D040 says 2024-08-01; key_value: D024 says '5% + CPI, max 10% per 12-month period', D040 says '5% + CPI, max 10%; 8.9% for 2024-08-01 to 2025-07-31'
- **r-0005** CA | application_screening_fees | Cal. Civ. Code §1950.6
    - conflict: Sources disagree: effective_date: D026 says 1998-01-01, D005 says 2026; key_value: D026 says '$30 per applicant, adjusted annually by CPI', D005 says '$68.96 (2026 screening fee cap)'
- **r-0127** Los Angeles, CA | rent_increase_limits | Los Angeles Rent Stabilization Ordinance
    - conflict: Sources disagree: effective_date: D041 says 2026-02-02, D042 says 2025-07-01; key_value: D041 says '0% utility increase', D042 says '3%'
- **r-0099** San Diego, CA | algorithmic_rent_setting | San Diego Mun. Code §98.1103
    - conflict: Effective date is the thirtieth day after final passage, but the date of final passage is blank in this packet.
- **r-0131** San Francisco, CA | rent_increase_limits | S.F. Rent Ordinance
    - conflict: Sources disagree: key_value: D079 says 'certificate of occupancy after June 13, 1979', D083 says '1.6%'
- **r-0110** Santa Ana, CA | rent_increase_limits | Santa Ana Rent Stabilization Ordinance
    - conflict: Sources disagree: effective_date: D084 says 2026-09-01, D085 says 2021-11-19; key_value: D084 says '2.87%, Sept 1, 2026 through Aug 31, 2027', D085 says '3% per year or 80% of CPI change, whichever is lower'

## Sources that disagree

- CA / application_screening_fees Cal. Civ. Code §1950.6
    - effective_date: D026 says 1998-01-01, D005 says 2026
    - key_value: D026 says '$30 per applicant, adjusted annually by CPI', D005 says '$68.96 (2026 screening fee cap)'
- CA / rent_increase_limits Cal. Civ. Code §1947.12
    - effective_date: D024 says 2024-04-01, D040 says 2024-08-01
    - key_value: D024 says '5% + CPI, max 10% per 12-month period', D040 says '5% + CPI, max 10%; 8.9% for 2024-08-01 to 2025-07-31'
- Los Angeles, CA / rent_increase_limits Los Angeles Rent Stabilization Ordinance
    - effective_date: D041 says 2026-02-02, D042 says 2025-07-01
    - key_value: D041 says '0% utility increase', D042 says '3%'
- San Francisco, CA / rent_increase_limits S.F. Rent Ordinance
    - key_value: D079 says 'certificate of occupancy after June 13, 1979', D083 says '1.6%'
- Santa Ana, CA / rent_increase_limits Santa Ana Rent Stabilization Ordinance
    - effective_date: D084 says 2026-09-01, D085 says 2021-11-19
    - key_value: D084 says '2.87%, Sept 1, 2026 through Aug 31, 2027', D085 says '3% per year or 80% of CPI change, whichever is lower'

## Possible duplicates (same jurisdiction and category, overlapping citations)

- MA / just_cause_eviction: `G.L. c. 186, §11` vs `G.L. c. 186, §12`
- MA / just_cause_eviction: `G.L. c. 186, §11` vs `G.L. c. 186, §18`
- MA / just_cause_eviction: `G.L. c. 186, §11` vs `G.L. c. 186, §31`
- MA / just_cause_eviction: `G.L. c. 186, §12` vs `G.L. c. 186, §18`
- MA / just_cause_eviction: `G.L. c. 186, §12` vs `G.L. c. 186, §31`
- MA / just_cause_eviction: `G.L. c. 186, §18` vs `G.L. c. 186, §31`
- NJ / algorithmic_rent_setting: `P.L. 2026, c.43 §4` vs `P.L. 2026, c.43 §6`

## Coverage matrix

| jurisdiction | rent | just cause | deposit | app fees | screening | algo |
|---|---|---|---|---|---|---|
| CA | 1 | 4 | 3 | 1 | 3 | 1 |
| NJ | 4 | 6 | 7 | 2 | 5 | 2 (2N) |
| MA | 2 (1F) | 5 (1F) | 1 | 2 | 1 | 2 (2P) |
| Los Angeles, CA | 1 | 5 | · | · | · | 1 (1P) |
| San Francisco, CA | 2 | 4 | 1 | · | 1 | 1 |
| San Diego, CA | · | 3 | · | · | 1 | 1 |
| Berkeley, CA | 3 | 3 | 1 | 2 | 1 | 1 |
| Santa Ana, CA | 1 | 1 | · | · | · | · |
| Jersey City, NJ | 1 | · | · | · | · | · |
| Hoboken, NJ | · | · | · | · | · | · |
| Newark, NJ | · | · | · | · | · | · |
| Boston, MA | · | 1 | · | · | 2 | · |
| Cambridge, MA | · | · | · | · | 1 | · |

`·` = no rule extracted. N = not yet effective, P = pending bill, F = failed. An empty cell is correct for some cells (e.g. MA has no rent control): check, do not assume.

## Blocks left out of very long documents (check nothing you need is here)

- D067: 26 of 44 blocks left out (78,518 chars)
    - block 1 (4171 chars): 1
    - block 2 (1114 chars): 2. Landlord and tenant are required to include their names in the lease agreement.
    - block 3 (3734 chars): 1. Lead paint EPA approved information pamphlet (N.J.A.C. 5:10-6.6);
    - block 4 (5728 chars): 4
    - block 5 (1306 chars): 6
    - block 6 (5073 chars): 2. If the tenant fails to properly care for the pet;
    - block 9 (5904 chars): 11
    - block 13 (3975 chars): receipted first class mail addressed to the tenant at tenant’s last known address and at any
    - block 16 (5934 chars): 21
    - block 17 (4591 chars): writing within seven (7) days after filing the amended statement. In any eviction action by a
    - block 18 (5964 chars): 24
    - block 19 (4030 chars): tenant will supply heat to a dwelling unit when the unit is served by separate heating equipment
    - block 20 (1749 chars): 27
    - block 21 (4282 chars): § 4851 et al.).
    - block 22 (1841 chars): 1. Public Water Systems:
    - block 23 (1153 chars): 2. Private Water Systems:
    - block 24 (997 chars): 1.  Repair and Deduct
    - block 25 (5934 chars): 2. The tenant must not have caused the condition.
    - block 35 (2329 chars): 43
    - block 37 (1037 chars): 45
    - block 38 (978 chars): VICINAGE OMBUDSMAN TELEPHONE NUMBERS
    - block 39 (718 chars): STATE OF NEW JERSEY
    - block 40 (740 chars): ATLANTIC COUNTY
    - block 41 (708 chars): NEWARK, NJ 07102
    - block 42 (701 chars): FREEHOLD, NJ 07728
    - block 43 (3827 chars): CENTRAL JERSEY LEGAL SERVICES

