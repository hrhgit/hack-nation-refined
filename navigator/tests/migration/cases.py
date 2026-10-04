"""Contract inputs shared by the Python baseline and the TypeScript implementation."""
import copy
import itertools
import json

import test_pipeline as pipeline
from test_stage23 import rule, address, relationship, open_question

SPAN = "A landlord shall not demand or receive a security deposit exceeding one month’s rent."

def cases():
    result = []
    def add(name, op, args, **kw):
        result.append(dict(name=name, op=op, args=args, **kw))
    for n, text in enumerate([
        'prose ```json\n{"category":"x","a":{"b":"}\\\""},}\n```',
        '{"rules":[{"category":"x"}]}', '{"packet_id":"D100-01","n_rules":0}',
        '{"category":"x"', '{ stray prose\n{"category":"x"}',
        '{"category": bad} {"packet_id":"D100-01","n_rules":1}', '',
        '{"category":"x","quoted_span":"escaped \\\\ path and { braces }"}',
    ]):
        add("json_%02d" % n, "parse", {"text": text})
    for n, text in enumerate([
        "Home\nAbout\nHelp\nSearch\nLogin\nTerms\nContact\nMenu\n\nSection 1. Security deposit $100.\n",
        "\ufeffTitle\u200b\n\n\n(a). Clause\n1. Real law\nNo rent increase.\n",
        "Rent control limits five units. " * 210, "😀 §1. 法律\nSecurity deposit 2 months\r\n",
    ]):
        add("clean_%02d" % n, "clean", {"text": text})
        add("blocks_%02d" % n, "blocks", {"text": text, "budget": 3500})
    for n, (body, span) in enumerate([
        (SPAN, SPAN.replace("’", "'")),
        ("First three words here, followed by many middle words, and the final three words.", "First three words [...] final three words."),
        ("A landlord shall not demand or receive a security deposit exceeding one month of rent.", "A landlord shall not demand or receive any security deposit exceeding one month of rent."),
        (SPAN, "An invented sentence with no matching words in the source."),
        ("😀 prefix “A landlord shall not demand or receive a security deposit.”", '“A landlord shall not demand or receive a security deposit.”'),
        ("法律内容租金 上限为五 单元以上适用", "法律内容租金 上限为五 单元以上适用"),
        (SPAN, "one month"),
    ]):
        add("span_%02d" % n, "span", {"body": body, "span": span})
    values = [None, "2026", "2026-10", "2026-02-30", "Jan 1st, 2027", "1 July 2027", "7/1/27", "February 2027", "someday"]
    for n, value in enumerate(values):
        add("normalize_date_%02d" % n, "facts", {"name": "normalize_date", "value": value})
    for name, texts in {
        "doc_dates": ["Approved March 5, 2024. 3-28-2024; 7/1/27; 1979-06-13; February 2027.", "none"],
        "numbers_in": ["a fee of $ 1, 000 within ( 30) days; one and one-half months; twenty-five units", "😀 six $1,500.50"],
        "normalize_citation": ["Cal. Civ. Code Section 1947.12(a)(2), subdivision (b)", "Hoboken § 155-14"],
        "citation_key": ["G.L. c. 186, §15B(a)", "Ord. 2026-31 (Code §8.99.010)"],
        "split_citation": ["Cal. Civ. Code §1950.5: service member rules", "G.L. c. 186, §15B, deposit limit"],
        "normalize_jurisdiction": ["the city and county of San Francisco, California", "new jersey", " Cambridge , ma ", "something"],
        "act_dates": [pipeline.D104_BODY, "This act takes effect immediately. Approved March 5, 2024.",
                      "This ordinance shall be effective thirty ( 30) days after its adoption. ADOPTED this 3rd day of March, 2026.",
                      "This act takes effect immediately. Approved March 5, 2024. Approved April 2, 2024."],
    }.items():
        for n, text in enumerate(texts):
            add("facts_%s_%02d" % (name, n), "facts", {"name": name, "value": text})
    for n, value in enumerate(["2024", "2024-02", "2024-02-29", "2026-02-30", "next week", "0000", "2026-13"]):
        add("date_interval_%02d" % n, "date_interval", {"value": value}, error=n >= 3)
    for n, value in enumerate(["2024-02-29", "2026-02-30", "2026-1-1", None]):
        add("query_date_%02d" % n, "query_date", {"value": value}, error=n > 0)
    for n, value in enumerate(["Hoboken Mun. Code §155-14", "SF Admin. Code §37.9", "Berkeley §13.76.110",
                               "Jersey City §19:2-18", "Ord. 2026-31", "G.L. c. 186, §15B"]):
        add("chapter_%02d" % n, "chapter", {"value": value})
    for n, value in enumerate(["", None, "0", "12", "-1", True, "1.5"]):
        add("integer_%02d" % n, "integer", {"value": value}, error=n >= 4)
    for n, value in enumerate(["Five or more apartments", "Apartment 4 to 8 units", "7U/24U", ">4-unit", "duplex", "5+ units", "3 units or more"]):
        add("units_%02d" % n, "unit_lower_bound", {"value": value})
    add("batch_match", "parse_batch", {"text": 'A,"address",Match,Exact,"matched","-71.2,42.1"\n', "ids": ["A"]})
    add("batch_missing", "parse_batch", {"text": '', "ids": ["A"]}, error=True)
    add("batch_duplicate", "parse_batch", {"text": 'A,addr,No_Match\nA,addr,No_Match\n', "ids": ["A"]}, error=True)
    schema = {"type": "object", "required": ["s"], "properties": {"s": {"type": "string", "minLength": 3}, "n": {"type": "integer", "minimum": 0}}}
    for n, value in enumerate([{"s": "abc", "n": 0}, {"s": "x", "n": True}, {"n": -2}, [], {"s": "😀a"}]):
        add("schema_%02d" % n, "schema", {"value": value, "schema": schema})
    add("schema_special_field_names", "schema", {"value": {}, "schema": {"type": "object", "required": ["__proto__", "constructor"]}})
    add("schema_unknown_type", "schema", {"value": {}, "schema": {"type": "constructor"}}, error=True)
    add("facts_special_word", "facts", {"name": "numbers_in", "value": "constructor __proto__ five"})
    add("jurisdiction_special_word", "facts", {"name": "normalize_jurisdiction", "value": "constructor"})
    add("conditions_unknown_operator", "conditions", {"value": {"conditions": [
        {"type": "built", "role": "covered", "op": "constructor", "date": "1979"}]}})
    condsets = []
    for role, op in itertools.product(["covered", "exempt"], ["before", "after", "on_or_before", "on_or_after"]):
        condsets.append([{"type": "built", "role": role, "op": op, "date": "1979-06-13", "basis": "certificate_of_occupancy"}])
    for role, op in itertools.product(["covered", "exempt"], ["at_least", "more_than", "at_most", "fewer_than"]):
        condsets.append([{"type": "units", "role": role, "op": op, "n": 4}])
    condsets += [
        [{"type": "built_within_years", "role": "exempt", "years": 15, "conditional": True}],
        [{"type": "owner", "role": "exempt", "who": "owner-occupied", "unit_limit": 2}],
        [{"type": "owner", "role": "exempt", "who": "natural person"}, {"type": "owner", "role": "exempt", "who": "owner-occupied", "unit_limit": 2}],
        [{"type": "other", "role": "exempt", "text": "Section 8 subsidized units"}],
        [{"type": "other", "role": "covered", "text": "only subsidized units"}],
        [{"type": "built", "role": "exempt", "op": "after", "date": "1979-06-13", "group": "window"},
         {"type": "built", "role": "exempt", "op": "before", "date": "1980", "group": "window"}],
        ["x", {"type": "mystery"}, {"type": "built"}],
        [{"type": "units", "role": "exempt", "op": "at_most", "n": 99}],
    ]
    for n, value in enumerate(condsets):
        add("conditions_%02d" % n, "conditions", {"value": {"conditions": value, "coverage_quotes": []},
                                                   "dates": ["1979-06-13", "1980"], "nums": ["4", "2", "15"]})
    add("conditions_new_building_benefit", "conditions", {"value": {"conditions": [
        {"type": "built_within_years", "role": "covered", "years": 30, "basis": "construction"}]}})
    add("conditions_alternative", "conditions", {"value": {"conditions": [
        {"type": "built", "role": "covered", "op": "before", "date": "1979-06-13", "also": "replacement units", "basis": "construction"}]}})
    add("conditions_legacy", "conditions", {"value": {"min_units": "3", "built_before": "1979", "owner_dependent": "true"}})
    add("conditions_bad_types", "conditions", {"value": {"conditions": "bad", "min_units": True, "coverage_quotes": "bad"}})
    add("conditions_bad_object", "conditions", {"value": "x"})
    add("relations", "relations", {"body": "A municipality shall be prohibited from enacting an ordinance that conflicts with this act.",
        "value": [{"type": "preempts_local", "quote": "A municipality shall be prohibited from enacting an ordinance that conflicts with this act."},
                  {"type": "invented", "quote": "bad quote"}, {"type": "yields_to_local", "quote": "A totally invented source passage with different facts."}]})
    addresses = {"A%03d" % i: address(year_built=year, units=units, units_at_least=lower)
                 for i, (year, units, lower) in enumerate(itertools.product([None, 1950, 1979, 1980, 2011, 2022], [None, 2, 5], [None, 5]))}
    addresses.update({"NJ": address(state="NJ", legal_city="Newark, NJ"), "unresolved": address(legal_city=None),
                      "outside": address(legal_city=None, jurisdiction_known=True),
                      "exact": address(year_built=1979, certificate_of_occupancy="1979-06-13")})
    appls = [{}, {"min_units": 4}, {"max_units": 4}, {"built_before": "1979-06-13"},
             {"built_on_or_before": "1979", "date_basis": "construction_date"},
             {"built_after": "1979-06-13"}, {"built_on_or_after": "1979-06-13"},
             {"exempt_if_newer_than_years": 15, "date_basis": "certificate_of_occupancy"},
             {"covered_if_newer_than_years": 30, "date_basis": "construction_date"},
             {"alternatives": [{"flats": {"built_before": "1979-06-13", "date_basis": "construction_date"}, "also": "replacement units"}]},
             {"owner_dependent": True, "owner_exempt_if_units_at_most": 2},
             {"owner_dependent": True}, {"other": "only registered units", "contract": 2},
             {"other": "when collecting a fee", "other_kind": "trigger"},
             {"program_notes": ["subsidized units"], "per_tenancy": "lease exemption"},
             {"deferred": [{"flats": {"min_units": 5}, "note": "4 or fewer units", "conditional": True}]},
             {"deferred": [{"flats_all": [{"built_on_or_before": "1979"}, {"built_on_or_after": "1980"}], "note": "window", "conditional": False}]},
             ]
    rules = [rule("R%03d" % i, "Los Angeles, CA", applicability=a) for i, a in enumerate(appls)]
    rules += [rule("life_%s" % (life or "missing"), lifecycle=life) for life in [None, "enacted", "pending_bill", "failed", "withdrawn"]]
    rules += [rule("date_%d" % i, effective_date=eff) for i, eff in enumerate(["2026", "2026-10", "2026-10-01", "2027-01-01"])]
    rules += [rule("valid", valid_through="2026-10"), rule("coverage_missing", coverage_missing="owner filing")]
    for day in ["2024-02-29", "2026-01-01", "2026-10-01", "2026-10-31", "2027-07-01"]:
        add("engine_matrix_" + day.replace("-", "_"), "engine", {"rules": rules, "addresses": addresses, "as_of": day})
    for kind, prec, review in [("precedence", [relationship()], []), ("review", [], [open_question()])]:
        add("engine_" + kind, "engine", {"rules": [rule("state"), rule("city", "Los Angeles, CA", applicability={"min_units": 5})],
            "addresses": addresses, "precedence": prec, "review": review, "export": True})
    for n, bad in enumerate([rule(""), rule(category="bad"), rule(lifecycle="bad"), rule(effective_date="2026-02-30"),
                             rule(applicability={"min_units": True}), rule(level="city")]):
        add("engine_invalid_%02d" % n, "engine", {"rules": [bad], "addresses": {"A": address()}}, error=True)
    add("engine_duplicate", "engine", {"rules": [rule(), rule()], "addresses": {"A": address()}}, error=True)
    add("engine_special_identifiers", "engine", {"rules": [rule("__proto__"), rule("constructor")],
        "addresses": {"__proto__": address(), "constructor": address()}})
    add("engine_null_source_and_empty_interaction", "engine", {"rules": [rule(source_url=None, interaction="")],
        "addresses": {"A": address()}, "export": True})
    add("conditions_special_group_name", "conditions", {"value": {"conditions": [
        {"type": "built", "role": "exempt", "op": "after", "date": "1979", "group": "__proto__"},
        {"type": "built", "role": "exempt", "op": "before", "date": "1980", "group": "__proto__"}]}})
    add("engine_cycle", "engine", {"rules": [rule("state"), rule("city", "Los Angeles, CA")], "addresses": {"A": address()},
        "precedence": [relationship(), relationship(yielding={"level": "city"}, prevailing={"level": "state"})]}, error=True)
    tests = [{"test_id": "T1", "type": "as_of", "as_of_before": "2026-12-31", "as_of_after": "2027-01-01", "rule_ids": ["future"]},
             {"test_id": "T2", "type": "boundary", "as_of": "2026-10-01", "rule_ids": ["city"]},
             {"test_id": "T3", "type": "pending", "as_of": "2026-10-01", "rule_ids": ["pending"]},
             {"test_id": "T4", "type": "negative", "as_of": "2026-10-01", "rule_ids": ["failed"], "states": ["MA"]}]
    changes_args = {"rules": [rule("future", effective_date="2027-01-01"), rule("city", "Los Angeles, CA"),
                    rule("pending", lifecycle="pending_bill"), rule("failed", "MA", lifecycle="failed")],
                    "addresses": {"A": address(), "B": address(state="MA", legal_city="Boston, MA")}, "tests": tests,
                    "rule_map": {k: {"team_rule_id": k} for k in ["future", "city", "pending", "failed"]}}
    add("changes_all_types", "changes", changes_args)
    add("changes_special_test_id", "changes", dict(changes_args, tests=[dict(tests[0], test_id="__proto__")]))
    add("changes_date_override", "changes", dict(changes_args, date_overrides={"T1": {"as_of_after": "2028-01-01"}}))
    add("changes_unknown_override", "changes", dict(changes_args, date_overrides={"unknown": {}}), error=True)
    add("changes_invalid_override", "changes", dict(changes_args, date_overrides={"T2": {"as_of_after": "2028-01-01"}}), error=True)
    add("changes_missing_rule", "changes", dict(changes_args, rules=[]))
    good = pipeline.rec(quoted_span=SPAN)
    receipt = {"packet_id": "D100-01", "n_rules": 1, "note": None}
    def answer(records, recpt=receipt):
        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records + ([recpt] if recpt else []))
    for name, answers in [
        ("empty", {}), ("good", {"answer.txt": answer([good])}),
        ("no_receipt", {"answer.txt": answer([good], None)}),
        ("receipt_mismatch", {"answer.txt": answer([good], dict(receipt, n_rules=0))}),
        ("invented_quote", {"answer.txt": answer([dict(good, quoted_span="A made up sentence that cannot be found in the original.")])}),
        ("wrong_category", {"answer.txt": answer([dict(good, category="made_up")])}),
        ("missing_field", {"answer.txt": answer([{k: v for k, v in good.items() if k != "requirement"}])}),
        ("unsupported_value", {"answer.txt": answer([dict(good, key_value="$9999")])}),
        ("wrong_date", {"answer.txt": answer([dict(good, effective_date="2099-01-01")])}),
        ("normalization", {"answer.txt": answer([dict(good, quoted_span=SPAN.replace("’", "'"), jurisdiction="City of Cambridge, MA", effective_date="January 1, 2027")])}),
        ("first_flow", {"answer1.txt": pipeline.PipelineTest().first_answer()}),
        ("duplicate_law", {"answer.txt": answer([good, dict(good, title="Same deposit cap")], dict(receipt, n_rules=2))}),
        ("wrong_packet", {"answer.txt": answer([dict(good, packet_id="D999-01")])}),
        ("invalid_receipt", {"answer.txt": answer([good], dict(receipt, n_rules=True))}),
        ("truncated", {"answer.txt": answer([good]) + '\n{"category":"security_deposits"'}),
        ("chapter_merge", {"answer.txt": answer([good, dict(good, citation="Cambridge Mun. Code §8.99.020", title="Deposit exception")], dict(receipt, n_rules=2))}),
    ]:
        add("pipeline_" + name, "pipeline", {"answers": answers, "fixture": {"manifest": pipeline.MANIFEST, "docs": {"D100": pipeline.D100, "D101": pipeline.D101, "D102": pipeline.D102}}})
    for n, value in enumerate(["https://api.deepseek.com", "http://127.0.0.1:1234/v1", "http://[::1]:1234", "http://example.com",
                               "https://user:secret@example.com", "https://api.deepseek.com?q=1", "file:///etc/passwd"]):
        add("api_endpoint_%02d" % n, "api_endpoint", {"value": value}, error=n >= 3)
    def reply(text, finish="stop"):
        return {"model": "deepseek-flash", "choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": finish}], "usage": {"prompt_tokens": 30, "completion_tokens": 20}}
    for n, value in enumerate([reply("ok"), {}, reply(""), reply(None), {"choices": []}]):
        add("api_answer_%02d" % n, "api_answer", {"value": value}, error=n > 0)
    for n, only in enumerate([None, ["D100"], ["D101-01"], ["bad"]]):
        add("api_select_%02d" % n, "api_select", {"pending": {"D100-01": [], "D101-01": ["fix"]},
            "index": {"packets": {"D100-01": {"doc_id": "D100"}, "D101-01": {"doc_id": "D101"}}, "docs": {"D100": {}, "D101": {}}}, "only": only}, error=n == 3)
    for name, text in [("good", answer([good])), ("wrong_packet", answer([dict(good, packet_id="D999-01")])),
                       ("duplicate_receipt", answer([good]) + "\n" + json.dumps(receipt)), ("no_json", "none"),
                       ("truncated", '{"packet_id":"D100-01"')]:
        add("check_final_" + name, "check_final", {"text": text}, error=name != "good")
    add("cards", "cards", {})
    fix = {"manifest": pipeline.MANIFEST, "docs": {"D100": pipeline.D100, "D101": pipeline.D101, "D102": pipeline.D102}}
    for n, text in enumerate(["{", "", "[]", json.dumps(good, ensure_ascii=False),
                             json.dumps(dict(good, quoted_span="made up sentence that is not there")),
                             json.dumps(dict(good, citation="42 USC 3604; 24 CFR 100.50")),
                             json.dumps(dict(good, effective_date=None, applicability={"conditions": [{"type": "built", "role": "covered", "op": "after", "date": "2027-01-01"}]}))]):
        add("tool_check_%02d" % n, "tool_check", {"fixture": fix, "text": text})
    bad = dict(good, quoted_span="A made up sentence that cannot be found in the original.")
    for op in ["api_run", "agent_run"]:
        for name, replies, extra in [("good", [reply(answer([good]))], {}),
                                    ("repair", [reply(answer([bad])), reply(answer([good]))], {}),
                                    ("once", [reply(answer([bad]))], {"once": True}),
                                    ("dry_run", [], {"dry_run": True}),
                                    ("truncated", [reply(answer([good]), "length")], {}),
                                    ("connection_error", [{"error": "HTTP 429"}], {})]:
            add(op + "_" + name, op, dict(fixture=fix, replies=replies, **extra))
    def tool(name, args, call_id):
        return {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [
            {"id": call_id, "type": "function", "function": {"name": name, "arguments": args}}]}, "finish_reason": "tool_calls"}], "usage": {}}
    add("agent_run_cards_and_self_check", "agent_run", {"fixture": fix, "replies": [
        tool("read_card", json.dumps({"name": "citations"}), "c1"),
        tool("check_record", json.dumps({"record_json": json.dumps(good, ensure_ascii=False)}), "c2"), reply(answer([good]))]})
    add("agent_run_unknown_tool_and_card", "agent_run", {"fixture": fix, "replies": [
        tool("read_card", "broken arguments", "c1"), tool("no_such_tool", "{}", "c2"), reply(answer([good]))]})
    for day in ["2026-10-01", "2027-07-01", "2024-02-29"]:
        add("real_all_" + day.replace("-", "_"), "real_all", {"as_of": day})
    for op in ["real_changes", "real_rules", "real_packets", "real_ingest", "real_census", "real_review", "real_requests"]:
        add(op, op, {})
    for route in ["meta", "rules", "changes", "pipeline"]:
        add("web_" + route, "web", {"route": route})
    for n, query in enumerate([{"address_id": ["A0001"]}, {"address_id": ["A0001"], "year_built": ["1960"], "units": ["5"]},
        {"address_id": ["A0001"], "as_of": ["2027-07-01"]}, {"address_id": ["Z9999"]},
        {"address_id": ["A0001"], "as_of": ["2026-02-30"]}, {"address_id": ["A0001"], "units": ["many"]}]):
        add("web_lookup_%02d" % n, "web", {"route": "lookup", "query": query}, error=n >= 3)
    for n, query in enumerate([{"doc_id": ["D024"], "quote": [""]}, {"doc_id": ["../.env"]}, {"doc_id": ["X999"]}]):
        add("web_source_%02d" % n, "web", {"route": "source", "query": query}, error=n > 0)
    return result
