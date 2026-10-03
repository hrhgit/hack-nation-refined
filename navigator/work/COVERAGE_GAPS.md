# Documents without text (not extractable until someone supplies the text)

The corpus lists 87 documents but only 54 have text. The rest cannot produce rules or quoted spans.

To add one by hand (reading a page is allowed; do not bulk-scrape sites whose terms forbid it):

    python run.py add-doc --file page.txt --jurisdiction "Hoboken, NJ" --url <page url>

| doc_id | jurisdiction | source type | capture | url |
|---|---|---|---|---|
| D002 | Berkeley, CA | secondary (law firm / ne | link-only | https://morganlewis.com/pubs/2026/08/algorithmic-rent-pricing-litigation-expands-under-new-state-and-local-laws |
| D015 | CA | secondary (law firm / ne | link-only | https://caanet.org/compliance-reminder-section-8-acceptance-and-criminal-background-checks-are-fair-housing-issues/ |
| D017 | CA | secondary (law firm / ne | link-only | https://california.public.law/codes/civil_code_section_1950.6 |
| D018 | CA | secondary (law firm / ne | link-only | https://law.justia.com/codes/california/code-civ/division-3/part-4/title-5/chapter-2/section-1946-2/ |
| D019 | CA | secondary (law firm / ne | link-only | https://law.justia.com/codes/california/code-civ/division-3/part-4/title-5/chapter-2/section-1947-12/ |
| D020 | CA | secondary (law firm / ne | link-only | https://law.justia.com/codes/california/code-civ/division-3/part-4/title-5/chapter-2/section-1950-5/ |
| D021 | CA | secondary (law firm / ne | link-only | https://law.justia.com/codes/california/code-gov/title-2/division-3/part-2-8/chapter-6/article-2/section-12955/ |
| D028 | CA | secondary (law firm / ne | link-only | https://www.clearygottlieb.com/news-and-insights/publication-listing/californias-antitrust-law-amendments-kick-in-targeting-algorithmic-pricing |
| D030 | Cambridge, MA | secondary (law firm / ne | link-only | https://www.cambridgeday.com/?p=158097 |
| D032 | Hoboken, NJ | code publisher | check-terms | https://ecode360.com/15252438 |
| D033 | Hoboken, NJ | code publisher | check-terms | https://ecode360.com/15252470 |
| D034 | Hoboken, NJ | code publisher | check-terms | https://ecode360.com/46833413 |
| D035 | Jersey City, NJ | secondary (law firm / ne | link-only | https://hudsoncountyview.com/jersey-city-council-approves-realpage-ban-and-increasing-benefits-for-laborers/ |
| D037 | Jersey City, NJ | secondary (law firm / ne | link-only | https://www.morganlewis.com/pubs/2026/08/algorithmic-rent-pricing-litigation-expands-under-new-state-and-local-laws |
| D038 | Los Angeles, CA | code publisher | check-terms | https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-322208 |
| D044 | Los Angeles, CA | secondary (law firm / ne | link-only | https://members.aagla.org/news/city-of-la-security-deposit-interest-requirement |
| D054 | MA | secondary (law firm / ne | link-only | https://masslandlords.net/can-massachusetts-landlords-charge-an-application-fee/ |
| D055 | MA | secondary (law firm / ne | link-only | https://massrealestatelawblog.com/tag/cella-v-attorney-general/ |
| D056 | MA | official | yes | https://www.mass.gov/doc/803-cmr-5-criminal-offender-record-information-cori-housing/download |
| D059 | MA | secondary (law firm / ne | link-only | https://www.wbur.org/news/2026/06/23/massachusetts-high-court-rent-control-ballot-question-struck |
| D060 | NJ | secondary (law firm / ne | link-only | https://daypitney.com/new-jersey-enacts-fair-act-to-prohibit-algorithmic-rent-setting-practices |
| D061 | NJ | secondary (law firm / ne | link-only | https://law.justia.com/codes/new-jersey/title-10/section-10-5-12/ |
| D062 | NJ | secondary (law firm / ne | link-only | https://law.justia.com/codes/new-jersey/title-2a/section-2a-18-61-1/ |
| D063 | NJ | secondary (law firm / ne | link-only | https://law.justia.com/codes/new-jersey/title-46/section-46-8-21-2/ |
| D064 | NJ | secondary (law firm / ne | link-only | https://law.justia.com/codes/new-jersey/title-46/section-46-8-26/ |
| D070 | Newark, NJ | code publisher | check-terms | https://ecode360.com/36623772 |
| D071 | Newark, NJ | code publisher | check-terms | https://ecode360.com/36637822 |
| D072 | Newark, NJ | code publisher | check-terms | https://ecode360.com/36642000 |
| D074 | San Diego, CA | code publisher | check-terms | https://gocodebook.com/library/us/ca/san-diego-zoning/division-11-prohibition-of-anti-competitive-automated-rent-price-fixing/98.1103-use-and-sale-of-algorithmic-devices-prohibited |
| D075 | San Diego, CA | code publisher | check-terms | https://gocodebook.com/library/us/ca/san-diego-zoning/division-8-prohibition-of-discrimination-based-on-a-tenant-s-source-of-income |
| D077 | San Diego, CA | secondary (law firm / ne | link-only | https://www.lassd.org/resource/city-of-san-diego-tenant-protection-ordinance/ |
| D086 | Santa Ana, CA | secondary (law firm / ne | link-only | https://www.ocbj.com/real-estate/santa-ana-bans-landlords-from-using-ai-apartment-rent-pricing-software/ |
| D087 | Santa Ana, CA | secondary (law firm / ne | link-only | https://www.publicceo.com/2026/02/santa-ana-city-council-continues-to-strengthen-tenant-protections-by-banning-anticompetitive-rent-setting-software/ |
