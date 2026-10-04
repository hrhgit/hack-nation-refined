## How rental law is layered

- Rules come from three levels: state statutes, county rules and city ordinances. A city rule may be stricter than the state's. Some states forbid local rules: Massachusetts bars local rent control (G.L. c. 40P, §4), so do not invent rent control for Boston or Cambridge.
- Many rules cover only some buildings. Look for: year built or certificate-of-occupancy cutoffs, number of units, who owns or lives in the property (small landlord, owner-occupied), type of tenancy.
- A web page, guide or FAQ explains a law; the law itself is the statute or ordinance the page names. Record the law and cite the law. A guide such as a state "tenant handbook" mentions many statutes: record only those it explains in some detail, one record per law and category.

## Reading the legal status

- `enacted`: "Chaptered", "Approved", "signed", "adopted", "Ordinance No. …", a codified section stated as current law, "is hereby amended".
- `pending_bill`: a bill or motion that was only introduced, referred to committee or heard; a draft ordinance whose "date of final passage" is blank; "An Act relative to …" with no approval line. A bill is not law until the packet shows it was approved.
- `failed`: withdrawn, died in committee, vetoed, defeated, struck from the ballot.

## Effective dates are often written as a rule. Read them literally.

- "first day of the Nth month next following (the date of) enactment": count N months after the month of approval and take day 1. Invented example: approved March 5, 2024 and "the fourth month next following enactment" gives April (1st), May (2nd), June (3rd), July (4th), so 2024-07-01.
- "takes effect immediately" or "upon passage": the approval date.
- "N days after enactment / final passage": add N days to that date. A blank passage date means `null`.
- An amended section can print several dates ("operative April 1, 2024", "applies to increases on or after March 15, 2019"). Use the date from which the requirement in `key_value` applies and name any other date in `conflict_note`.
- A page that says a rate is "effective March 1, 2026" is giving the start of that rate's period: use it for that value.
- Nothing stated means `null`. Never fill a date from memory.

## Laws you are likely to meet, and how to cite them

Use this list only to NAME and CITE a law that the packet itself describes. It tells you nothing about what a law says: if the packet does not state a rule, the rule does not exist for you. When the packet prints a code citation, use the packet's.

| the law, as pages call it | cite as | category |
|---|---|---|
| California Tenant Protection Act (AB 1482), rent cap | Cal. Civ. Code §1947.12 | rent_increase_limits |
| California Tenant Protection Act, just cause | Cal. Civ. Code §1946.2 | just_cause_eviction |
| California security deposits (AB 12 lowered the cap) | Cal. Civ. Code §1950.5 | security_deposits |
| California tenant screening fee | Cal. Civ. Code §1950.6 | application_screening_fees |
| California fair housing law (FEHA), incl. source of income / Section 8 | Cal. Gov. Code §12955 | screening_restrictions |
| California common pricing algorithms (AB 325, SB 763) | AB 325 (Cal. Bus. & Prof. Code §16729) | algorithmic_rent_setting |
| New Jersey Anti-Eviction Act | N.J.S.A. 2A:18-61.1 | just_cause_eviction |
| New Jersey Security Deposit Act (cap is in §21.2) | N.J.S.A. 46:8-21.2 | security_deposits |
| New Jersey application fee cap | P.L. 2025, c.405 | application_screening_fees |
| New Jersey Fair Chance in Housing Act | P.L. 2021, c.110 | screening_restrictions |
| New Jersey FAIR Act (algorithmic rent setting) | P.L. 2026, c.43 | algorithmic_rent_setting |
| Massachusetts ban on local rent control | G.L. c. 40P, §4 | rent_increase_limits |
| Massachusetts security deposit and upfront charges | G.L. c. 186, §15B | security_deposits and application_screening_fees |
| Massachusetts broker (finder) fee rule | G.L. c. 112, §87DDD½ | application_screening_fees |
| Massachusetts discrimination law, incl. public assistance | G.L. c. 151B, §4 | screening_restrictions |
| Massachusetts algorithmic rent-fixing bills | S.2983, H.5222 | algorithmic_rent_setting |
| San Francisco Rent Ordinance (§37.3 increases, §37.9 just cause, §37.9A and §37.9C relocation, §37.10C algorithmic devices) | S.F. Admin. Code ch. 37 | several |
| Los Angeles Rent Stabilization Ordinance (RSO) | L.A.M.C. §151.00 et seq. | rent_increase_limits, just_cause_eviction |
| Los Angeles Just Cause Ordinance (JCO), relocation | L.A.M.C. §165.00 et seq. | just_cause_eviction |
| Berkeley Rent Ordinance / Measure BB | Berkeley Mun. Code ch. 13.76 | rent_increase_limits, just_cause_eviction |
| Berkeley tenant screening and application fees | Berkeley Mun. Code ch. 13.78 | application_screening_fees |
| Berkeley Fair Chance | Berkeley Mun. Code ch. 13.106 | screening_restrictions |
| Berkeley coordinated pricing algorithms | Berkeley Mun. Code ch. 13.63 | algorithmic_rent_setting |
| San Diego tenant protections (just cause) | San Diego Mun. Code §98.0701 et seq. | just_cause_eviction |
| San Diego automated rent price-fixing ban | San Diego Mun. Code §§98.1101–98.1104 | algorithmic_rent_setting |
| Jersey City Rent Control Ordinance | Jersey City Mun. Code ch. 260 | rent_increase_limits |
| Cambridge Fair Housing Ordinance | Cambridge Mun. Code ch. 14.04 | screening_restrictions |
| Boston Housing Stability Notification Act | Boston Mun. Code §10-11.7 | just_cause_eviction |

Pages that name a program but print no code number (for example the Santa Ana Rent Stabilization Ordinance and Just Cause Eviction Ordinance): cite the program name alone, exactly as the page names it.
