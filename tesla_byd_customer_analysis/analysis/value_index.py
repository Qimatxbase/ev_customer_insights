"""Exploratory customer value proposition tables."""

from __future__ import annotations

import pandas as pd

from .. import config
from ..processing.value_dimensions import DIMENSION_KEYWORDS
from ..utils import write_csv


def value_dimension_comparison(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dimension in DIMENSION_KEYWORDS:
        sub = df[df["value_dimensions"].fillna("").str.contains(dimension, regex=False)]
        for brand in ["Tesla", "BYD"]:
            brand_sub = sub[sub["brand"].isin([brand, "Tesla & BYD"])]
            rows.append(
                {
                    "dimension": dimension,
                    "brand": brand,
                    "positive": int((brand_sub["sentiment"] == "Positive").sum()),
                    "negative": int((brand_sub["sentiment"] == "Negative").sum()),
                    "mixed": int((brand_sub["sentiment"] == "Mixed").sum()),
                    "neutral": int((brand_sub["sentiment"] == "Neutral").sum()),
                    "net_sentiment": float(brand_sub["sentiment_score"].mean()) if len(brand_sub) else 0.0,
                    "sample_size": len(brand_sub),
                    "label": "Sentiment within the collected online customer-discussion sample.",
                }
            )
    out = pd.DataFrame(rows)
    write_csv(out, config.TABLE_DIR / "value_dimension_comparison.csv")
    return out


def final_research_table(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "Price": "Price / affordability",
        "Value for money": "Value for money",
        "Technology/software": "Technology / software",
        "Performance": "Driving experience / performance",
        "Range/efficiency": "Battery / range",
        "Charging": "Charging infrastructure",
        "Features": "Features / equipment",
        "Interior/comfort": "Interior / comfort",
        "Build quality": "Vehicle quality",
        "Reliability": "Reliability",
        "Service/after-sales": "Service / after-sales",
        "Warranty": "Warranty",
        "Running cost": "Running costs",
        "Brand/reputation": "Brand / reputation",
        "Overall ownership experience": "",
    }
    rows = []
    for label, dimension in mapping.items():
        sub = df if not dimension else df[df["value_dimensions"].fillna("").str.contains(dimension, regex=False)]
        tesla = sub[sub["brand"].isin(["Tesla", "Tesla & BYD"])]
        byd = sub[sub["brand"].isin(["BYD", "Tesla & BYD"])]
        t_score = tesla["sentiment_score"].mean() if len(tesla) else 0
        b_score = byd["sentiment_score"].mean() if len(byd) else 0
        evidence_strength = "Insufficient evidence" if len(sub) < 5 else "Moderate" if len(sub) < 30 else "Stronger"
        rows.append(
            {
                "dimension": label,
                "Tesla_customer_perception": "; ".join(tesla["text"].dropna().head(2).astype(str)),
                "BYD_customer_perception": "; ".join(byd["text"].dropna().head(2).astype(str)),
                "Tesla_advantage": bool(t_score > b_score and len(tesla) > 0 and len(byd) > 0),
                "BYD_advantage": bool(b_score > t_score and len(tesla) > 0 and len(byd) > 0),
                "evidence_strength": evidence_strength,
                "n_tesla": len(tesla),
                "n_byd": len(byd),
                "n_direct_comparisons": int((sub["comparison_type"] == "Direct comparison").sum()),
                "interpretation": "Derived from collected sample; review source balance and quotes before drawing a marketing conclusion.",
            }
        )
    out = pd.DataFrame(rows)
    write_csv(out, config.TABLE_DIR / "final_research_table.csv")
    return out

