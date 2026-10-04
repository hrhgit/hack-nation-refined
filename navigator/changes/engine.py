"""Compare actual lookup results, without hard-coded expected address sets."""
from __future__ import annotations

import copy
from collections import Counter
from pathlib import Path

from lookup.common import DISCLAIMER, PACK, matches, query_date, read_json


class ChangeTracker:
    def __init__(self, lookup_engine, tests=None, rule_map=None):
        self.engine = lookup_engine
        self.tests = copy.deepcopy(tests if tests is not None else read_json(PACK / "dev" / "change_tests.json"))
        self.rule_map = copy.deepcopy(rule_map if rule_map is not None else read_json(Path(__file__).with_name("test_rule_map.json")))
        self.cache = {}
        self.audit_cache = {}

    def mapped(self, external_id):
        if external_id not in self.rule_map:
            raise ValueError("变更题缺少法规对照配置: " + external_id)
        return sorted(r["team_rule_id"] for r in self.engine.rules if matches(r, self.rule_map[external_id]))

    def _lookups(self, day):
        query_date(day)
        if day not in self.cache:
            output, audit = self.engine.all(day)
            self.cache[day] = output["lookups"]
            self.audit_cache[day] = audit["addresses"]
        return self.cache[day]

    @staticmethod
    def _signature(rows, relevant):
        return {row["team_rule_id"]: (row["result"], row["conflict_flag"]) for row in rows if row["team_rule_id"] in relevant}

    def run(self, date_overrides=None):
        """Optional per-test dates replace the supplied dates and are audited."""
        overrides = date_overrides or {}
        if set(overrides) - {case["test_id"] for case in self.tests}:
            raise ValueError("日期配置含未知题号")
        output, audit = {}, {"disclaimer": DISCLAIMER, "tests": {}}
        for supplied in self.tests:
            case = copy.deepcopy(supplied)
            test_id = case["test_id"]
            replacement = overrides.get(test_id, {})
            allowed_dates = {"as_of_before", "as_of_after"} if case["type"] == "as_of" else {"as_of"}
            if set(replacement) - allowed_dates:
                raise ValueError("只能覆盖该题实际使用的查询日期：%s" % ", ".join(sorted(allowed_dates)))
            case.update(replacement)
            mapping = {rid: self.mapped(rid) for rid in case["rule_ids"] + case.get("conflict_with", [])}
            missing = [rid for rid, ids in mapping.items() if not ids]
            relevant = {rid for external in case["rule_ids"] for rid in mapping[external]}
            conflict_rules = {rid for external in case.get("conflict_with", []) for rid in mapping[external]}
            affected, conflicts, evidence = [], [], {}
            notes = []
            if case["type"] == "as_of":
                before, after = case["as_of_before"], case["as_of_after"]
                old, new = self._lookups(before), self._lookups(after)
                notes.append("Compared the lookup results on %s and %s" % (before, after))
                for aid in sorted(self.engine.addresses):
                    previous = self._signature(old[aid], relevant)
                    current = self._signature(new[aid], relevant)
                    if previous != current:
                        affected.append(aid)
                        evidence[aid] = {"before": previous, "after": current}
                    if relevant and conflict_rules:
                        pairs = self.audit_cache[before][aid]["conflict_pairs"] + self.audit_cache[after][aid]["conflict_pairs"]
                        if any(state_id in relevant and city_id in conflict_rules for state_id, city_id in pairs):
                            conflicts.append(aid)
            else:
                day = case["as_of"]
                lookups = self._lookups(day)
                notes.append("Query date %s" % day)
                if case["type"] in {"boundary", "pending"}:
                    target_results = {"applies", "unknown"} if case["type"] == "boundary" else {"pending"}
                    for aid, rows in sorted(lookups.items()):
                        chosen = [row for row in rows if row["team_rule_id"] in relevant and row["result"] in target_results]
                        if chosen:
                            affected.append(aid)
                            evidence[aid] = chosen
                    if case["type"] == "boundary":
                        counts = Counter(self.engine.addresses[aid].get("legal_city") or "city not resolved" for aid in affected)
                        notes.append("Affected addresses by city: " + (", ".join("%s %s" % (city, count) for city, count in sorted(counts.items())) or "none, because no city ban is in the rule set"))
                    else:
                        notes.append("The list shows the addresses the bills would cover if enacted; they are reported as pending, not as law")
                elif case["type"] == "negative":
                    targets = case.get("states", [])
                    violations = []
                    for aid, rows in sorted(lookups.items()):
                        if targets and self.engine.addresses[aid]["state"] not in targets:
                            continue
                        for row in rows:
                            rule = self.engine.by_id[row["team_rule_id"]]
                            # a state rule that bars cities from regulating rent (Massachusetts c. 40P) is the opposite of a cap
                            bars_local = any(r.get("type") == "preempts_local" for r in rule.get("relations") or [])
                            if row["result"] == "applies" and rule["category"] == "rent_increase_limits" and not bars_local:
                                violations.append((aid, row["team_rule_id"]))
                    if violations:
                        raise ValueError("反例检查失败：麻州地址出现适用的涨租上限: %s" % violations)
                    if any(self.engine.by_id[rid].get("lifecycle") not in {"failed", "withdrawn"} for rid in relevant):
                        raise ValueError("反例检查失败：公投规则未记为 failed")
                    notes.append("The affected list is empty; every target address was checked and none has an applicable rent cap")
                    if relevant:
                        notes.append("The ballot measure is recorded as failed")
                else:
                    raise ValueError("不支持的变更题类型: " + case["type"])
            if missing:
                notes.append("Rules missing from the extracted set: %s; this answer covers only what the extracted rules support and is incomplete" % ", ".join(missing))
            notes.append(DISCLAIMER)
            output[test_id] = {"affected_address_ids": sorted(affected), "conflict_flag_address_ids": sorted(conflicts), "notes": ". ".join(notes)}
            audit["tests"][test_id] = {"query_dates": {k: case[k] for k in ("as_of", "as_of_before", "as_of_after") if k in case},
                                      "rule_mapping": mapping, "missing_rules": missing, "evidence": evidence}
        return output, audit
