"""LDA/NMF topic modelling helpers with graceful small-data handling."""

from __future__ import annotations

import pandas as pd

from .. import config
from ..utils import write_csv


def run_nmf_topics(df: pd.DataFrame, topic_counts: list[int] | None = None) -> pd.DataFrame:
    if topic_counts is None:
        topic_counts = [2, 3, 4, 5]
    docs = df["clean_text"].fillna("").loc[df["clean_text"].fillna("").str.split().map(len) >= 4]
    if len(docs) < 5:
        out = pd.DataFrame(columns=["method", "n_topics", "topic", "top_terms", "metric", "value"])
        write_csv(out, config.TABLE_DIR / "nmf_topics.csv")
        return out
    from sklearn.decomposition import NMF
    from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer(max_df=0.9, min_df=2, ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(docs)
    terms = vectorizer.get_feature_names_out()
    rows = []
    for n_topics in [n for n in topic_counts if n < len(docs)]:
        model = NMF(n_components=n_topics, random_state=config.RANDOM_SEED, init="nndsvda", max_iter=500)
        doc_topic = model.fit_transform(matrix)
        for topic_idx, topic in enumerate(model.components_):
            top_terms = "; ".join(terms[i] for i in topic.argsort()[-12:][::-1])
            rows.append({"method": "NMF", "n_topics": n_topics, "topic": topic_idx, "top_terms": top_terms, "metric": "reconstruction_error", "value": model.reconstruction_err_})
    out = pd.DataFrame(rows)
    write_csv(out, config.TABLE_DIR / "nmf_topics.csv")
    return out


def topic_brand_distribution(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(columns=["method", "topic", "brand", "n_records", "share"])
    write_csv(out, config.TABLE_DIR / "topic_brand_distribution.csv")
    return out

