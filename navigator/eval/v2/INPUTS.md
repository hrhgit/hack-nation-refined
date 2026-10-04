# 第二版样本与答案审阅

真实材料均保留为开发题；新题为助手构造的人工文本，尚无人独立核对。所有预期都在评分端；模型只收到原文。
本文件包含保留测试题答案，不能交给修改提示词的分析员。当前作者能读到本文件，因此不声称人员之间的盲测隔离。

|组别|文本包数|说明|
|---|---:|---|
|train|117|按文件/题型整组保留|
|validation|14|按文件/题型整组保留|
|test|12|按文件/题型整组保留|

## 新题原文与预期

### Z001-01 · size · validation

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-1
A landlord shall not demand a security deposit exceeding one month of rent.
This ordinance applies only to residential buildings containing at least 6 dwelling units.
Effective January 1, 2025.

预期记录数：1

[
  {
    "id": "below",
    "facts": {
      "year_built": 1960,
      "units": 5,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "excluded",
    "ok": [
      "excluded"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "at",
    "facts": {
      "year_built": 1960,
      "units": 6,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "missing",
    "facts": {
      "year_built": 1960,
      "units": null,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "unknown",
    "ok": [
      "unknown"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "conflict",
    "facts": {
      "year_built": 1960,
      "units": 2,
      "units_at_least": 7
    },
    "as_of": "2026-10-01",
    "exact": "unknown",
    "ok": [
      "unknown"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z002-01 · size · validation

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-2
A landlord shall not demand a security deposit exceeding one month of rent.
This ordinance applies only to residential buildings containing at least 9 dwelling units.
Effective January 1, 2025.

预期记录数：1

[
  {
    "id": "below",
    "facts": {
      "year_built": 1960,
      "units": 8,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "excluded",
    "ok": [
      "excluded"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "at",
    "facts": {
      "year_built": 1960,
      "units": 9,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "missing",
    "facts": {
      "year_built": 1960,
      "units": null,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "unknown",
    "ok": [
      "unknown"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "conflict",
    "facts": {
      "year_built": 1960,
      "units": 2,
      "units_at_least": 10
    },
    "as_of": "2026-10-01",
    "exact": "unknown",
    "ok": [
      "unknown"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z003-01 · owner · validation

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-3
A landlord shall not reject a tenant solely because rent is paid using a housing subsidy.
Owner-occupied premises with no more than 6 dwelling units are exempt from this ordinance.
Effective January 1, 2025.

预期记录数：1

[
  {
    "id": "owner-unknown",
    "facts": {
      "year_built": 1960,
      "units": 6,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "unknown",
    "ok": [
      "unknown"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "too-large-for-exemption",
    "facts": {
      "year_built": 1960,
      "units": 7,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z004-01 · owner · validation

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-4
A landlord shall not reject a tenant solely because rent is paid using a housing subsidy.
Owner-occupied premises with no more than 9 dwelling units are exempt from this ordinance.
Effective January 1, 2025.

预期记录数：1

[
  {
    "id": "owner-unknown",
    "facts": {
      "year_built": 1960,
      "units": 9,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "unknown",
    "ok": [
      "unknown"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "too-large-for-exemption",
    "facts": {
      "year_built": 1960,
      "units": 10,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z005-01 · effective · validation

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-5
A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
This ordinance takes effect on 2027-02-01.

预期记录数：1

[
  {
    "id": "before",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "not_yet_effective",
    "ok": [
      "not_yet_effective"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "on",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2027-02-01",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z006-01 · effective · validation

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-6
A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
This ordinance takes effect on 2027-03-01.

预期记录数：1

[
  {
    "id": "before",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "not_yet_effective",
    "ok": [
      "not_yet_effective"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "on",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2027-03-01",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z007-01 · empty · validation

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-7
This library bulletin lists opening hours and contains no rental housing requirements.


预期记录数：0

[]


### Z008-01 · empty · validation

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-8
Federal law only: 15 U.S.C. 1681m requires users of consumer reports to provide an adverse action notice. This page states no state or city rule.


预期记录数：0

[]


### Z009-01 · expiry · test

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-9
A landlord shall not demand a security deposit exceeding one month of rent.
This temporary security deposit rule remains valid through 2026-10-12 and expires the next day.
Effective January 1, 2025.

预期记录数：1

[
  {
    "id": "last-day",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-12",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "next-day",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-13",
    "exact": "excluded",
    "ok": [
      "excluded"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z010-01 · expiry · test

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-10
A landlord shall not demand a security deposit exceeding one month of rent.
This temporary security deposit rule remains valid through 2026-10-13 and expires the next day.
Effective January 1, 2025.

预期记录数：1

[
  {
    "id": "last-day",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-13",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "next-day",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-14",
    "exact": "excluded",
    "ok": [
      "excluded"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z011-01 · benefit · test

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-11
Newly constructed residential buildings are exempt from local rent control for 6 years following completion of construction.

Effective January 1, 2025.

预期记录数：1

[
  {
    "id": "new",
    "facts": {
      "year_built": 2025,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "old",
    "facts": {
      "year_built": 1990,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "excluded",
    "ok": [
      "excluded"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "boundary",
    "facts": {
      "year_built": 2020,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "unknown",
    "ok": [
      "unknown"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z012-01 · benefit · test

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-12
Newly constructed residential buildings are exempt from local rent control for 9 years following completion of construction.

Effective January 1, 2025.

预期记录数：1

[
  {
    "id": "new",
    "facts": {
      "year_built": 2025,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "old",
    "facts": {
      "year_built": 1990,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "excluded",
    "ok": [
      "excluded"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "boundary",
    "facts": {
      "year_built": 2017,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "unknown",
    "ok": [
      "unknown"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z013-01 · alternative · test

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-13
A landlord may terminate a residential tenancy only for a just cause listed in Section 9.
This ordinance covers buildings constructed before January 1, 1980, as well as replacement units built under Section 9.
Effective January 1, 2025.

预期记录数：1

[
  {
    "id": "old",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "replacement-unknown",
    "facts": {
      "year_built": 2020,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "unknown",
    "ok": [
      "unknown"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z014-01 · alternative · test

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-14
A landlord may terminate a residential tenancy only for a just cause listed in Section 9.
This ordinance covers buildings constructed before January 1, 1981, as well as replacement units built under Section 9.
Effective January 1, 2025.

预期记录数：1

[
  {
    "id": "old",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "applies",
    "ok": [
      "applies"
    ],
    "basis": "Explicit synthetic clause in this document."
  },
  {
    "id": "replacement-unknown",
    "facts": {
      "year_built": 2020,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "unknown",
    "ok": [
      "unknown"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z015-01 · pending · test

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-15
A landlord shall not charge an application screening fee exceeding 37 dollars.
This is a proposal still in committee. It has not been enacted and has no effective date.

预期记录数：1

[
  {
    "id": "proposal",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "pending",
    "ok": [
      "pending"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


### Z016-01 · pending · test

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Cambridge Ordinance No. 2099-16
A landlord shall not charge an application screening fee exceeding 37 dollars.
This is a proposal still in committee. It has not been enacted and has no effective date.

预期记录数：1

[
  {
    "id": "proposal",
    "facts": {
      "year_built": 1960,
      "units": 20,
      "units_at_least": null
    },
    "as_of": "2026-10-01",
    "exact": "pending",
    "ok": [
      "pending"
    ],
    "basis": "Explicit synthetic clause in this document."
  }
]


## 变更链题（文本包 → 入库 → 查询 → 变更题）

每题让模型提取一组文本包，再走正式的入库、地址查询和变更题，检查变更题的结果。真实链 CHAIN-T1 到 CHAIN-T5 用比赛随包的 `expected_behavior` 和 500 个已解析地址；构造链用虚构文本。预期都在评分端。


### CHAIN-T1 · chain:T1 · train

文本包：D022-01, X005-01；变更题：T1（as_of）

随包说明：not_yet_effective before, applies after, for every CA address.

[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": "250 项"
  },
  {
    "kind": "dated",
    "ids": "250 项",
    "before": "not_yet_effective",
    "after": "applies"
  }
]


### CHAIN-T2 · chain:T2 · train

文本包：D034-01, D035-01, D037-01, X102-01；变更题：T2（boundary）

随包说明：HOB-ALG-01 only for Hoboken addresses; JC-ALG-01 only for Jersey City addresses; neither for Newark.

[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": "90 项"
  },
  {
    "kind": "boundary",
    "by_address": "500 项"
  }
]


### CHAIN-T3 · chain:T3 · train

文本包：D069-01, D034-01, D035-01, D037-01, X102-01；变更题：T3（as_of）

随包说明：not_yet_effective on 2026-10-01, applies on 2027-07-02 for every NJ address; Jersey City and Hoboken addresses carry a conflict flag for human review.

[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": "140 项"
  },
  {
    "kind": "dated",
    "ids": "140 项",
    "before": "not_yet_effective",
    "after": "applies"
  },
  {
    "kind": "conflicts",
    "ids": "90 项"
  },
  {
    "kind": "rule_field",
    "jurisdiction": "NJ",
    "citation_regex": "56:9-20|c\\.\\s?43",
    "field": "effective_date",
    "equals": "2027-07-01"
  },
  {
    "kind": "rule_field",
    "jurisdiction": "NJ",
    "citation_regex": "56:9-20|c\\.\\s?43",
    "field": "relations",
    "contains": "preempts_local"
  }
]


### CHAIN-T4 · chain:T4 · train

文本包：D045-01, D046-01, D047-01；变更题：T4（pending）

随包说明：Reported as pending (not in force) for every Boston and Cambridge address; affected set = all MA addresses if enacted.

[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": "110 项"
  },
  {
    "kind": "pending"
  }
]


### CHAIN-T5 · chain:T5 · train

文本包：X101-01；变更题：T5（negative）

随包说明：No rent cap reported for any Boston or Cambridge address; IP 25-21 recorded as failed. Affected set is empty.

[
  {
    "kind": "no_error"
  },
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": []
  },
  {
    "kind": "rule_field",
    "jurisdiction": "MA",
    "citation_regex": "25-21",
    "field": "lifecycle",
    "equals": "failed"
  }
]


### CHAIN-RELATIVE-0 · chainrelative · validation

文本包：Y101-01；变更题：C-REL0（as_of）

INVENTED EVALUATION TEXT — not actual law.
MA
An Act Relating to Rent-Setting Software (Invented Act 2099-R0)
Section 1. A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
Section 2. This act shall take effect on the first day of the twelfth month next following its enactment.
Approved August 12, 2026.


[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": [
      "M1",
      "M2",
      "M3",
      "M4"
    ]
  },
  {
    "kind": "dated",
    "ids": [
      "M1",
      "M2",
      "M3",
      "M4"
    ],
    "before": "not_yet_effective",
    "after": "applies"
  },
  {
    "kind": "rule_field",
    "jurisdiction": "MA",
    "citation_regex": "2099-R0",
    "field": "effective_date",
    "equals": "2027-08-01"
  }
]


### CHAIN-RELATIVE-1 · chainrelative · validation

文本包：Y102-01；变更题：C-REL1（as_of）

INVENTED EVALUATION TEXT — not actual law.
MA
An Act Relating to Rent-Setting Software (Invented Act 2099-R1)
Section 1. A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
Section 2. This act takes effect ninety (90) days after its approval.
Approved September 10, 2026.


[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": [
      "M1",
      "M2",
      "M3",
      "M4"
    ]
  },
  {
    "kind": "dated",
    "ids": [
      "M1",
      "M2",
      "M3",
      "M4"
    ],
    "before": "not_yet_effective",
    "after": "applies"
  },
  {
    "kind": "rule_field",
    "jurisdiction": "MA",
    "citation_regex": "2099-R1",
    "field": "effective_date",
    "equals": "2026-12-09"
  }
]


### CHAIN-PREEMPT-0 · chainpreempt · validation

文本包：Y103-01, Y104-01；变更题：C-PRE0（as_of）

INVENTED EVALUATION TEXT — not actual law.
MA
An Act Relating to Rent-Setting Software (Invented Act 2099-P0)
Section 1. A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
Section 2. A municipality may not enact or enforce an ordinance that conflicts with this act.
Section 3. This act takes effect on January 1, 2028.


INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Ordinance Cambridge Invented Ordinance 2099-Q0
Section 1. A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
Section 2. This ordinance takes effect on January 1, 2025.


[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": [
      "M1",
      "M2",
      "M3",
      "M4"
    ]
  },
  {
    "kind": "dated",
    "ids": [
      "M1",
      "M2",
      "M3",
      "M4"
    ],
    "before": "not_yet_effective",
    "after": "applies"
  },
  {
    "kind": "conflicts",
    "ids": [
      "M3",
      "M4"
    ]
  },
  {
    "kind": "rule_field",
    "jurisdiction": "MA",
    "citation_regex": "2099-P0",
    "field": "relations",
    "contains": "preempts_local"
  }
]


### CHAIN-PREEMPT-1 · chainpreempt · validation

文本包：Y105-01, Y106-01；变更题：C-PRE1（as_of）

INVENTED EVALUATION TEXT — not actual law.
MA
An Act Relating to Rent-Setting Software (Invented Act 2099-P1)
Section 1. A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
Section 2. A municipality may not enact or enforce an ordinance that conflicts with this act.
Section 3. This act takes effect on July 1, 2029.


INVENTED EVALUATION TEXT — not actual law.
Boston, MA
Ordinance Boston Invented Ordinance 2099-Q1
Section 1. A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
Section 2. This ordinance takes effect on January 1, 2025.


[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": [
      "M1",
      "M2",
      "M3",
      "M4"
    ]
  },
  {
    "kind": "dated",
    "ids": [
      "M1",
      "M2",
      "M3",
      "M4"
    ],
    "before": "not_yet_effective",
    "after": "applies"
  },
  {
    "kind": "conflicts",
    "ids": [
      "M1",
      "M2"
    ]
  },
  {
    "kind": "rule_field",
    "jurisdiction": "MA",
    "citation_regex": "2099-P1",
    "field": "relations",
    "contains": "preempts_local"
  }
]


### CHAIN-BOUNDARY-0 · chainboundary · validation

文本包：Y107-01, Y108-01；变更题：C-BND0（boundary）

INVENTED EVALUATION TEXT — not actual law.
Hoboken, NJ
Ordinance Hoboken Invented Ordinance 2099-H0
Section 1. A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
Section 2. This ordinance takes effect on March 1, 2025.


INVENTED EVALUATION TEXT — not actual law.
Jersey City, NJ
Ordinance Jersey City Invented Ordinance 2099-J0
Section 1. A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
Section 2. This ordinance takes effect on June 1, 2025.


[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": [
      "H1",
      "H2",
      "J1",
      "J2"
    ]
  },
  {
    "kind": "boundary",
    "by_address": {
      "H1": [
        "CH-A"
      ],
      "H2": [
        "CH-A"
      ],
      "J1": [
        "CH-B"
      ],
      "J2": [
        "CH-B"
      ],
      "N1": []
    }
  }
]


### CHAIN-BOUNDARY-1 · chainboundary · validation

文本包：Y109-01, Y110-01；变更题：C-BND1（boundary）

INVENTED EVALUATION TEXT — not actual law.
Cambridge, MA
Ordinance Cambridge Invented Ordinance 2099-H1
Section 1. A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
Section 2. This ordinance takes effect on March 1, 2025.


INVENTED EVALUATION TEXT — not actual law.
Boston, MA
Ordinance Boston Invented Ordinance 2099-J1
Section 1. A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
Section 2. This ordinance takes effect on June 1, 2025.


[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": [
      "M1",
      "M2",
      "M3",
      "M4"
    ]
  },
  {
    "kind": "boundary",
    "by_address": {
      "M3": [
        "CH-A"
      ],
      "M4": [
        "CH-A"
      ],
      "M1": [
        "CH-B"
      ],
      "M2": [
        "CH-B"
      ],
      "L1": []
    }
  }
]


### CHAIN-PENDING-0 · chainpending · test

文本包：Y111-01；变更题：C-PND0（pending）

INVENTED EVALUATION TEXT — not actual law.
MA
A Bill Relating to Rent-Setting Software (Invented Bill H.990)
A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
This bill is pending in committee. It has not been enacted and has no effective date.


[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": [
      "M1",
      "M2",
      "M3",
      "M4"
    ]
  },
  {
    "kind": "pending"
  }
]


### CHAIN-PENDING-1 · chainpending · test

文本包：Y112-01；变更题：C-PND1（pending）

INVENTED EVALUATION TEXT — not actual law.
MA
A Bill Relating to Rent-Setting Software (Invented Bill H.991)
A landlord shall not use software that analyzes nonpublic competitor rent data to recommend residential rents.
This bill was referred to the Joint Committee on Housing and has not passed either chamber. It has no effective date.


[
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": [
      "M1",
      "M2",
      "M3",
      "M4"
    ]
  },
  {
    "kind": "pending"
  }
]


### CHAIN-FAILED-0 · chainfailed · test

文本包：Y113-01；变更题：C-FLD0（negative）

INVENTED EVALUATION TEXT — not actual law.
MA
An Initiative Petition to Limit Residential Rent Increases (Invented Initiative Petition 99-0).
On June 23, 2026 the Supreme Judicial Court ruled that the question may not be placed on the 2026 ballot. The measure will not appear and cannot take effect.


[
  {
    "kind": "no_error"
  },
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": []
  },
  {
    "kind": "rule_field",
    "jurisdiction": "MA",
    "citation_regex": "99-0",
    "field": "lifecycle",
    "equals": "failed"
  }
]


### CHAIN-FAILED-1 · chainfailed · test

文本包：Y114-01；变更题：C-FLD1（negative）

INVENTED EVALUATION TEXT — not actual law.
MA
An Initiative Petition to Limit Residential Rent Increases (Invented Initiative Petition 99-1).
The sponsors did not collect enough signatures, the question was never placed on the 2026 ballot, and the measure was abandoned. It cannot take effect.


[
  {
    "kind": "no_error"
  },
  {
    "kind": "no_missing_rules"
  },
  {
    "kind": "affected",
    "ids": []
  },
  {
    "kind": "rule_field",
    "jurisdiction": "MA",
    "citation_regex": "99-1",
    "field": "lifecycle",
    "equals": "failed"
  }
]


## 真实材料清单

|文本包|来源|条件答案数|随包引用可评分|
|---|---|---:|---|
|D001-01|starter|0|True|
|D003-01|starter|0|True|
|D004-01|starter|0|True|
|D005-01|starter|0|True|
|D006-01|starter|0|True|
|D007-01|starter|0|True|
|D008-01|starter|0|True|
|D009-01|starter|1|True|
|D010-01|starter|1|True|
|D011-01|starter|0|True|
|D012-01|starter|0|True|
|D013-01|starter|0|True|
|D014-01|starter|0|True|
|D016-01|starter|0|True|
|D016-02|starter|0|True|
|D022-01|starter|0|True|
|D023-01|starter|1|True|
|D023-02|starter|0|True|
|D024-01|starter|1|True|
|D025-01|starter|0|True|
|D025-02|starter|0|True|
|D026-01|starter|0|True|
|D027-01|starter|0|True|
|D029-01|starter|1|True|
|D031-01|starter|0|True|
|D032-01|extra|1|False|
|D032-02|extra|0|False|
|D032-03|extra|0|False|
|D032-04|extra|0|False|
|D033-01|extra|0|False|
|D033-02|extra|0|False|
|D034-01|extra|1|False|
|D035-01|extra|1|False|
|D036-01|starter|0|True|
|D037-01|extra|0|False|
|D038-01|extra|0|False|
|D039-01|starter|0|True|
|D040-01|starter|1|True|
|D041-01|starter|2|True|
|D042-01|starter|0|True|
|D043-01|starter|1|True|
|D043-02|starter|0|True|
|D044-01|extra|0|False|
|D045-01|starter|0|True|
|D046-01|starter|0|True|
|D047-01|starter|0|True|
|D048-01|starter|1|True|
|D049-01|starter|0|True|
|D049-02|starter|0|True|
|D049-03|starter|0|True|
|D050-01|starter|0|True|
|D051-01|starter|0|True|
|D052-01|starter|0|True|
|D052-02|starter|0|True|
|D053-01|starter|0|True|
|D056-01|extra|0|False|
|D056-02|extra|0|False|
|D057-01|starter|0|True|
|D058-01|starter|0|True|
|D061-01|extra|0|False|
|D061-02|extra|0|False|
|D062-01|extra|1|False|
|D063-01|extra|0|False|
|D064-01|extra|1|False|
|D065-01|starter|1|True|
|D066-01|starter|1|True|
|D067-01|starter|0|True|
|D067-02|starter|1|True|
|D067-03|starter|0|True|
|D067-04|starter|1|True|
|D068-01|starter|0|True|
|D069-01|starter|1|True|
|D070-01|extra|0|False|
|D070-02|extra|0|False|
|D070-03|extra|0|False|
|D070-04|extra|0|False|
|D071-01|extra|0|False|
|D071-02|extra|0|False|
|D072-01|extra|0|False|
|D072-02|extra|0|False|
|D073-01|starter|1|True|
|D073-02|starter|0|True|
|D074-01|extra|1|False|
|D075-01|extra|1|False|
|D076-01|starter|0|True|
|D078-01|starter|0|True|
|D079-01|starter|1|True|
|D080-01|starter|1|True|
|D081-01|starter|0|True|
|D082-01|starter|0|True|
|D083-01|starter|0|True|
|D084-01|starter|0|True|
|D085-01|starter|0|True|
|D086-01|extra|1|False|
|D086-02|extra|0|False|
|R001-01|rehearsal|0|False|
|R002-01|rehearsal|0|False|
|R003-01|rehearsal|0|False|
|R004-01|rehearsal|0|False|
|X001-01|extra|0|False|
|X002-01|extra|1|False|
|X002-02|extra|0|False|
|X002-03|extra|0|False|
|X003-01|extra|0|False|
|X004-01|extra|0|False|
|X005-01|extra|0|False|
|X006-01|extra|0|False|
|X006-02|extra|0|False|
|X007-01|extra|0|False|
|X008-01|extra|0|False|
|X101-01|extra|1|False|
|X102-01|extra|0|False|
