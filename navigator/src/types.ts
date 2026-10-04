// The stored records are extensible JSON. Known production fields have explicit
// types; additional fields remain available to the schema validator and exports.
export type Data = Record<string, any>;
export type Lifecycle = 'enacted' | 'pending_bill' | 'failed' | 'withdrawn';
export type Status = 'in_force' | 'not_yet_effective' | 'pending' | 'failed' | 'unknown';
export type Result = 'applies' | 'unknown' | 'superseded' | 'not_yet_effective' | 'pending';
export interface Rule extends Data {
  team_rule_id: string;
  jurisdiction: string;
  level: 'state' | 'city';
  category: string;
  citation: string;
  lifecycle?: Lifecycle | null;
  effective_date?: string | null;
  applicability?: Data | null;
}
export interface Address extends Data {
  state: string;
  legal_city?: string | null;
  year_built?: number | null;
  units?: number | null;
  units_at_least?: number | null;
}
export interface LookupRow {
  team_rule_id: string;
  result: Result;
  explanation: string;
  conflict_flag: boolean;
}
export interface DecisionStep {
  step: number;
  outcome: string;
  facts: unknown;
  explanation: string;
}
export interface Trace extends Data {
  team_rule_id: string;
  steps: DecisionStep[];
  missing_facts: {field: string; explanation: string}[];
}
export type Query = Record<string, string[]>;
