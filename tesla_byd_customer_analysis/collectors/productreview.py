"""ProductReview.com.au public-page collector.

This collector only uses ordinary public GET requests and simple HTML parsing. If
the site blocks access or changes markup, it records the failure instead of
attempting to bypass protections.
"""

from __future__ import annotations

import logging

import pandas as pd

from .. import config
from ..utils import append_report_event, enforce_schema, now_utc, polite_get, stable_id, write_csv


def collect(events: list[dict], logger: logging.Logger) -> pd.DataFrame:
    rows: list[dict] = []
    try:
        from bs4 import BeautifulSoup
    except ModuleNotFoundError as exc:
        append_report_event(events, source="productreview", method="public HTML", query_or_url="configured ProductReview URLs", records_found=0, records_added=0, errors="beautifulsoup4 is not installed")
        logger.warning("ProductReview collector dependency missing: %s", exc)
        df = enforce_schema(pd.DataFrame(rows))
        write_csv(df, config.RAW_DIR / "productreview.csv")
        return df
    for url in config.PRODUCTREVIEW_URLS:
        try:
            before = len(rows)
            response = polite_get(url, logger)
            soup = BeautifulSoup(response.text, "html.parser")
            review_nodes = soup.select("[data-review-id], article, .review")
            for node in review_nodes[: config.MAX_RECORDS_PER_SOURCE or None]:
                text = " ".join(node.get_text(" ", strip=True).split())
                if not text or len(text) < 30:
                    continue
                title_node = node.find(["h1", "h2", "h3"])
                rating_text = node.get("aria-label", "")
                brand_hint = "Tesla" if "tesla" in url.lower() else "BYD" if "byd" in url.lower() else "Unknown"
                rows.append(
                    {
                        "record_id": stable_id("productreview", url, text[:200]),
                        "source": "productreview",
                        "content_type": "customer_review",
                        "brand": brand_hint,
                        "vehicle_model": None,
                        "comparison_type": None,
                        "location": None,
                        "state": None,
                        "rating": rating_text,
                        "title": title_node.get_text(" ", strip=True) if title_node else None,
                        "text": text,
                        "date": None,
                        "author_id": None,
                        "helpful_count": None,
                        "score": None,
                        "thread_id": None,
                        "url": response.url,
                        "collected_at": now_utc(),
                    }
                )
            error_note = "" if review_nodes else "Page reachable, but no parseable review nodes found in static HTML. Use approved export/API/manual capture if needed."
            append_report_event(events, source="productreview", method="public HTML", query_or_url=url, records_found=len(review_nodes), records_added=len(rows) - before, errors=error_note)
        except Exception as exc:
            append_report_event(events, source="productreview", method="public HTML", query_or_url=url, records_found=0, records_added=0, errors=str(exc))
            logger.warning("ProductReview collection failed for %s: %s", url, exc)
    df = enforce_schema(pd.DataFrame(rows))
    write_csv(df, config.RAW_DIR / "productreview.csv")
    return df
