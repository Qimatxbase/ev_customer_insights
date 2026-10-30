"""Direct Tesla-vs-BYD comparison extraction."""

from __future__ import annotations

import re

import pandas as pd

from .value_dimensions import tag_dimensions


def preferred_brand(text: str) -> str:
    lower = str(text).lower()
    tesla_pos = bool(re.search(r"tesla|model\s*[3y]", lower) and re.search(r"better|prefer|stronger|love|superior", lower))
    byd_pos = bool(re.search(r"byd|atto|seal|sealion|dolphin", lower) and re.search(r"better|prefer|cheaper|value|more equipment|stronger|love", lower))
    if tesla_pos and byd_pos:
        return "Mixed / depends"
    if byd_pos:
        return "BYD"
    if tesla_pos:
        return "Tesla"
    if re.search(r"depends|both|trade.?off|mixed", lower):
        return "Mixed / depends"
    if re.search(r"no preference|either", lower):
        return "No preference"
    return "Unknown"


def add_comparison_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dimensions = df["text"].fillna("").map(tag_dimensions)
    df["preferred_brand"] = df["text"].fillna("").map(preferred_brand)
    df["comparison_dimension"] = dimensions.map(lambda vals: "; ".join(vals))
    df["comparison_reason"] = df["text"]
    df["tesla_dimension"] = dimensions.map(lambda vals: "; ".join(vals) if vals else "")
    df["byd_dimension"] = dimensions.map(lambda vals: "; ".join(vals) if vals else "")
    return df

