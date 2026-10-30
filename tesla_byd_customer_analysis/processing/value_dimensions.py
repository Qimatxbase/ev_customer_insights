"""Rule-assisted value proposition dimension tagging."""

from __future__ import annotations

import re

import pandas as pd


DIMENSION_KEYWORDS = {
    "Price / affordability": ["price", "cheap", "cheaper", "expensive", "cost", "afford", "discount", "$", "aud"],
    "Value for money": ["value", "money", "worth", "bang for buck", "for the money"],
    "Technology / software": ["software", "app", "ota", "update", "screen", "autopilot", "adas", "tech"],
    "Driving experience / performance": ["drive", "driving", "performance", "acceleration", "handling", "power"],
    "Battery / range": ["battery", "range", "kwh", "efficiency", "efficient"],
    "Charging infrastructure": ["charging", "charger", "supercharger", "chargefox", "evie", "network"],
    "Vehicle quality": ["quality", "build", "paint", "panel", "rattle", "fault", "defect"],
    "Interior / comfort": ["interior", "seat", "comfort", "comfortable", "cabin", "space"],
    "Design": ["design", "looks", "style", "styling"],
    "Features / equipment": ["feature", "equipment", "standard", "included", "sunroof", "camera"],
    "Safety": ["safety", "ancap", "airbag", "assist"],
    "Reliability": ["reliable", "reliability", "breakdown", "issue", "problem"],
    "Service / after-sales": ["service", "support", "repair", "parts", "dealer", "after sales"],
    "Delivery experience": ["delivery", "handover", "wait", "delivered"],
    "Warranty": ["warranty"],
    "Running costs": ["running cost", "insurance", "maintenance", "servicing", "electricity"],
    "Brand / reputation": ["brand", "reputation", "elon", "image"],
    "Resale value": ["resale", "depreciation", "used price"],
    "Finance / ownership cost": ["finance", "loan", "lease", "novated", "ownership cost"],
}


def tag_dimensions(text: str) -> list[str]:
    lower = str(text).lower()
    matches = []
    for dimension, keywords in DIMENSION_KEYWORDS.items():
        for keyword in keywords:
            pattern = r"\b" + re.escape(keyword).replace(r"\ ", r"\s+") + r"\b"
            if keyword in {"$", "aud"}:
                found = keyword in lower
            else:
                found = bool(re.search(pattern, lower))
            if found:
                matches.append(dimension)
                break
    return matches


def add_value_dimensions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tags = df["text"].fillna("").map(tag_dimensions)
    df["value_dimensions"] = tags.map(lambda values: "; ".join(values))
    for dimension in DIMENSION_KEYWORDS:
        df[f"dim_{dimension.lower().replace(' / ', '_').replace(' ', '_').replace('-', '_')}"] = tags.map(lambda vals, d=dimension: d in vals)
    return df

