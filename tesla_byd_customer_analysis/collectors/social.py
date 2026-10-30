"""Public social comment ingestion.

Most social platforms restrict comment collection behind APIs, account access, or
terms. This module ingests approved exports placed in data/raw/social_exports/
instead of scraping login-gated pages.
"""

from __future__ import annotations

import logging

import pandas as pd

from .. import config
from ..utils import append_report_event, enforce_schema, now_utc, stable_id, write_csv


def collect(events: list[dict], logger: logging.Logger) -> pd.DataFrame:
    export_dir = config.RAW_DIR / "social_exports"
    rows: list[dict] = []
    if not export_dir.exists():
        append_report_event(
            events,
            source="social",
            method="approved API/export ingestion",
            query_or_url=str(export_dir),
            records_found=0,
            records_added=0,
            errors="No approved social export directory found. Use official APIs or manually approved exports.",
        )
        df = enforce_schema(pd.DataFrame(rows))
        write_csv(df, config.RAW_DIR / "social.csv")
        return df

    for path in export_dir.glob("*.csv"):
        try:
            before = len(rows)
            source_df = pd.read_csv(path)
            for _, row in source_df.iterrows():
                text = row.get("text") or row.get("comment") or row.get("body")
                if pd.isna(text) or not str(text).strip():
                    continue
                rows.append(
                    {
                        "record_id": stable_id("social", path.name, row.get("url"), text),
                        "source": row.get("source", "social"),
                        "content_type": "customer_comment",
                        "brand": row.get("brand"),
                        "vehicle_model": row.get("vehicle_model"),
                        "comparison_type": None,
                        "location": row.get("location"),
                        "state": row.get("state"),
                        "rating": row.get("rating"),
                        "title": row.get("title"),
                        "text": str(text),
                        "date": row.get("date"),
                        "author_id": row.get("author_id") or row.get("author"),
                        "helpful_count": None,
                        "score": row.get("score") or row.get("likes"),
                        "thread_id": row.get("thread_id") or row.get("post_id"),
                        "url": row.get("url"),
                        "collected_at": now_utc(),
                    }
                )
            append_report_event(events, source="social", method="approved CSV export", query_or_url=str(path), records_found=len(source_df), records_added=len(rows) - before, errors="")
        except Exception as exc:
            logger.warning("Social export failed for %s: %s", path, exc)
            append_report_event(events, source="social", method="approved CSV export", query_or_url=str(path), records_found=0, records_added=0, errors=str(exc))
    df = enforce_schema(pd.DataFrame(rows))
    write_csv(df, config.RAW_DIR / "social.csv")
    return df
