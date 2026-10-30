"""Pointwise mutual information for bigram associations."""

from __future__ import annotations

from collections import Counter
from math import log2

import pandas as pd

from .. import config
from ..utils import write_csv


def pmi_for_tokens(documents: list[list[str]], min_freq: int = 2) -> list[dict]:
    unigram = Counter()
    bigram = Counter()
    for tokens in documents:
        unigram.update(tokens)
        bigram.update(zip(tokens, tokens[1:]))
    total_unigrams = sum(unigram.values()) or 1
    total_bigrams = sum(bigram.values()) or 1
    rows = []
    for pair, freq in bigram.items():
        if freq < min_freq:
            continue
        p_xy = freq / total_bigrams
        p_x = unigram[pair[0]] / total_unigrams
        p_y = unigram[pair[1]] / total_unigrams
        rows.append({"bigram": " ".join(pair), "frequency": freq, "PMI": log2(p_xy / (p_x * p_y))})
    return rows


def pmi_brand_comparison(df: pd.DataFrame, min_freq: int = 2) -> pd.DataFrame:
    rows = []
    for group, subdf in df.groupby("comparison_type", dropna=False):
        docs = [str(text).split() for text in subdf["clean_text"].fillna("")]
        for row in pmi_for_tokens(docs, min_freq=min_freq):
            row["brand"] = group
            rows.append(row)
    out = pd.DataFrame(rows).sort_values(["brand", "PMI"], ascending=[True, False]) if rows else pd.DataFrame(columns=["bigram", "frequency", "PMI", "brand"])
    write_csv(out, config.TABLE_DIR / "pmi_brand_comparison.csv")
    return out

