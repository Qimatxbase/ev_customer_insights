"""Transparent overall and aspect sentiment scoring."""

from __future__ import annotations

import re

import pandas as pd

from .value_dimensions import DIMENSION_KEYWORDS

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ModuleNotFoundError:  # pragma: no cover
    SentimentIntensityAnalyzer = None


POSITIVE_WORDS = {
    "amazing", "excellent", "good", "great", "happy", "love", "premium", "quick", "reliable", "solid",
    "value", "comfortable", "impressed", "easy", "better", "best", "strong", "smooth", "efficient",
}
NEGATIVE_WORDS = {
    "awful", "bad", "cheap", "confusing", "damaged", "disappointing", "expensive", "frustrating",
    "overpriced", "problem", "rude", "slow", "terrible", "unhelpful", "weak", "worse", "fault",
}
NEGATION_WORDS = {"not", "never", "no", "without"}


def rule_score(text: str) -> float:
    tokens = re.findall(r"[a-z]+", str(text).lower())
    score = 0
    for idx, token in enumerate(tokens):
        negated = any(t in NEGATION_WORDS for t in tokens[max(0, idx - 3):idx])
        if token in POSITIVE_WORDS:
            score += -1 if negated else 1
        elif token in NEGATIVE_WORDS:
            score += 1 if negated else -1
    return score / max(len(tokens), 1)


def classify(score: float, text: str) -> str:
    has_positive = any(word in str(text).lower() for word in POSITIVE_WORDS)
    has_negative = any(word in str(text).lower() for word in NEGATIVE_WORDS)
    if has_positive and has_negative:
        return "Mixed"
    if score >= 0.05:
        return "Positive"
    if score <= -0.05:
        return "Negative"
    return "Neutral"


def score_text(text: str) -> tuple[str, float]:
    if SentimentIntensityAnalyzer is not None:
        analyzer = SentimentIntensityAnalyzer()
        score = analyzer.polarity_scores(str(text))["compound"]
    else:
        score = rule_score(text)
    return classify(score, text), float(score)


def aspect_sentiment(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", str(text))
    pieces = []
    for dimension, keywords in DIMENSION_KEYWORDS.items():
        relevant = [s for s in sentences if any(k.lower() in s.lower() for k in keywords)]
        if not relevant:
            continue
        label, score = score_text(" ".join(relevant))
        if label != "Neutral":
            pieces.append(f"{dimension}={label}:{score:.3f}")
    return "; ".join(pieces)


def add_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    scored = df["text"].fillna("").map(score_text)
    df["sentiment"] = scored.map(lambda item: item[0])
    df["sentiment_score"] = scored.map(lambda item: item[1])
    df["aspect_sentiment"] = df["text"].fillna("").map(aspect_sentiment)
    return df

