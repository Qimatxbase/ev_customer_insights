"""Schema harmonisation, brand/model detection, comparison labels, and Australia relevance."""

from __future__ import annotations

import re

import pandas as pd

from .. import config
from ..utils import enforce_schema


MODEL_PATTERNS = {
    "Tesla Model Y": [r"\bmodel\s*y\b", r"\btesla\s+y\b"],
    "Tesla Model 3": [r"\bmodel\s*3\b", r"\btesla\s*3\b"],
    "BYD Sealion 7": [r"\bsealion\s*7\b", r"\bsea\s*lion\s*7\b"],
    "BYD Atto 3": [r"\batto\s*3\b"],
    "BYD Dolphin": [r"\bdolphin\b"],
    "BYD Seal": [r"\bbyd\s+seal\b", r"\bseal\b"],
}


def _contains(patterns: list[str], text: str) -> bool:
    return any(re.search(pattern, text, flags=re.I) for pattern in patterns)


def detect_vehicle_model(text: str) -> str:
    lower = str(text)
    for model, patterns in MODEL_PATTERNS.items():
        if _contains(patterns, lower):
            return model
    return "Unknown"


def detect_brand(text: str, existing: str | None = None) -> str:
    text_l = str(text).lower()
    has_tesla = bool(re.search(r"\btesla\b|\bmodel\s*[3y]\b", text_l))
    has_byd = bool(re.search(r"\bbyd\b|\batto\s*3\b|\bseal(?:ion\s*7)?\b|\bdolphin\b", text_l))
    if has_tesla and has_byd:
        return "Tesla & BYD"
    if has_tesla:
        return "Tesla"
    if has_byd:
        return "BYD"
    if existing in {"Tesla", "BYD", "Tesla & BYD"}:
        return existing
    return "Unknown"


def detect_comparison_type(text: str, brand: str) -> str:
    text_l = str(text).lower()
    direct_terms = [" vs ", " versus ", " compared", "compare", "better than", "cheaper than", "instead of", "rather than"]
    if brand == "Tesla & BYD" and any(term in f" {text_l} " for term in direct_terms):
        return "Direct comparison"
    if brand == "Tesla & BYD":
        return "Direct comparison"
    if brand == "Tesla":
        return "Tesla only"
    if brand == "BYD":
        return "BYD only"
    return "Other"


def detect_state(row: pd.Series) -> str | None:
    if pd.notna(row.get("state")) and str(row.get("state")).strip():
        return str(row.get("state")).strip().upper()
    text = " ".join(str(row.get(col, "")) for col in ["location", "title", "text"])
    lower = text.lower()
    for term, state in config.AUSTRALIAN_STATES.items():
        if re.search(r"\b" + re.escape(term) + r"\b", lower):
            return state
    return None


def australia_relevance(row: pd.Series) -> str:
    text = " ".join(str(row.get(col, "")) for col in ["source", "location", "state", "title", "text", "url"]).lower()
    if any(term in text for term in config.AUSTRALIAN_CONTEXT_TERMS) or detect_state(row):
        return "High"
    if row.get("source") in {"productreview", "carsales"}:
        return "Medium"
    if row.get("source") == "reddit" and any(sub in text for sub in ["australia", "carsaus", "ausev"]):
        return "Medium"
    return "Low"


def normalise_records(df: pd.DataFrame) -> pd.DataFrame:
    df = enforce_schema(df.copy())
    combined_text = (df["title"].fillna("") + " " + df["text"].fillna("")).str.strip()
    df["brand"] = [detect_brand(text, existing if pd.notna(existing) else None) for text, existing in zip(combined_text, df["brand"])]
    df["vehicle_model"] = [
        existing if pd.notna(existing) and str(existing).strip() and str(existing) != "None" else detect_vehicle_model(text)
        for text, existing in zip(combined_text, df["vehicle_model"])
    ]
    df["comparison_type"] = [detect_comparison_type(text, brand) for text, brand in zip(combined_text, df["brand"])]
    df["state"] = df.apply(detect_state, axis=1)
    df["australia_relevance"] = df.apply(australia_relevance, axis=1)
    dates = pd.to_datetime(df["date"], errors="coerce", utc=True)
    df["year"] = dates.dt.year
    df["month"] = dates.dt.month
    return df

