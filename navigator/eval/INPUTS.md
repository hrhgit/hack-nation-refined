# Extraction eval: the inputs

One case = one packet (`work/packets/<id>.md`, or `eval/rehearsal/packets/` for the four invented documents), sent exactly as production sends it. 69 cases: 33 train, 36 test; 27 have hand-made expected laws. The split is random inside each (document kind, has-labels) group, seed 20261003, never chosen by score. The four invented rehearsal documents (R001 to R004) are all in the test split.

## Expected laws (written by hand from the challenge brief, not from any model)

| id | packet | jurisdiction | category | checks | source |
|---|---|---|---|---|---|
| CA-1947.12 | [D024-01](../work/packets/D024-01.md) | CA | rent_increase_limits | status=in_force, numbers=5/10 | challenge brief, 'Rule categories, with real examples from the corpus': CA Tenant Protection Act, Civ. Code 1947.12 (5% + CPI, max 10%) |
| CA-1946.2 | [D023-01](../work/packets/D023-01.md) | CA | just_cause_eviction | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': CA Civ. Code 1946.2 |
| CA-1950.5 | [D025-01](../work/packets/D025-01.md) | CA | security_deposits | status=in_force, date=2024-07-01, numbers=1/2 | challenge brief, 'Rule categories, with real examples from the corpus': CA Civ. Code 1950.5 as amended by AB 12 (one month; two for qualifying small landlords; eff. 7/1/2024) |
| CA-1950.6 | [D026-01](../work/packets/D026-01.md) | CA | application_screening_fees | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': CA Civ. Code 1950.6 (CPI-adjusted cap) |
| CA-FEHA | [D027-01](../work/packets/D027-01.md) | CA | screening_restrictions | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': CA source-of-income protections under FEHA (SB 329) |
| CA-AB325 | [D022-01](../work/packets/D022-01.md) | CA | algorithmic_rent_setting | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': CA AB 325 / SB 763 (1/1/2026). The date itself is not in the text, so it is not checked. |
| NJ-AEA | [D067-03](../work/packets/D067-03.md) | NJ | just_cause_eviction | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': NJ Anti-Eviction Act, N.J.S.A. 2A:18-61.1 |
| NJ-SDA | [D067-01](../work/packets/D067-01.md) | NJ | security_deposits | status=in_force, numbers=1.5 | challenge brief, 'Rule categories, with real examples from the corpus': NJ N.J.S.A. 46:8-21.2 (1.5 months) |
| NJ-405 | [D066-01](../work/packets/D066-01.md) | NJ | application_screening_fees | status=in_force, date=2026-05-01, numbers=50 | challenge brief, 'Rule categories, with real examples from the corpus': NJ P.L.2025, c.405 ($50 cap, eff. 5/1/2026) |
| NJ-FCHA | [D065-01](../work/packets/D065-01.md) | NJ | screening_restrictions | status=in_force, date=2022-01-01 | challenge brief, 'Rule categories, with real examples from the corpus': NJ Fair Chance in Housing Act (2021). Date: the act's own clause, 7th month after approval on 2021-06-18. |
| NJ-FAIR | [D069-01](../work/packets/D069-01.md) | NJ | algorithmic_rent_setting | status=not_yet_effective, date=2027-07-01 | challenge brief, 'Rule categories, with real examples from the corpus': NJ FAIR Act, P.L.2026, c.43 (eff. 7/1/2027), challenge test T3 |
| MA-40P | [D048-01](../work/packets/D048-01.md) | MA | rent_increase_limits | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': MA G.L. c.40P (state bar on local rent control) |
| MA-15B-deposit | [D052-01](../work/packets/D052-01.md) | MA | security_deposits | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': MA G.L. c.186 15B (first month's rent) |
| MA-15B-fees | [D052-01](../work/packets/D052-01.md) | MA | application_screening_fees | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': MA G.L. c.186 15B (upfront charges limited) |
| MA-87DDD | [D057-01](../work/packets/D057-01.md) | MA | application_screening_fees | status=in_force, date=2025-08-01 | challenge brief, 'Rule categories, with real examples from the corpus': MA broker-fee rule, G.L. c.112 87DDD1/2 (8/1/2025) |
| MA-S2983 | [D046-01](../work/packets/D046-01.md) | MA | algorithmic_rent_setting | status=pending | challenge brief, 'Rule categories, with real examples from the corpus': MA S.2983 (pending), challenge test T4 |
| MA-H5222 | [D045-01](../work/packets/D045-01.md) | MA | algorithmic_rent_setting | status=pending | challenge brief, 'Rule categories, with real examples from the corpus': MA H.5222 (pending), challenge test T4 |
| SF-37.10C | [D081-01](../work/packets/D081-01.md) | San Francisco, CA | algorithmic_rent_setting | status=in_force, date=2024-10 | challenge brief, 'Rule categories, with real examples from the corpus': San Francisco 37.10C (Oct 2024) |
| SF-rent | [D083-01](../work/packets/D083-01.md) | San Francisco, CA | rent_increase_limits | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': SF Rent Ordinance, Admin. Code ch. 37 |
| SF-37.9 | [D079-01](../work/packets/D079-01.md) | San Francisco, CA | just_cause_eviction | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': S.F. Admin. Code 37.9 (illustrative output) |
| SD-algo | [D076-01](../work/packets/D076-01.md) | San Diego, CA | algorithmic_rent_setting | found only | challenge brief, 'Rule categories, with real examples from the corpus': San Diego 98.1101-98.1104 (Jun 2025). Status not checked: the packet is a draft. |
| BK-13.63 | [D001-01](../work/packets/D001-01.md) | Berkeley, CA | algorithmic_rent_setting | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': Berkeley ch. 13.63 (2026). The packet prints no effective date, so none is checked. |
| LA-RSO | [D041-01](../work/packets/D041-01.md) | Los Angeles, CA | rent_increase_limits | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': LA Rent Stabilization Ordinance |
| LA-JCO | [D040-01](../work/packets/D040-01.md) | Los Angeles, CA | just_cause_eviction | status=in_force | challenge brief, 'Rule categories, with real examples from the corpus': LA just cause (illustrative) |
| REH-cambridge | [R001-01](rehearsal/packets/R001-01.md) | Cambridge, MA | algorithmic_rent_setting | status=not_yet_effective, date=2026-12-13 | rehearsal R001: passed September 14, 2026, effective 90 days after final passage |
| REH-boston | [R002-01](rehearsal/packets/R002-01.md) | Boston, MA | application_screening_fees | status=pending, numbers=50 | rehearsal R002: a docket still in committee |
| REH-newark | [R003-01](rehearsal/packets/R003-01.md) | Newark, NJ | security_deposits | status=in_force, date=2026-09, numbers=1.5 | rehearsal R003: six sections about one law; effective on passage (Sept 2) and publication (Sept 9) |
| REH-hoboken | [R004-01](rehearsal/packets/R004-01.md) | Hoboken, NJ | screening_restrictions | status=in_force, date=2026-03-01 | rehearsal R004: a web page that prints no code number and lists two rules of one law |

Laws whose text is not in the corpus (Santa Ana, Jersey City, Hoboken, Newark ordinances) cannot appear in any packet and are not listed.

## All cases

| packet | split | kind | document jurisdiction | expected laws | chars | records in the earlier extraction |
|---|---|---|---|---|---|---|
| [D001-01](../work/packets/D001-01.md) | test | ordinance | Berkeley, CA | BK-13.63 | 8160 | 1 |
| [D003-01](../work/packets/D003-01.md) | test | web_page | Berkeley, CA | - | 6325 | 1 |
| [D004-01](../work/packets/D004-01.md) | test | web_page | Berkeley, CA | - | 2806 | 1 |
| [D005-01](../work/packets/D005-01.md) | test | web_page | Berkeley, CA | - | 4099 | 3 |
| [D006-01](../work/packets/D006-01.md) | train | web_page | Berkeley, CA | - | 14260 | 6 |
| [D007-01](../work/packets/D007-01.md) | test | web_page | Berkeley, CA | - | 5159 | 5 |
| [D008-01](../work/packets/D008-01.md) | test | ordinance | Berkeley, CA | - | 2162 | 1 |
| [D009-01](../work/packets/D009-01.md) | test | ordinance | Berkeley, CA | - | 3052 | 3 |
| [D010-01](../work/packets/D010-01.md) | train | web_page | Boston, MA | - | 6684 | 2 |
| [D011-01](../work/packets/D011-01.md) | train | statute | Boston, MA | - | 3730 | 2 |
| [D012-01](../work/packets/D012-01.md) | train | web_page | Boston, MA | - | 3992 | 1 |
| [D013-01](../work/packets/D013-01.md) | train | web_page | Boston, MA | - | 5775 | 2 |
| [D014-01](../work/packets/D014-01.md) | test | ordinance | Boston, MA | - | 6141 | 2 |
| [D016-01](../work/packets/D016-01.md) | test | guide | CA | - | 24043 | 2 |
| [D016-02](../work/packets/D016-02.md) | train | guide | CA | - | 2960 | 0 |
| [D022-01](../work/packets/D022-01.md) | test | statute | CA | CA-AB325 | 6543 | 1 |
| [D023-01](../work/packets/D023-01.md) | test | statute | CA | CA-1946.2 | 23757 | 2 |
| [D023-02](../work/packets/D023-02.md) | train | statute | CA | - | 1706 | 0 |
| [D024-01](../work/packets/D024-01.md) | test | statute | CA | CA-1947.12 | 15725 | 2 |
| [D025-01](../work/packets/D025-01.md) | train | statute | CA | CA-1950.5 | 24226 | 5 |
| [D025-02](../work/packets/D025-02.md) | test | statute | CA | - | 3747 | 2 |
| [D026-01](../work/packets/D026-01.md) | test | statute | CA | CA-1950.6 | 7041 | 5 |
| [D027-01](../work/packets/D027-01.md) | train | statute | CA | CA-FEHA | 10673 | 4 |
| [D029-01](../work/packets/D029-01.md) | train | web_page | Cambridge, MA | - | 12702 | 1 |
| [D031-01](../work/packets/D031-01.md) | train | web_page | Cambridge, MA | - | 6323 | 0 |
| [D036-01](../work/packets/D036-01.md) | train | guide | Jersey City, NJ | - | 5932 | 1 |
| [D039-01](../work/packets/D039-01.md) | test | ordinance | Los Angeles, CA | - | 3341 | 1 |
| [D040-01](../work/packets/D040-01.md) | train | web_page | Los Angeles, CA | LA-JCO | 9937 | 4 |
| [D041-01](../work/packets/D041-01.md) | test | web_page | Los Angeles, CA | LA-RSO | 10634 | 5 |
| [D042-01](../work/packets/D042-01.md) | test | web_page | Los Angeles, CA | - | 5253 | 2 |
| [D043-01](../work/packets/D043-01.md) | train | ordinance | Los Angeles, CA | - | 21827 | 6 |
| [D043-02](../work/packets/D043-02.md) | train | ordinance | Los Angeles, CA | - | 13485 | 5 |
| [D045-01](../work/packets/D045-01.md) | train | statute | MA | MA-H5222 | 2744 | 1 |
| [D046-01](../work/packets/D046-01.md) | test | statute | MA | MA-S2983 | 3193 | 1 |
| [D047-01](../work/packets/D047-01.md) | test | statute | MA | - | 3205 | 1 |
| [D048-01](../work/packets/D048-01.md) | train | statute | MA | MA-40P | 2790 | 1 |
| [D049-01](../work/packets/D049-01.md) | test | statute | MA | - | 23274 | 1 |
| [D049-02](../work/packets/D049-02.md) | train | statute | MA | - | 23876 | 2 |
| [D049-03](../work/packets/D049-03.md) | train | statute | MA | - | 10217 | 0 |
| [D050-01](../work/packets/D050-01.md) | test | statute | MA | - | 2433 | 1 |
| [D051-01](../work/packets/D051-01.md) | train | statute | MA | - | 4096 | 2 |
| [D052-01](../work/packets/D052-01.md) | test | statute | MA | MA-15B-deposit, MA-15B-fees | 23643 | 6 |
| [D052-02](../work/packets/D052-02.md) | train | statute | MA | - | 3204 | 1 |
| [D053-01](../work/packets/D053-01.md) | test | statute | MA | - | 4297 | 2 |
| [D057-01](../work/packets/D057-01.md) | train | statute | MA | MA-87DDD | 2805 | 1 |
| [D058-01](../work/packets/D058-01.md) | test | statute | MA | - | 2979 | 1 |
| [D065-01](../work/packets/D065-01.md) | train | statute | NJ | NJ-FCHA | 21245 | 4 |
| [D066-01](../work/packets/D066-01.md) | train | statute | NJ | NJ-405 | 4447 | 1 |
| [D067-01](../work/packets/D067-01.md) | train | guide | NJ | NJ-SDA | 23057 | 4 |
| [D067-02](../work/packets/D067-02.md) | train | guide | NJ | - | 20388 | 10 |
| [D067-03](../work/packets/D067-03.md) | test | guide | NJ | NJ-AEA | 21057 | 3 |
| [D067-04](../work/packets/D067-04.md) | test | guide | NJ | - | 18253 | 5 |
| [D068-01](../work/packets/D068-01.md) | test | guide | NJ | - | 7105 | 1 |
| [D069-01](../work/packets/D069-01.md) | test | statute | NJ | NJ-FAIR | 10701 | 2 |
| [D073-01](../work/packets/D073-01.md) | train | ordinance | San Diego, CA | - | 24141 | 2 |
| [D073-02](../work/packets/D073-02.md) | train | ordinance | San Diego, CA | - | 14753 | 2 |
| [D076-01](../work/packets/D076-01.md) | train | ordinance | San Diego, CA | SD-algo | 23449 | 1 |
| [D078-01](../work/packets/D078-01.md) | test | web_page | San Francisco, CA | - | 7044 | 1 |
| [D079-01](../work/packets/D079-01.md) | train | web_page | San Francisco, CA | SF-37.9 | 5680 | 2 |
| [D080-01](../work/packets/D080-01.md) | test | web_page | San Francisco, CA | - | 1397 | 1 |
| [D081-01](../work/packets/D081-01.md) | train | web_page | San Francisco, CA | SF-37.10C | 1487 | 1 |
| [D082-01](../work/packets/D082-01.md) | test | web_page | San Francisco, CA | - | 3872 | 2 |
| [D083-01](../work/packets/D083-01.md) | test | web_page | San Francisco, CA | SF-rent | 5028 | 5 |
| [D084-01](../work/packets/D084-01.md) | train | web_page | Santa Ana, CA | - | 4460 | 3 |
| [D085-01](../work/packets/D085-01.md) | train | web_page | Santa Ana, CA | - | 5652 | 3 |
| [R001-01](rehearsal/packets/R001-01.md) | test | rehearsal | Cambridge, MA | REH-cambridge | 2279 | 1 |
| [R002-01](rehearsal/packets/R002-01.md) | test | rehearsal | Boston, MA | REH-boston | 1633 | 1 |
| [R003-01](rehearsal/packets/R003-01.md) | test | rehearsal | Newark, NJ | REH-newark | 1742 | 1 |
| [R004-01](rehearsal/packets/R004-01.md) | test | rehearsal | Hoboken, NJ | REH-hoboken | 1567 | 1 |

## Things to know before trusting a number from this eval

- It stands in for the organisers' scoring script, which is not in the data pack. The final answer must be checked on the real one.
- Only 28 laws have hand-made expectations. For every other packet the score rests on the code-checked parts (clean first pass, one record per law, clean and numbered citations, dates) and on agreement with the earlier extraction about whether a packet holds any rule.
- The earlier extraction (Claude sub-agents) is used for two coarse checks only: does the packet yield any record, and which (jurisdiction, category) cells. It is a frozen copy (`silver.json`), not an answer key.
- A label may only expect a date the packet text supports (tests enforce it). Berkeley and AB 325 therefore carry no date check.
- D046-01 and D047-01 hold the same bill text, so that bill counts twice.
- Claude's earlier answers already find all expected laws, so `recall` cannot show gains for a model as strong; it matters for DeepSeek.
- The primer planned as a later round names some laws that are also expected here. A gain on those laws then measures "knows the citation", not general skill; the unlabeled packets keep the general part honest.
