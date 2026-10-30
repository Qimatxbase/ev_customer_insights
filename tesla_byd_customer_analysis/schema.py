"""Dataset schema helpers."""

from __future__ import annotations

from .config import SCHEMA_COLUMNS

COMPARISON_COLUMNS = SCHEMA_COLUMNS + [
    "australia_relevance",
    "is_duplicate",
    "duplicate_group",
    "text_quality",
    "clean_text",
    "tokens",
    "word_count",
    "value_dimensions",
    "sentiment",
    "sentiment_score",
    "aspect_sentiment",
    "tesla_dimension",
    "byd_dimension",
    "preferred_brand",
    "comparison_dimension",
    "comparison_reason",
]

