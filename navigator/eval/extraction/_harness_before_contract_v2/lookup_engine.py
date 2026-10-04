"""Evaluate geography, lifecycle, coverage, precedence and conflicts on a date.

The engine consumes facts and explicit selectors. It does not infer legal facts
from prose, historical status snapshots, extractor IDs, or extractor flags.
"""
from __future__ import annotations

import copy
import calendar
import datetime as dt
import re
from collections import defaultdict
from pathlib import Path

from .common import CATEGORIES, DEFAULT_DATE, DISCLAIMER, ROOT, date_interval, matches, query_date, read_json

REVIEW_NOTE = "a state law and a city ordinance regulate the same subject and the sources do not settle which one governs here; flagged for human review"


def sentence(text):
    text = text.strip()
    return text[0].upper() + text[1:] + ("" if text.endswith(".") else ".")


RESULTS = {"applies", "unknown", "superseded", "not_yet_effective", "pending"}
FIELDS = ["team_rule_id", "jurisdiction", "level", "category", "status", "title", "requirement",
          "key_value", "coverage_conditions", "exemptions", "overrides", "interaction", "effective_date",
          "citation", "source_doc_id", "source_url", "quoted_span", "confidence", "conflict_flag", "conflict_note"]


def load_rules(path=ROOT / "work" / "rules_enriched.json", supplements=None):
    payload = read_json(path)
    rules = copy.deepcopy(payload["rules"] if isinstance(payload, dict) else payload)
    supplements = supplements if supplements is not None else read_json(Path(__file__).with_name("coverage_facts.json"))
    for supplement in supplements:
        if not supplement.get("basis") or not supplement.get("source"):
            raise ValueError("覆盖条件补充必须有依据和来源")
        for rule in rules:
            if matches(rule, supplement["match"]):
                if not rule.get("applicability"):
                    rule["applicability"] = {}
                rule["applicability"].update(supplement.get("applicability", {}))
                rule.update(supplement.get("set", {}))
                rule.setdefault("coverage_sources", []).append({k: supplement[k] for k in ("id", "basis", "source")})
    return rules


# Words that mark a text condition as a property of the building, unit or owner (not in the address data).
# Anything else describes when the duty is triggered (an event, a tenancy, a fee) and does not change coverage.
BUILDING_WORDS = re.compile(
    r"exclud|exempt|does not apply|not apply to|only (?:to|if|a)|owner[- ]occup|subsid|affordable|income[- ]restricted|funded|"
    r"certificate of occupancy|covered by|under the rent ordinance|convert|condominium|mobile ?home|"
    r"(?:one|two|three|single)[- ]family|produced in|built|constructed", re.I)


def other_kind(text):
    return "building" if BUILDING_WORDS.search(text) else "trigger"


def state_of(rule):
    return rule["jurisdiction"] if rule["level"] == "state" else rule["jurisdiction"].rsplit(", ", 1)[-1]


def status_on(rule, as_of):
    lifecycle = rule.get("lifecycle")
    if lifecycle in {"failed", "withdrawn"}:
        return "failed"
    if lifecycle == "pending_bill":
        return "pending"
    if lifecycle != "enacted":
        return "unknown"
    effective = rule.get("effective_date")
    if not effective:
        return "in_force"
    first, last = date_interval(effective)
    day = query_date(as_of)
    if day < first:
        return "not_yet_effective"
    if day < last:
        return "unknown"
    return "in_force"


class LookupEngine:
    def __init__(self, rules, addresses, precedence=None, review=None):
        for item in rules:
            for field in ("team_rule_id", "jurisdiction", "citation"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    raise ValueError("规则缺少有效的%s" % field)
        self.rules = sorted(copy.deepcopy(rules), key=lambda r: r["team_rule_id"])
        self.addresses = copy.deepcopy(addresses)
        for aid, address in self.addresses.items():
            if not isinstance(address.get("state"), str) or not address["state"]:
                raise ValueError("%s缺少州" % aid)
            for field in ("year_built", "units", "units_at_least"):
                value = address.get(field)
                if value is not None and (type(value) is not int or value < 0):
                    raise ValueError("%s.%s 必须是非负整数或 null" % (aid, field))
        self.precedence = copy.deepcopy(precedence if precedence is not None else read_json(Path(__file__).with_name("precedence.json")))
        ids = [r["team_rule_id"] for r in self.rules]
        if len(set(ids)) != len(ids):
            raise ValueError("规则编号重复")
        self.by_id = {r["team_rule_id"]: r for r in self.rules}
        for rule in self.rules:
            if rule.get("category") not in CATEGORIES or rule.get("level") not in {"state", "city"}:
                raise ValueError("规则类别或地区级别错误: " + rule["team_rule_id"])
            if rule.get("lifecycle") not in {None, "enacted", "pending_bill", "failed", "withdrawn"}:
                raise ValueError("未知的规则通过状态: " + rule["team_rule_id"])
            if rule.get("effective_date"):
                date_interval(rule["effective_date"])
            if rule.get("valid_through"):
                date_interval(rule["valid_through"])
            if (rule["level"] == "city") != (", " in rule["jurisdiction"]):
                raise ValueError("规则地区与级别不一致: " + rule["team_rule_id"])
            applicability = rule.get("applicability") or {}
            for field in ("min_units", "max_units", "exempt_if_newer_than_years", "owner_exempt_if_units_at_most"):
                value = applicability.get(field)
                if value is not None and (type(value) is not int or value < 0):
                    raise ValueError("%s.%s 必须是非负整数" % (rule["team_rule_id"], field))
            for field in ("built_on_or_before", "built_after"):
                if applicability.get(field):
                    date_interval(applicability[field])
        self.edges = self._precedence_edges()
        self.review = copy.deepcopy(review if review is not None else read_json(Path(__file__).with_name("review_pairs.json")))
        self.review_pairs = self._review_pairs()

    @classmethod
    def from_files(cls, rules_path=ROOT / "work" / "rules_enriched.json",
                   addresses_path=ROOT / "work" / "addresses_resolved.json"):
        return cls(load_rules(rules_path), read_json(addresses_path))

    def _precedence_edges(self):
        edges = {}
        for entry in self.precedence:
            if not entry.get("basis") or not entry.get("source"):
                raise ValueError("取代关系必须有原文依据和来源")
            for yielding in self.rules:
                if yielding.get("lifecycle") != "enacted":
                    continue
                if yielding["category"] != entry["category"] or state_of(yielding) != entry["state"]:
                    continue
                if not matches(yielding, entry["yielding"]):
                    continue
                for prevailing in self.rules:
                    if prevailing.get("lifecycle") != "enacted":
                        continue
                    if prevailing["category"] != yielding["category"] or state_of(prevailing) != entry["state"]:
                        continue
                    if yielding is not prevailing and matches(prevailing, entry["prevailing"]):
                        edges[(yielding["team_rule_id"], prevailing["team_rule_id"])] = entry
        # Circular declarations cannot produce a consistent answer.
        outgoing = defaultdict(set)
        for yielding, prevailing in edges:
            outgoing[yielding].add(prevailing)
        def visit(node, ancestors):
            if node in ancestors:
                raise ValueError("取代关系形成循环")
            for other in outgoing[node]:
                visit(other, ancestors | {node})
        for node in list(outgoing):
            visit(node, set())
        return edges

    def _review_pairs(self):
        """State/city pairs whose priority the sources leave open; every entry needs a quoted basis."""
        pairs = {}
        for entry in self.review:
            if not entry.get("basis") or not entry.get("source"):
                raise ValueError("需人工复核的州/市关系必须有原文依据和来源")
            for state_rule in self.rules:
                if state_rule["level"] != "state" or state_rule.get("lifecycle") != "enacted":
                    continue
                if state_rule["category"] != entry["category"] or state_of(state_rule) != entry["state"]:
                    continue
                if not matches(state_rule, entry["state_rule"]):
                    continue
                for city_rule in self.rules:
                    if city_rule["level"] != "city" or city_rule.get("lifecycle") != "enacted":
                        continue
                    if city_rule["category"] != entry["category"] or state_of(city_rule) != entry["state"]:
                        continue
                    if matches(city_rule, entry["city_rule"]):
                        pairs[(state_rule["team_rule_id"], city_rule["team_rule_id"])] = entry
        return pairs

    @staticmethod
    def _coverage(rule, address, day):
        a = rule.get("applicability") or {}
        checks, missing, failures = [], [], []

        def add(field, fact, outcome, explanation):
            checks.append({"field": field, "fact": fact, "outcome": outcome, "explanation": explanation})
            if outcome == "unknown":
                missing.append((field, explanation))
            elif outcome == "excluded":
                failures.append(explanation)

        year = address.get("year_built")
        basis = a.get("date_basis") or "unspecified"
        exact = address.get(basis) if basis in {"construction_date", "certificate_of_occupancy"} else None
        actual = query_date(exact) if exact else None
        label = "certificate of occupancy date" if basis == "certificate_of_occupancy" else "construction date"

        def cutoff(field, value, before):
            start, end = date_interval(value)
            if actual:
                if start != end and start <= actual <= end:
                    add(field, exact, "unknown", "the source gives the cutoff only to the year or month, so the boundary cannot be settled")
                else:
                    passed = actual <= start if before else actual > end
                    add(field, exact, "met" if passed else "excluded", "the %s is %s and the cutoff is %s" % (label, exact, value))
            elif year is None:
                add(field, None, "unknown", "the data has no year built and no %s" % label)
            elif start.year == year:
                # A year alone cannot decide a mid-year cutoff, especially a certificate date.
                if basis == "construction_date" and start == dt.date(year, 1, 1) and end == dt.date(year, 12, 31):
                    add(field, year, "met" if before else "excluded", "year built %s is the cutoff year" % year)
                else:
                    add(field, year, "unknown", "year built is %s, the cutoff is %s, and the data has no exact %s to place the building before or after it" % (year, value, label))
            else:
                passed = year < start.year if before else year > end.year
                add(field, year, "met" if passed else "excluded", "year built is %s; the %s cutoff is %s" % (year, label, value))

        if a.get("built_on_or_before"):
            cutoff("built_on_or_before", a["built_on_or_before"], True)
        if a.get("built_after"):
            cutoff("built_after", a["built_after"], False)
        if a.get("exempt_if_newer_than_years") is not None:
            years = a["exempt_if_newer_than_years"]
            target_year = day.year - years
            boundary = day.replace(year=target_year, day=min(day.day, calendar.monthrange(target_year, day.month)[1]))
            cutoff("exempt_if_newer_than_years", boundary.isoformat(), True)
            last = checks[-1]
            if last["outcome"] == "met":
                last["explanation"] = "the building dates from %s, too old for the rule's exemption of housing first occupied in the previous %s years" % (actual.year if actual else year, years)
            elif last["outcome"] == "excluded":
                failures[-1] = last["explanation"] = "the building dates from %s, inside the rule's exemption for housing first occupied in the previous %s years" % (actual.year if actual else year, years)

        units, lower = address.get("units"), address.get("units_at_least")
        for field, is_min in (("min_units", True), ("max_units", False)):
            threshold = a.get(field)
            if threshold is None:
                continue
            if units is not None:
                passed = units >= threshold if is_min else units <= threshold
                add(field, {"units": units}, "met" if passed else "excluded", "the building has %s units; the rule requires %s %s" % (units, "at least" if is_min else "no more than", threshold))
            elif lower is not None and lower >= threshold and is_min:
                add(field, {"units_at_least": lower}, "met", "the land-use record shows at least %s units, which meets the minimum of %s" % (lower, threshold))
            elif lower is not None and lower > threshold and not is_min:
                add(field, {"units_at_least": lower}, "excluded", "the building has at least %s units, above the rule's limit of %s" % (lower, threshold))
            else:
                add(field, {"units": units, "units_at_least": lower}, "unknown", "the data has no exact unit count, and the known minimum cannot settle the threshold of %s units" % threshold)

        if a.get("owner_dependent"):
            maximum = a.get("owner_exempt_if_units_at_most")
            known_lower = units if units is not None else lower
            if maximum is not None and known_lower is not None and known_lower > maximum:
                add("owner_dependent", {"units_lower": known_lower, "exemption_max_units": maximum}, "met",
                    "the building has at least %s units, so the owner-based exception (limited to %s units) cannot apply" % (known_lower, maximum))
            else:
                add("owner_dependent", None, "unknown", "coverage depends on who the owner is or whether the owner lives there, and the data has no owner information")
        if a.get("other"):
            kind = a.get("other_kind") or other_kind(a["other"])
            if kind == "building":
                add("other", None, "unknown", "the data cannot settle this condition: %s" % a["other"])
            else:
                add("other", None, "note", "condition stated in the source: %s" % a["other"])
        if rule.get("coverage_note"):
            add("coverage_note", None, "note", "individual tenancies can differ: %s" % rule["coverage_note"])
        if rule.get("coverage_missing"):
            add("coverage_missing", None, "unknown", "coverage also depends on facts not in the data: %s" % rule["coverage_missing"])
        # A known exclusion wins even when other required facts are absent.
        return ("excluded" if failures else "unknown" if missing else "met"), checks, missing

    def _initial(self, rule, address, as_of):
        day = query_date(as_of)
        trace = {"team_rule_id": rule["team_rule_id"], "steps": [], "missing_facts": [],
                 "source": {"citation": rule["citation"], "source_url": rule.get("source_url"), "retrieved": rule.get("retrieved"),
                            "quoted_span": rule.get("quoted_span"), "coverage_sources": rule.get("coverage_sources", []),
                            "date_source": rule.get("date_source"), "fact_corrections": rule.get("overrides_applied") or []}}
        def step(number, outcome, facts, explanation):
            trace["steps"].append({"step": number, "outcome": outcome, "facts": facts, "explanation": explanation})
        def done(result, explanation, number):
            trace.update(result=result, stopped_at_step=number, explanation=explanation)
            return result, explanation, trace
        if state_of(rule) != address["state"]:
            step(1, "excluded", {"state": address["state"]}, "the address is in a different state")
            return done(None, "the address is in a different state", 1)
        if rule["level"] == "city":
            legal_city = address.get("legal_city")
            if legal_city is None and not address.get("jurisdiction_known", False):
                message = "the legal city of this address could not be determined, so it is not known whether it lies in %s" % rule["jurisdiction"]
                step(1, "unknown", {"legal_city": None}, message)
                trace["missing_facts"] = [{"field": "legal_city", "explanation": message}]
                # Failed rules are never emitted, even for an unresolved city.
                if rule.get("lifecycle") in {"failed", "withdrawn"}:
                    step(2, "excluded", {"lifecycle": rule["lifecycle"]}, "the measure failed or was withdrawn")
                    return done(None, "the measure failed or was withdrawn", 2)
                return done("unknown", message, 1)
            if legal_city != rule["jurisdiction"]:
                step(1, "excluded", {"legal_city": legal_city, "resolved_by": address.get("resolved_by")}, "the address is in a different city")
                return done(None, "the address is in a different city", 1)
        step(1, "met", {"state": address["state"], "legal_city": address.get("legal_city"), "resolved_by": address.get("resolved_by")}, "the address is inside the rule's jurisdiction")
        if rule.get("lifecycle") in {"failed", "withdrawn"}:
            step(2, "excluded", {"lifecycle": rule["lifecycle"]}, "the measure failed or was withdrawn")
            return done(None, "the measure failed or was withdrawn", 2)
        step(2, "met", {"lifecycle": rule.get("lifecycle")}, "the measure has not failed")
        if rule.get("lifecycle") == "pending_bill":
            step(3, "pending", {"lifecycle": "pending_bill"}, "this is still a proposal, not enacted law")
            return done("pending", "The address is in %s, but this is a proposal that has not become law" % rule["jurisdiction"], 3)
        if rule.get("lifecycle") != "enacted":
            message = "the record does not say whether the measure was enacted, and the extraction-time status is not used in its place"
            step(3, "unknown", {"lifecycle": rule.get("lifecycle")}, message)
            trace["missing_facts"] = [{"field": "lifecycle", "explanation": message}]
            return done("unknown", message, 3)
        step(3, "met", {"lifecycle": "enacted"}, "the rule is enacted")
        status = status_on(rule, as_of)
        if status == "not_yet_effective":
            message = "Enacted, but it takes effect on %s, after the query date %s" % (rule["effective_date"], as_of)
            step(4, status, {"effective_date": rule["effective_date"], "as_of": as_of}, message)
            return done(status, message, 4)
        if status == "unknown":
            message = "the effective date is known only to the year or month, and the query date %s falls inside that span" % as_of
            step(4, "unknown", {"effective_date": rule["effective_date"], "as_of": as_of}, message)
            trace["missing_facts"] = [{"field": "effective_date", "explanation": message}]
            return done("unknown", message, 4)
        step(4, "met", {"effective_date": rule.get("effective_date"), "as_of": as_of}, "no effective date later than the query date")
        if rule.get("valid_through") and day > date_interval(rule["valid_through"])[1]:
            message = "the figure in this rule is published for a period ending %s and is not reported for %s" % (rule["valid_through"], as_of)
            step(4, "excluded", {"valid_through": rule["valid_through"], "as_of": as_of}, message)
            return done(None, message, 4)
        no_date = not rule.get("effective_date")
        step(5, "met", {"effective_date": rule.get("effective_date"), "date_source": rule.get("date_source")}, "the source states no effective date; treated as in force" if no_date else "the effective date has passed")
        coverage, checks, missing = self._coverage(rule, address, day)
        step(6, coverage, checks, "checked building date, unit count, owner and other coverage conditions")
        trace["missing_facts"] = [{"field": field, "explanation": explanation} for field, explanation in missing]
        details = [check["explanation"] for check in checks if check["outcome"] in (("excluded",) if coverage == "excluded" else ("unknown",) if coverage == "unknown" else ("met", "note"))]
        message = "; ".join(details) if details else "The address is in %s and the rule lists no further coverage condition" % rule["jurisdiction"]
        if no_date:
            message += "; the source states no effective date"
        if coverage == "excluded":
            return done(None, message, 6)
        if coverage == "unknown":
            return done("unknown", message, 6)
        return done("applies", message, 8)

    def evaluate(self, address_id, as_of=DEFAULT_DATE):
        query_date(as_of)
        address = self.addresses[address_id]
        results, traces = {}, {}
        for rule in self.rules:
            result, explanation, trace = self._initial(rule, address, as_of)
            traces[rule["team_rule_id"]] = trace
            if result:
                results[rule["team_rule_id"]] = {"team_rule_id": rule["team_rule_id"], "result": result,
                                               "explanation": explanation, "conflict_flag": False}
        # Resolve dependency chains from the most prevailing rule first.
        visited = set()
        def resolve(rid):
            if rid in visited:
                return
            visited.add(rid)
            candidate = results.get(rid)
            if not candidate or candidate["result"] not in {"applies", "unknown"}:
                return
            edges = [(p, entry) for (y, p), entry in self.edges.items() if y == rid]
            for prevailing, entry in edges:
                resolve(prevailing)
            applicable = [(p, e) for p, e in edges if p in results and results[p]["result"] == "applies"]
            uncertain = [(p, e) for p, e in edges if p in results and results[p]["result"] == "unknown"]
            # Coverage unknown stops at step 6; don't claim it is superseded.
            if applicable and candidate["result"] == "applies":
                candidate["result"] = "superseded"
                candidate["explanation"] += "; %s applies to this address, so this rule yields to it. Basis: %s" % (", ".join(self.by_id[p]["citation"] for p, _ in applicable), applicable[0][1]["basis"])
            elif uncertain:
                candidate["result"] = "unknown"
                candidate["explanation"] += "; it also depends on whether the city rule covers this address, which the data cannot settle"
            if applicable or uncertain:
                traces[rid]["steps"].append({"step": 7, "outcome": candidate["result"], "facts": [{"rule": p, "result": results[p]["result"], "basis": e["basis"]} for p, e in applicable + uncertain], "explanation": candidate["explanation"]})
                traces[rid]["stopped_at_step"] = 7
                if uncertain and not applicable:
                    traces[rid]["missing_facts"].append({"field": "precedence_coverage", "explanation": "whether the prevailing city rule covers this address is not known"})
        for rid in list(results):
            resolve(rid)
        pairs = []
        for (state_id, city_id), entry in sorted(self.review_pairs.items()):
            if state_id not in results or city_id not in results:
                continue
            if (state_id, city_id) in self.edges or (city_id, state_id) in self.edges:
                continue
            results[state_id]["conflict_flag"] = results[city_id]["conflict_flag"] = True
            pairs.append([state_id, city_id])
        for rid, result in results.items():
            rule = self.by_id[rid]
            if result["conflict_flag"]:
                result["explanation"] += "; " + REVIEW_NOTE
            date_sources = sorted({correction["source"] for correction in rule.get("overrides_applied") or []
                                   if "effective_date" in correction.get("after", {}) and correction.get("source")})
            if date_sources:
                result["explanation"] += "; effective date taken from: " + ", ".join(date_sources)
            retrieved = rule.get("retrieved") or next((s.get("retrieved") for s in rule.get("sources") or [] if s.get("retrieved")), "not recorded")
            result["explanation"] = sentence(result["explanation"]) + " Source: %s, %s (retrieved %s). %s" % (rule["citation"], rule.get("source_url", ""), retrieved, DISCLAIMER)
            trace = traces[rid]
            if trace["stopped_at_step"] == 8:
                trace["steps"].append({"step": 7, "outcome": "met", "facts": [], "explanation": "no applicable rule requires this one to yield"})
                trace["steps"].append({"step": 8, "outcome": result["result"], "facts": [], "explanation": "coverage conditions are met"})
            trace.update(result=result["result"], explanation=result["explanation"], conflict_flag=result["conflict_flag"],
                         source={"citation": rule["citation"], "source_url": rule.get("source_url"), "retrieved": retrieved,
                                 "quoted_span": rule.get("quoted_span"), "coverage_sources": rule.get("coverage_sources", []),
                                 "date_source": rule.get("date_source"), "fact_corrections": rule.get("overrides_applied") or []})
        return [results[k] for k in sorted(results)], {"rules": [traces[k] for k in sorted(traces)], "conflict_pairs": pairs}

    def lookup(self, address_id, as_of=DEFAULT_DATE):
        return self.evaluate(address_id, as_of)[0]

    def all(self, as_of=DEFAULT_DATE):
        lookups, audit = {}, {}
        for aid in sorted(self.addresses):
            lookups[aid], audit[aid] = self.evaluate(aid, as_of)
        return {"as_of": as_of, "lookups": lookups}, {"as_of": as_of, "disclaimer": DISCLAIMER, "addresses": audit}

    def exported_rules(self, as_of=DEFAULT_DATE, lookup_payload=None):
        if lookup_payload is None:
            lookup_payload = self.all(as_of)[0]
        flagged = {row["team_rule_id"] for rows in lookup_payload["lookups"].values() for row in rows if row["conflict_flag"]}
        output = []
        for rule in self.rules:
            record = {k: copy.deepcopy(rule.get(k)) for k in FIELDS}
            record["status"] = status_on(rule, as_of)
            if record["status"] == "unknown":
                raise ValueError("规则%s缺少准确的通过状态或生效日期，无法导出四种状态之一" % rule["team_rule_id"])
            record["overrides"] = sorted(y for y, p in self.edges if p == rule["team_rule_id"])
            record["interaction"] = "; ".join(sorted({entry["basis"] for (y, p), entry in self.edges.items() if rule["team_rule_id"] in {y, p}})) or rule.get("interaction")
            record["conflict_flag"] = rule["team_rule_id"] in flagged
            record["conflict_note"] = REVIEW_NOTE[0].upper() + REVIEW_NOTE[1:] + "." if record["conflict_flag"] else None
            record["retrieved"] = rule.get("retrieved")
            record["applicability"] = copy.deepcopy(rule.get("applicability") or {})
            record["coverage_sources"] = copy.deepcopy(rule.get("coverage_sources", []))
            record["date_source"] = rule.get("date_source")
            record["fact_corrections"] = copy.deepcopy(rule.get("overrides_applied") or [])
            if rule.get("valid_through"):
                record["valid_through"] = rule["valid_through"]
            record["disclaimer"] = DISCLAIMER
            output.append(record)
        return output


def lookup(address_id, as_of=DEFAULT_DATE):
    """File-backed public entry point; engine instances support repeated queries."""
    return LookupEngine.from_files().lookup(address_id, as_of)
