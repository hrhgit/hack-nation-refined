"""Write the four invented 'new ordinance' rehearsal cases (stand-ins for the document released at hour 16).

The documents are invented, in realistic legal style, with different structures and different traps. They live in
eval/rehearsal/ only: they never enter the real corpus, work/packets or the production rules. The gold answers are
written by hand next to them.
"""
from __future__ import annotations

import csv
import json
import sys

from common import HERE, ROOT
from nav.corpus import _read_manifest
from nav.packets import build_doc_packets, render_packet

REH = HERE / "rehearsal"
HDR = "SOURCE: https://example.org/rehearsal/%s\nRETRIEVED: 2026-10-03 09:00 UTC\n\n"

DOCS = {
 "R001": ("Cambridge, MA", "cambridge-ordinance-2026-31", """CITY OF CAMBRIDGE
ORDINANCE NO. 2026-31
AN ORDINANCE PROHIBITING THE USE OF ALGORITHMIC RENT-SETTING SOFTWARE IN RESIDENTIAL RENTAL HOUSING

Be it ordained by the City Council of the City of Cambridge as follows:

Section 1. Findings and purpose.
The City Council finds that software that analyzes nonpublic rental data from competing landlords to recommend rents can raise rents above competitive levels. The purpose of this ordinance is to prohibit that practice for residential rental units in the City of Cambridge.

Section 2. Definitions.
(a) "Algorithmic rent-setting device" means software that uses an algorithm to analyze nonpublic competitor rental data in order to recommend rents or occupancy levels for residential dwelling units.
(b) "Nonpublic competitor rental data" means rental rates, occupancy levels or lease terms of units owned by a person other than the user that are not publicly available.
(c) "Landlord" means an owner, lessor or manager of a residential dwelling unit.

Section 3. Prohibition.
It shall be unlawful for a landlord to use an algorithmic rent-setting device to set the rent or occupancy level of any residential dwelling unit in the City of Cambridge. It shall also be unlawful to sell or license such a device to a landlord for use in the City of Cambridge.

Section 4. Exemptions.
This ordinance does not apply to a unit owned by a public housing authority or to a dwelling unit in an owner-occupied building of four or fewer units.

Section 5. Penalties and enforcement.
A violation is subject to a civil penalty of up to $1,000 per violation. Each unit for which a device is used, and each month of use, is a separate violation. The City Solicitor may bring a civil action to enforce this ordinance.

Section 6. Effective date.
This ordinance shall take effect ninety (90) days after its final passage.

Passed to be ordained September 14, 2026.
Attest: City Clerk
"""),
 "R002": ("Boston, MA", "boston-docket-0842", """Boston City Council
Docket #0842
Order for an ordinance regulating application and screening fees charged to prospective tenants

Filed by: Councilor R. Almeida
Date filed: September 9, 2026
Current status: Referred to the Committee on Housing and Community Development on September 9, 2026. No hearing has been held. This docket has not been passed by the City Council and is not in effect.

Text of the proposed ordinance

Section 1. Definitions.
"Application fee" means any fee charged to a prospective tenant to apply for a rental unit, including fees for a credit check, a background check or administrative processing.

Section 2. Limit on fees.
No landlord shall charge a prospective tenant an application or screening fee exceeding fifty dollars ($50) per application. A landlord may charge only one such fee per applicant for a unit.

Section 3. Receipt and refund.
A landlord who charges a fee shall give the applicant a written receipt. If the landlord does not run the checks for which the fee was charged, the fee shall be refunded within seven days.

Section 4. Penalty.
A landlord who violates this ordinance is subject to a fine of $300 for each violation.

Section 5. Effective date.
This ordinance shall take effect upon passage.
"""),
 "R003": ("Newark, NJ", "newark-ordinance-6psf-a", """CITY OF NEWARK
MUNICIPAL COUNCIL
ORDINANCE 6PSF-A
AN ORDINANCE REGULATING SECURITY DEPOSITS IN RESIDENTIAL RENTAL HOUSING

BE IT ORDAINED by the Municipal Council of the City of Newark:

SECTION 1. LIMIT ON SECURITY DEPOSITS.
(a) A landlord shall not demand or accept a security deposit of more than one and one-half (1.5) times the monthly rent for a residential rental unit.
(b) A landlord who increases the rent may require an additional deposit only so that the total deposit does not exceed one and one-half times the new monthly rent.

SECTION 2. HANDLING OF DEPOSITS.
The landlord shall hold the deposit in an interest-bearing account at a New Jersey bank and shall pay the tenant the interest earned each year.

SECTION 3. RETURN OF DEPOSITS.
Within thirty (30) days after the tenancy ends, the landlord shall return the deposit with interest, together with an itemized statement of any deductions.

SECTION 4. EXEMPTIONS.
This ordinance does not apply to owner-occupied buildings with two or fewer rental units.

SECTION 5. PENALTIES.
A landlord who fails to return a deposit as required by Section 3 shall pay the tenant twice the amount wrongfully withheld, plus court costs.

SECTION 6. EFFECTIVE DATE.
This ordinance shall take effect upon passage and publication.

Passed by the Municipal Council on September 2, 2026.
Published in the Newark Star-Ledger on September 9, 2026.
"""),
 "R004": ("Hoboken, NJ", "hoboken-fair-chance-faq", """City of Hoboken | Rent Leveling and Stabilization Board
Home About Contact Forms News
Tenant Fair Chance Ordinance: frequently asked questions

What is the Tenant Fair Chance Ordinance?
Hoboken's Tenant Fair Chance Ordinance limits how landlords may screen people who apply to rent an apartment. It took effect on March 1, 2026 and applies to all residential rental units in Hoboken except owner-occupied buildings with four or fewer units.

What may a landlord not do?
A landlord may not ask about an applicant's criminal history before making a conditional offer.
After a conditional offer, a landlord may consider only convictions from the past five years and must give the applicant a chance to explain.
A landlord may not refuse to rent to an applicant because the applicant pays with a housing voucher or other lawful source of income.

What happens if a landlord breaks the rules?
The Board may fine a landlord up to $2,000 for each violation. Tenants may also file a complaint with the Board within one year.

Where can I get more information?
Call the Board at (201) 555-0100 or visit City Hall, 94 Washington Street.
Privacy Policy Terms of Use Accessibility
"""),
}

APP = {"built_on_or_before": None, "built_after": None, "date_basis": None, "min_units": None, "max_units": None,
       "owner_dependent": False, "other": None}


def gold(pid, jur, cat, life, title, req, cite, quote, kv=None, eff=None, exemptions=None, penalty=None, owner=False):
    app = dict(APP, owner_dependent=owner)
    return {"packet_id": pid, "doc_id": pid.split("-")[0], "jurisdiction": jur, "category": cat, "lifecycle": life,
            "title": title, "requirement": req, "key_value": kv, "coverage_conditions": "Residential rental units in the city",
            "applicability": app, "exemptions": exemptions, "penalty": penalty, "effective_date": eff, "citation": cite,
            "quoted_span": quote, "interaction": None, "confidence": 0.95, "conflict_flag": False, "conflict_note": None}


GOLD = [
    gold("R001-01", "Cambridge, MA", "algorithmic_rent_setting", "enacted", "Ban on algorithmic rent-setting software",
         "Landlords may not use, sell or license software that analyzes nonpublic competitor rent data to set rents or occupancy levels.",
         "Cambridge Ordinance No. 2026-31",
         "It shall be unlawful for a landlord to use an algorithmic rent-setting device to set the rent or occupancy level of any residential dwelling unit in the City of Cambridge.",
         eff="2026-12-13", exemptions="Public housing authority units; owner-occupied buildings of four or fewer units",
         penalty="Civil penalty up to $1,000 per violation; each unit and each month is a separate violation", owner=True),
    gold("R002-01", "Boston, MA", "application_screening_fees", "pending_bill", "Cap on tenant application and screening fees",
         "A proposed ordinance would cap application and screening fees at $50 and require receipts and refunds. It has not been passed.",
         "Boston City Council Docket #0842",
         "No landlord shall charge a prospective tenant an application or screening fee exceeding fifty dollars ($50) per application.",
         kv="$50 per application", penalty="Fine of $300 per violation"),
    gold("R003-01", "Newark, NJ", "security_deposits", "enacted", "Cap on security deposits",
         "A landlord may not take a security deposit above 1.5 times the monthly rent, must keep it in an interest-bearing account and return it with interest within 30 days.",
         "Newark Ordinance 6PSF-A",
         "A landlord shall not demand or accept a security deposit of more than one and one-half (1.5) times the monthly rent for a residential rental unit.",
         kv="1.5 times monthly rent", eff="2026-09-09", exemptions="Owner-occupied buildings with two or fewer rental units",
         penalty="Twice the amount wrongfully withheld, plus court costs", owner=True),
    gold("R004-01", "Hoboken, NJ", "screening_restrictions", "enacted", "Tenant Fair Chance Ordinance",
         "Landlords may not ask about criminal history before a conditional offer and may not refuse an applicant for using a voucher or other lawful source of income.",
         "Hoboken Tenant Fair Chance Ordinance",
         "A landlord may not ask about an applicant's criminal history before making a conditional offer.",
         eff="2026-03-01", exemptions="Owner-occupied buildings with four or fewer units", penalty="Fine up to $2,000 per violation", owner=True),
]


def main() -> int:
    (REH / "text").mkdir(parents=True, exist_ok=True)
    (REH / "packets").mkdir(parents=True, exist_ok=True)
    rows = []
    for did, (jur, slug, body) in DOCS.items():
        (REH / "text" / (did + ".txt")).write_text(HDR % slug + body, encoding="utf-8")
        rows.append({"doc_id": did, "jurisdictions": jur, "url": "https://example.org/rehearsal/" + slug,
                     "source_type": "official", "capture": "yes", "retrieved_at": "2026-10-03 09:00 UTC", "sha256": "",
                     "text_file": "text/%s.txt" % did, "status": "ok"})
    with (REH / "manifest.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    docs = {}
    _read_manifest(REH / "manifest.csv", REH, "rehearsal", docs)
    for did, doc in docs.items():
        packets, _ = build_doc_packets(doc)
        for p in packets:
            (REH / "packets" / (p.packet_id + ".md")).write_text(render_packet(p, doc, "2026-10-01"), encoding="utf-8")
    bad = [g["packet_id"] for g in GOLD if " ".join(g["quoted_span"].split()) not in " ".join(docs[g["doc_id"]].body.split())]
    if bad:
        raise SystemExit("gold quotes not found in their documents: %s" % bad)
    lines = []
    for g in GOLD:
        lines.append(json.dumps(g, ensure_ascii=False))
        lines.append(json.dumps({"packet_id": g["packet_id"], "n_rules": 1, "note": None}))
    (REH / "oracle.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("rehearsal: %d documents, %d packets, %d gold records" % (len(docs), len(list((REH / "packets").glob("*.md"))), len(GOLD)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
