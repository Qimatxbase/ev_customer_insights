"""Dataset summaries and sample-bias tables."""

from __future__ import annotations

import pandas as pd

from .. import config
from ..utils import write_csv


def safe_summary(df: pd.DataFrame, group_cols: list[str], name: str) -> pd.DataFrame:
    if df.empty:
        out = pd.DataFrame(columns=group_cols + ["n_records"])
    else:
        out = df.groupby(group_cols, dropna=False).size().reset_index(name="n_records")
    write_csv(out, config.TABLE_DIR / name)
    return out


def run_basic_eda(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    outputs = {
        "source_summary": safe_summary(df, ["source"], "source_summary.csv"),
        "brand_summary": safe_summary(df, ["brand"], "brand_summary.csv"),
        "model_summary": safe_summary(df, ["vehicle_model"], "model_summary.csv"),
    }
    if df.empty:
        sentiment_brand = pd.DataFrame(columns=["brand", "sentiment", "n_records", "avg_sentiment"])
        sentiment_source = pd.DataFrame(columns=["source", "brand", "sentiment", "n_records", "avg_sentiment"])
        bias = pd.DataFrame(columns=["source", "brand", "n_records", "percentage_of_dataset", "date_min", "date_max"])
    else:
        sentiment_brand = df.groupby(["brand", "sentiment"], dropna=False).agg(n_records=("record_id", "count"), avg_sentiment=("sentiment_score", "mean")).reset_index()
        sentiment_source = df.groupby(["source", "brand", "sentiment"], dropna=False).agg(n_records=("record_id", "count"), avg_sentiment=("sentiment_score", "mean")).reset_index()
        dated = df.copy()
        dated["date_parsed"] = pd.to_datetime(dated["date"], errors="coerce")
        bias = dated.groupby(["source", "brand"], dropna=False).agg(
            n_records=("record_id", "count"),
            date_min=("date_parsed", "min"),
            date_max=("date_parsed", "max"),
        ).reset_index()
        bias["percentage_of_dataset"] = bias["n_records"] / max(len(df), 1) * 100
    write_csv(sentiment_brand, config.TABLE_DIR / "sentiment_by_brand.csv")
    write_csv(sentiment_source, config.TABLE_DIR / "sentiment_by_source.csv")
    write_csv(bias, config.TABLE_DIR / "sample_bias_table.csv")
    outputs.update({"sentiment_by_brand": sentiment_brand, "sentiment_by_source": sentiment_source, "sample_bias_table": bias})
    return outputs

