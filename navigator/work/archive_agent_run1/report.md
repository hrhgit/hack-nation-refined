# Extraction report

- as of **2026-10-01**
- answer files read: 108 | records parsed: 149 | accepted: 149 | rejected and still open: 0 (+0 rejected earlier and since fixed) | rules after merging: **120**
- packets done: **108 / 108**

## Packets still open (0)

None. Every packet has a complete, clean answer.

## Rules to check by hand (12 of 120)

- **r-0022** CA | rent_increase_limits | Cal. Civ. Code §1947.12
    - warning: applicability.date_basis differs between sources: D024 says certificate_of_occupancy, D040 says construction_date
    - conflict: The section is operative April 1, 2024, but subdivision (h) says it applies to rent increases occurring on or after March 15, 2019. | Sources disagree: effective_date: D024 says 2024-04-01, D040 says 2024-08-01; key_value: D024 says '5% + CPI, or 10%, whichever is lower, per 12 months', D040 says '5% + CPI, max 10%; 8.9% (Aug 1, 2024–Jul 31, 2025)'
- **r-0005** CA | application_screening_fees | Cal. Civ. Code §1950.6
    - conflict: Sources disagree: effective_date: D026 says 2026-01-01, D005 says 2026; key_value: D026 says '$30 per applicant, CPI-adjusted annually', D005 says '$68.96 (2026)'
- **r-0160** MA | application_screening_fees | 803 CMR 5.18
    - warning: D056 never mentions anything about application_screening_fees
- **r-0164** NJ | security_deposits | N.J.S.A. 46:8-26
    - warning: D064 never mentions anything about security_deposits
- **r-0136** Berkeley, CA | rent_increase_limits | Berkeley Mun. Code ch. 13.76
    - warning: applicability.built_on_or_before differs between sources: D006 says 1980, D009 says 1980-06
- **r-0134** Berkeley, CA | just_cause_eviction | Berkeley Mun. Code ch. 13.76
    - conflict: Sources disagree: key_value: D004 says '$19,413 standard; $6,471 additional (1.5% CPI adjustment)', D006 says "at least 1 month's Fair Market Rent"
- **r-0140** Hoboken, NJ | rent_increase_limits | Hoboken Mun. Code §155-5
    - conflict: Sources disagree: key_value: D033 says '5% or CPI differential, whichever is less, per 12 months', D032 says '5% or CPI differential, whichever is less'
- **r-0154** Los Angeles, CA | rent_increase_limits | Los Angeles Rent Stabilization Ordinance (L.A.M.C. §151.00 et seq.)
    - conflict: Sources disagree: key_value: D042 says '3% (July 1, 2025 - June 30, 2026)', D041 says 'once every 12 months'
- **r-0188** San Diego, CA | algorithmic_rent_setting | San Diego Mun. Code §§98.1101–98.1104
    - conflict: Sources disagree: lifecycle: D074 says enacted, D076 says pending_bill
- **r-0191** San Francisco, CA | rent_increase_limits | S.F. Admin. Code ch. 37
    - conflict: Sources disagree: key_value: D080 says '1.6% (3/1/2026-2/28/2027)', D083 says '1.6% (March 1, 2026 – February 28, 2027)'
- **r-0198** Santa Ana, CA | algorithmic_rent_setting | Santa Ana Mun. Code ch. 9, art. XXIV
    - warning: quoted_span realigned to the source (fuzzy match, 0.87)
    - warning: key_value numbers not found in D086: 1000
- **r-0196** Santa Ana, CA | algorithmic_rent_setting | Santa Ana Mun. Code §8-3702
    - warning: effective_date 2026-04-02 does not appear in D086: check it
    - warning: key_value numbers not found in D086: 1000

## Sources that disagree

- Berkeley, CA / just_cause_eviction Berkeley Mun. Code ch. 13.76
    - key_value: D004 says '$19,413 standard; $6,471 additional (1.5% CPI adjustment)', D006 says "at least 1 month's Fair Market Rent"
- CA / application_screening_fees Cal. Civ. Code §1950.6
    - effective_date: D026 says 2026-01-01, D005 says 2026
    - key_value: D026 says '$30 per applicant, CPI-adjusted annually', D005 says '$68.96 (2026)'
- CA / rent_increase_limits Cal. Civ. Code §1947.12
    - effective_date: D024 says 2024-04-01, D040 says 2024-08-01
    - key_value: D024 says '5% + CPI, or 10%, whichever is lower, per 12 months', D040 says '5% + CPI, max 10%; 8.9% (Aug 1, 2024–Jul 31, 2025)'
- Hoboken, NJ / rent_increase_limits Hoboken Mun. Code §155-5
    - key_value: D033 says '5% or CPI differential, whichever is less, per 12 months', D032 says '5% or CPI differential, whichever is less'
- Los Angeles, CA / rent_increase_limits Los Angeles Rent Stabilization Ordinance (L.A.M.C. §151.00 et seq.)
    - key_value: D042 says '3% (July 1, 2025 - June 30, 2026)', D041 says 'once every 12 months'
- San Diego, CA / algorithmic_rent_setting San Diego Mun. Code §§98.1101–98.1104
    - lifecycle: D074 says enacted, D076 says pending_bill
- San Francisco, CA / rent_increase_limits S.F. Admin. Code ch. 37
    - key_value: D080 says '1.6% (3/1/2026-2/28/2027)', D083 says '1.6% (March 1, 2026 – February 28, 2027)'

## Possible duplicates (same jurisdiction and category, overlapping citations)

- MA / just_cause_eviction: `G.L. c. 186, §11` vs `G.L. c. 186, §12`
- MA / just_cause_eviction: `G.L. c. 186, §11` vs `G.L. c. 186, §18`
- MA / just_cause_eviction: `G.L. c. 186, §11` vs `G.L. c. 186, §31`
- MA / just_cause_eviction: `G.L. c. 186, §12` vs `G.L. c. 186, §18`
- MA / just_cause_eviction: `G.L. c. 186, §12` vs `G.L. c. 186, §31`
- MA / just_cause_eviction: `G.L. c. 186, §18` vs `G.L. c. 186, §31`
- MA / screening_restrictions: `803 CMR 5.00` vs `803 CMR 5.17`

## Coverage matrix

| jurisdiction | rent | just cause | deposit | app fees | screening | algo |
|---|---|---|---|---|---|---|
| CA | 1 | 2 | 2 | 1 | 3 | 1 |
| NJ | 3 | 10 | 5 | 3 | 4 | 1 (1N) |
| MA | 3 (2F) | 5 (1F) | 1 | 3 | 4 | 2 (2P) |
| Los Angeles, CA | 1 | 4 | 1 | · | 1 | 1 (1P) |
| San Francisco, CA | 1 | 3 | 1 | · | · | 1 |
| San Diego, CA | · | 2 | · | · | 1 | 1 |
| Berkeley, CA | 2 | 1 | 1 | 1 | 1 | 1 |
| Santa Ana, CA | 2 | 2 | · | · | · | 2 |
| Jersey City, NJ | 7 | · | · | · | · | 1 |
| Hoboken, NJ | 9 | 1 | · | · | · | 1 |
| Newark, NJ | 7 | 2 | · | · | 3 | · |
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
- D070: 31 of 78 blocks left out (40,409 chars)
    - block 5 (2779 chars): Downloaded from https://ecode360.com/NE4043 on 2026-10-03
    - block 9 (784 chars): § 19:2-4. RENT REBATE. [Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024 by Ord. No.
    - block 11 (1357 chars): § 19:2-5.2. Petition for Surcharge. [Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024 by Ord.
    - block 13 (713 chars): § 19:2-6. TAX DECREASES.
    - block 14 (1147 chars): § 19:2-6.2. Tax Appeal, Reduction. [Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024 by Ord.
    - block 15 (1740 chars): § 19:2-7. MAJOR NEW IMPROVEMENTS; ADDITIONAL RENT.
    - block 16 (828 chars): § 19:2-7.2. Increase Prorated. [Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024 by Ord. No.
    - block 17 (1133 chars): § 19:2-7.3. Applicability; Notification. [Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024 by
    - block 19 (757 chars): § 19:2-8.2. Code Violations. [Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024 by Ord. No.
    - block 21 (780 chars): § 19:2-8.3. Submission of Records and Proofs. [Ord. 6 PSF-A(S), 9-5-2017; amended
    - block 22 (2901 chars): § 19:2-8.3                                                                                  § 19:2-8
    - block 26 (1070 chars): § 19:2-8.8. Excessive Purchase Price; Efficient Operator. [Ord. 6 PSF-A(S), 9-5-2017;
    - block 28 (763 chars): § 19:2-9.2. Interests. [Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024 by Ord. No. 6PSF-I,
    - block 41 (1517 chars): § 19:2-12.2                                                                                § 19:2-12
    - block 42 (898 chars): § 19:2-12.3. Minimum Percentage of Decrease. [Ord. 6 PSF-A(S), 9-5-2017; amended
    - block 43 (701 chars): § 19:2-12.5. Conditional Decrease; Correction. [Ord. 6 PSF-A(S), 9-5-2017; amended
    - block 48 (721 chars): Section 19:2-15.
    - block 50 (1814 chars): § 19:2-16. NO EXCESSIVE RENTS. [Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024 by
    - block 51 (1084 chars): § 19:2-17.2. Notification of Tenants. [Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024 by
    - block 53 (777 chars): § 19:2-17.5. Failure to Provide Heat, Water. [Ord. 6 PSF-A(S), 9-5-2017; amended
    - block 62 (1634 chars): § 19:2-18.4                                                                                 § 19:2-1
    - block 63 (1252 chars): § 19:2-18.5. City Auction Manual Required Notice. [Ord. 6 PSF-A(S), 9-5-2017; amended
    - block 65 (846 chars): § 19:2-20. LIBERALLY CONSTRUED. [Ord. 6 PSF-A(S), 9-5-2017; amended 9-18-2024
    - block 70 (2205 chars): § 19:2-25. INSPECTIONS. [Added 5-20-2026 by Ord. No. 6PSF-B, 05-20-2026]
    - block 71 (992 chars): § 19:2-25                                                                                   § 19:2-2
    - block 72 (2336 chars): § 19:2-25.1. Access for Inspections and Repairs; Complaints. [Added 5-20-2026 by Ord. No.
    - block 73 (2733 chars): § 19:2-25.2. Inspection Officers; Identification and Conduct. [Added 5-20-2026 by Ord. No.
    - block 74 (1180 chars): § 19:2-26. PROHIBITIONS ON OCCUPANCY. [Added 5-20-2026 by Ord. No. 6PSF-B,
    - block 75 (905 chars): § 19:2-28. SUPPLY AND POSTING OF CERTIFICATE OF HABITABILITY. [Added
    - block 76 (960 chars): § 19:2-29. MAXIMUM NUMBER OF OCCUPANTS; UNLAWFUL RESIDENTS. [Added
    - block 77 (1102 chars): § 19:2-31. ADHERENCE TO OTHER STANDARDS. [Added 5-20-2026 by Ord. No. 6PSF-
- D071: 185 of 199 blocks left out (331,700 chars)
    - block 0 (741 chars): City of Newark, NJ
    - block 1 (2184 chars): 3.       Property Management.
    - block 2 (1419 chars): § 2:10-1.2. Division of Housing Assistance; Manager; Duties. [Ord. 6 S+FE (S), 9-16-1998
    - block 3 (2995 chars): 4.       City of Newark Predatory Lending Program.
    - block 4 (1003 chars): § 2:10-1.2                                                                                     § 2:1
    - block 5 (2739 chars): 5.       City of Newark Neighborhood Rehabilitation Program.
    - block 8 (4311 chars): Downloaded from https://ecode360.com/NE4043 on 2026-10-03
    - block 9 (4404 chars): Downloaded from https://ecode360.com/NE4043 on 2026-10-03
    - block 10 (1525 chars): Downloaded from https://ecode360.com/NE4043 on 2026-10-03
    - block 11 (2441 chars): 6.       Federal HOME and ADDI Programs.
    - block 12 (846 chars): § 2:10-1.2                                                                                          
    - block 13 (2471 chars): 1.       Administer all programs established by the City to encourage the construction,
    - block 14 (935 chars): § 2:10-1.3                                                                                       § 2
    - block 15 (2394 chars): 1.       Maintain a complete registry of all real property owned by the City, including
    - block 16 (3162 chars): § 2:10-1.4                                                                                          
    - block 17 (837 chars): § 2:10-1.4A. Abandoned Property Rehabilitation Act.2 [Ord. 6 SF-C, 11-22-2010]
    - block 18 (1290 chars): § 2:10-1.4A                                                                                 § 2:10-1
    - block 19 (755 chars): 2.       Exceptions to abandoned property.
    - block 20 (1322 chars): 4.       DEPARTMENT — Shall mean the New Jersey Department of Community Affairs.
    - block 21 (853 chars): § 2:10-1.4A                                                                                       § 
    - block 22 (2624 chars): 7.       OWNER — Shall mean the holder or holders of title to an abandoned property.
    - block 23 (746 chars): 2.       An abandoned property shall not be included on the abandoned property list if
    - block 24 (1741 chars): § 2:10-1.4A                                                                                      § 2
    - block 27 (4688 chars): Downloaded from https://ecode360.com/NE4043 on 2026-10-03
    - block 28 (4236 chars): Downloaded from https://ecode360.com/NE4043 on 2026-10-03
    - block 29 (4096 chars): Downloaded from https://ecode360.com/NE4043 on 2026-10-03
    - block 30 (1063 chars): Downloaded from https://ecode360.com/NE4043 on 2026-10-03
    - block 31 (1635 chars): Section 4 of P.L. 2003, c. 210 (55:19-81) and the owner or party in interest has failed to
    - block 32 (1413 chars): 1.       Documentation that the property is on the municipal abandoned property list or a
    - block 33 (816 chars): Section 4 of P.L. 2002, c.210 (C.55:19-81).
    - block 36 (1100 chars): 2.       Any sums incurred or advanced for the purpose of rehabilitating the property by a
    - block 37 (3858 chars): § 2:10-1.4A                                                                                   § 2:10
    - block 38 (4333 chars): Downloaded from https://ecode360.com/NE4043 on 2026-10-03
    - block 40 (2519 chars): Downloaded from https://ecode360.com/NE4043 on 2026-10-03
    - block 41 (783 chars): Section 19 of P.L.2003, c.210 (C.55:19-96) shall be distributed in the following order of
    - block 42 (4572 chars): 5.       Other valid liens and security interests, in accordance with their priority; and
    - block 43 (1291 chars): Downloaded from https://ecode360.com/NE4043 on 2026-10-03
    - block 44 (3260 chars): Section 3 of P.L. 1942, c. 112 (C.40:48-2.3 or C.40:48-2.5) or Section 1 of P.L. 1989, c. 91
    - block 45 (2290 chars): § 2:10-1.4A                                                                                      § 2
    - block 46 (2040 chars): 2.       The realistic market value of the reused property after rehabilitation or new

