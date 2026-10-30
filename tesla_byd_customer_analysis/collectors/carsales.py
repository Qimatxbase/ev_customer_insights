"""Carsales and Australian automotive public-page collector."""

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
        append_report_event(events, source="carsales", method="public HTML", query_or_url="configured Carsales URLs", records_found=0, records_added=0, errors="beautifulsoup4 is not installed")
        logger.warning("Carsales collector dependency missing: %s", exc)
        df = enforce_schema(pd.DataFrame(rows))
        write_csv(df, config.RAW_DIR / "carsales.csv")
        return df
    for url in config.CARSales_URLS:
        try:
            before = len(rows)
            response = polite_get(url, logger)
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.select("article, .article, .listing-item")
            for article in articles[: config.MAX_RECORDS_PER_SOURCE or None]:
                text = " ".join(article.get_text(" ", strip=True).split())
                if len(text) < 40:
                    continue
                lower = text.lower()
                rows.append(
                    {
                        "record_id": stable_id("carsales", response.url, text[:200]),
                        "source": "carsales",
                        "content_type": "customer_review" if "owner review" in lower else "professional_review",
                        "brand": "Tesla" if "tesla" in lower else "BYD" if "byd" in lower else "Unknown",
                        "vehicle_model": None,
                        "comparison_type": None,
                        "location": None,
                        "state": None,
                        "rating": None,
                        "title": None,
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
            error_note = "" if articles else "Page reachable, but no parseable owner-review nodes found in static HTML. Use approved export/API/manual capture if needed."
            append_report_event(events, source="carsales", method="public HTML", query_or_url=url, records_found=len(articles), records_added=len(rows) - before, errors=error_note)
        except Exception as exc:
            logger.warning("Carsales collection failed for %s: %s", url, exc)
            append_report_event(events, source="carsales", method="public HTML", query_or_url=url, records_found=0, records_added=0, errors=str(exc))
    df = enforce_schema(pd.DataFrame(rows))
    write_csv(df, config.RAW_DIR / "carsales.csv")
    return df
