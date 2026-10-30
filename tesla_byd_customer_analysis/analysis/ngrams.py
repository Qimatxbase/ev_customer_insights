"""N-gram frequency analysis."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from ..utils import write_csv
from .. import config


def make_ngrams(tokens: list[str], n: int) -> list[str]:
    return [" ".join(tokens[i : i + n]) for i in range(max(0, len(tokens) - n + 1))]


def ngrams_by_brand(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    rows = []
    for group, subdf in df.groupby("comparison_type", dropna=False):
        for n in [2, 3]:
            counter: Counter[str] = Counter()
            for text in subdf["clean_text"].fillna(""):
                counter.update(make_ngrams(str(text).split(), n))
            for phrase, count in counter.most_common(top_n):
                rows.append({"group": group, "ngram_type": f"{n}-gram", "ngram": phrase, "frequency": count})
    out = pd.DataFrame(rows)
    write_csv(out, config.TABLE_DIR / "ngrams_by_brand.csv")
    return out

