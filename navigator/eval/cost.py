"""DeepSeek price list (USD per million tokens), from https://api-docs.deepseek.com/quick_start/pricing.

Peak hours cost double: Monday to Friday, 01:00-04:00 and 06:00-10:00 UTC (Chinese public holidays are ignored,
so a holiday run is priced slightly high).
"""
from __future__ import annotations

import datetime as dt
from typing import Any, Dict

PRICES = {
    "deepseek-flash": {"in_miss": 0.15, "in_hit": 0.003, "out": 0.6},
    "deepseek-v4-pro": {"in_miss": 0.66, "in_hit": 0.022, "out": 1.98},
}


def is_peak(ts: dt.datetime) -> bool:
    ts = ts.astimezone(dt.timezone.utc)
    return ts.weekday() < 5 and ts.hour in (1, 2, 3, 6, 7, 8, 9)


def cost_usd(model: str, usage: Dict[str, Any], ts: dt.datetime) -> float:
    key = next((k for k in PRICES if model and model.startswith(k)), None) or next(
        (k for k in PRICES if k.split("-")[-1] in (model or "")), None)
    if key is None:
        return 0.0
    p = PRICES[key]
    hit = usage.get("cache_read_input_tokens") or 0
    miss = usage.get("cache_miss_input_tokens")
    if miss is None:
        miss = max((usage.get("input_tokens") or 0) - hit, 0)
    usd = (miss * p["in_miss"] + hit * p["in_hit"] + (usage.get("output_tokens") or 0) * p["out"]) / 1e6
    return usd * (2.0 if is_peak(ts) else 1.0)
