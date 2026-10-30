"""Word-frequency comparisons."""

from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd

from .. import config
from ..utils import write_csv


def top_words(df: pd.DataFrame, group_col: str = "comparison_type", n: int = 30, remove_analysis_stopwords: bool = True) -> pd.DataFrame:
    rows = []
    stop = set(config.ANALYSIS_STOPWORDS) if remove_analysis_stopwords else set()
    for group, subdf in df.groupby(group_col, dropna=False):
        counter: Counter[str] = Counter()
        for text in subdf.get("clean_text", pd.Series(dtype=str)).fillna(""):
            counter.update(token for token in str(text).split() if token not in stop)
        total = sum(counter.values()) or 1
        for word, count in counter.most_common(n):
            rows.append({"group": group, "word": word, "frequency": count, "share": count / total})
    out = pd.DataFrame(rows)
    write_csv(out, config.TABLE_DIR / "top_words_by_brand.csv")
    return out


def comparative_terms(df: pd.DataFrame, n: int = 30) -> pd.DataFrame:
    rows = []
    brand_tokens = {}
    stop = set(config.ANALYSIS_STOPWORDS)
    for brand in ["Tesla", "BYD"]:
        tokens = []
        for text in df.loc[df["brand"].isin([brand, "Tesla & BYD"]), "clean_text"].fillna(""):
            tokens.extend(t for t in str(text).split() if t not in stop)
        brand_tokens[brand] = Counter(tokens)
    vocab = set(brand_tokens["Tesla"]) | set(brand_tokens["BYD"])
    tesla_total = sum(brand_tokens["Tesla"].values()) or 1
    byd_total = sum(brand_tokens["BYD"].values()) or 1
    for word in vocab:
        t_share = (brand_tokens["Tesla"][word] + 0.5) / tesla_total
        b_share = (brand_tokens["BYD"][word] + 0.5) / byd_total
        rows.append({"word": word, "tesla_share": t_share, "byd_share": b_share, "tesla_byd_log_ratio": pd.NA if b_share == 0 else float(np.log(t_share / b_share))})
    out = pd.DataFrame(rows, columns=["word", "tesla_share", "byd_share", "tesla_byd_log_ratio"])
    if not out.empty:
        out = out.sort_values("tesla_byd_log_ratio", ascending=False).head(n)
    write_csv(out, config.TABLE_DIR / "comparative_terms.csv")
    return out
