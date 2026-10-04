// Fixed category hints, preserved from the Python baseline.
export const CATEGORY_PATTERNS: Record<string, [RegExp, number][]> = {
  "rent_increase_limits": [
    [new RegExp("rent[- ]control|rent stabili[sz]ation|rent ordinance|rent board|rent adjustment", "ig"), 2],
    [new RegExp("(?:annual|maximum|allowable|general)\\s+(?:rent\\s+)?(?:adjustment|increase)", "ig"), 2],
    [new RegExp("(?:rent|rental rate)s?\\s+increase|increase\\s+(?:in\\s+)?(?:the\\s+)?(?:gross\\s+)?(?:rent|rental)", "ig"), 2],
    [new RegExp("consumer price index|\\bCPI\\b|cost of living", "ig"), 1],
    [new RegExp("rent (?:cap|ceiling)|maximum (?:lawful |allowable )?rent|banking", "ig"), 1],
    [new RegExp("preempt|local(?:ly)? (?:rent|regulat)", "ig"), 1],
  ],
  "just_cause_eviction": [
    [new RegExp("just cause|good cause|anti-eviction|cause for (?:eviction|termination)|grounds for (?:eviction|termination)", "ig"), 2],
    [new RegExp("\\bevict", "ig"), 1],
    [new RegExp("relocation (?:assistance|payment|benefit|fee)", "ig"), 2],
    [new RegExp("notice (?:of|to) (?:terminat|quit|vacate)|terminat\\w+ (?:of )?(?:a )?tenanc", "ig"), 1],
    [new RegExp("owner move-in|substantial rehabilitation|ellis act|withdraw\\w* .{0,40}rental market", "ig"), 1],
  ],
  "security_deposits": [
    [new RegExp("security deposit", "ig"), 2],
    [new RegExp("deposit.{0,60}month|month.{0,40}deposit", "ig"), 1],
    [new RegExp("(?:first|last) month'?s rent", "ig"), 1],
    [new RegExp("interest on (?:the |a )?(?:security )?deposit|deposit.{0,40}(?:escrow|interest)", "ig"), 1],
    [new RegExp("return(?:ed)? (?:of )?(?:the |a )?(?:security )?deposit", "ig"), 1],
  ],
  "application_screening_fees": [
    [new RegExp("application fee|screening fee|screening charge|application charge|tenant screening", "ig"), 2],
    [new RegExp("credit check.{0,30}fee|fee.{0,30}credit check", "ig"), 2],
    [new RegExp("broker'?s? fee|finder'?s fee|\\bbroker\\b", "ig"), 2],
    [new RegExp("holding deposit|lock fee|key fee|up-?front|advance payment|first and last month", "ig"), 1],
  ],
  "screening_restrictions": [
    [new RegExp("criminal (?:history|record|background|offender)|conviction|\\barrest|\\bCORI\\b|fair chance|ban the box", "ig"), 2],
    [new RegExp("source of income|lawful source|section 8|housing choice voucher|rental assistance|public assistance|voucher", "ig"), 2],
    [new RegExp("credit (?:history|score|report)|background check|income requirement|eviction (?:history|record)", "ig"), 1],
    [new RegExp("protected (?:class|characteristic)|discriminat", "ig"), 1],
  ],
  "algorithmic_rent_setting": [
    [new RegExp("algorithm", "ig"), 3],
    [new RegExp("pricing (?:software|device)|revenue management|non-?public (?:competitor )?(?:rental )?data|coordinated pricing|price[- ]fixing", "ig"), 2],
    [new RegExp("realpage|yieldstar|common pricing|occupancy levels", "ig"), 2],
    [new RegExp("antitrust|cartwright|sherman act", "ig"), 1],
  ],
};
export function scoreText(text: string): Record<string, number> {
  const out: Record<string, number> = {};
  for (const [cat, patterns] of Object.entries(CATEGORY_PATTERNS)) out[cat] = patterns.reduce((sum, [rx, w]) => sum + w * Math.min(Array.from(text.matchAll(rx)).length, 5), 0);
  return out;
}
export const isRelevant = (scores: Record<string, number>): boolean => Math.max(0, ...Object.values(scores)) >= 2 || Object.values(scores).reduce((a,b) => a+b,0) >= 3;
export function mergeScores(parts: Record<string, number>[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const part of parts) for (const [k,v] of Object.entries(part)) out[k] = (out[k] ?? 0) + v;
  return out;
}
