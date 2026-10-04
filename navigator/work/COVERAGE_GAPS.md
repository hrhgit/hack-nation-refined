# Documents without text (not extractable until someone supplies the text)

The corpus lists 97 documents but only 82 have text. The rest cannot produce rules or quoted spans.

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
| D054 | MA | secondary (law firm / ne | link-only | https://masslandlords.net/can-massachusetts-landlords-charge-an-application-fee/ |
| D055 | MA | secondary (law firm / ne | link-only | https://massrealestatelawblog.com/tag/cella-v-attorney-general/ |
| D059 | MA | secondary (law firm / ne | link-only | https://www.wbur.org/news/2026/06/23/massachusetts-high-court-rent-control-ballot-question-struck |
| D060 | NJ | secondary (law firm / ne | link-only | https://daypitney.com/new-jersey-enacts-fair-act-to-prohibit-algorithmic-rent-setting-practices |
| D077 | San Diego, CA | secondary (law firm / ne | link-only | https://www.lassd.org/resource/city-of-san-diego-tenant-protection-ordinance/ |
| D087 | Santa Ana, CA | secondary (law firm / ne | link-only | https://www.publicceo.com/2026/02/santa-ana-city-council-continues-to-strengthen-tenant-protections-by-banning-anticompetitive-rent-setting-software/ |
