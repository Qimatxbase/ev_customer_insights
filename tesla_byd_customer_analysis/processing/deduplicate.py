"""Duplicate and near-duplicate detection."""

from __future__ import annotations

import re

import pandas as pd

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ModuleNotFoundError:  # pragma: no cover
    TfidfVectorizer = None
    cosine_similarity = None

from ..utils import stable_id


def normalised_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def flag_duplicates(df: pd.DataFrame, threshold: float = 0.92) -> pd.DataFrame:
    df = df.copy()
    df["is_duplicate"] = False
    df["duplicate_group"] = None
    seen_url: dict[str, str] = {}
    seen_text: dict[str, str] = {}
    norm_texts = df["text"].fillna("").map(normalised_text)

    for idx, row in df.iterrows():
        url = str(row.get("url") or "").strip()
        text = norm_texts.loc[idx]
        group = None
        if url and url in seen_url:
            group = seen_url[url]
        elif text and text in seen_text:
            group = seen_text[text]
        else:
            group = stable_id("dup", url, text[:300])
            if url:
                seen_url[url] = group
            if text:
                seen_text[text] = group
        df.at[idx, "duplicate_group"] = group
        df.at[idx, "is_duplicate"] = list(df.loc[:idx, "duplicate_group"]).count(group) > 1

    if TfidfVectorizer is None or cosine_similarity is None:
        return df

    candidates = df[~df["is_duplicate"] & (norm_texts.str.len() > 50)].copy()
    if len(candidates) > 1:
        vectorizer = TfidfVectorizer(min_df=1, ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(norm_texts.loc[candidates.index])
        sim = cosine_similarity(matrix)
        indices = list(candidates.index)
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                if sim[i, j] >= threshold:
                    df.at[indices[j], "is_duplicate"] = True
                    df.at[indices[j], "duplicate_group"] = df.at[indices[i], "duplicate_group"]
    return df
