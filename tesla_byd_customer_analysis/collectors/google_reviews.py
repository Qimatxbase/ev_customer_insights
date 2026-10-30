"""Google Reviews collector placeholder using compliant API-only access.

Google Maps Platform Place Details returns a limited review sample for a place.
Bulk review scraping is not attempted here because it may violate access rules.
"""

from __future__ import annotations

import logging

import pandas as pd

from .. import config
from ..utils import append_report_event, enforce_schema, now_utc, stable_id, write_csv


def collect(events: list[dict], logger: logging.Logger) -> pd.DataFrame:
    rows: list[dict] = []
    if not config.GOOGLE_MAPS_API_KEY:
        append_report_event(
            events,
            source="google_reviews",
            method="Google Places API",
            query_or_url="configured Australian Tesla/BYD locations",
            records_found=0,
            records_added=0,
            errors="GOOGLE_MAPS_API_KEY not set. Use Google Places API or an approved export/provider.",
        )
        df = enforce_schema(pd.DataFrame(rows))
        write_csv(df, config.RAW_DIR / "google_reviews.csv")
        return df

    import requests

    for place in config.GOOGLE_PLACES:
        try:
            find_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
            find_params = {
                "input": f"{place['location']} Australia",
                "inputtype": "textquery",
                "fields": "place_id,name,formatted_address",
                "key": config.GOOGLE_MAPS_API_KEY,
            }
            found = requests.get(find_url, params=find_params, timeout=20).json()
            candidates = found.get("candidates", [])
            if not candidates:
                append_report_event(events, source="google_reviews", method="Google Places API", query_or_url=place["location"], records_found=0, records_added=0, errors="No place candidate found")
                continue
            place_id = candidates[0]["place_id"]
            details = requests.get(
                "https://maps.googleapis.com/maps/api/place/details/json",
                params={"place_id": place_id, "fields": "name,rating,reviews,url", "key": config.GOOGLE_MAPS_API_KEY},
                timeout=20,
            ).json()
            reviews = details.get("result", {}).get("reviews", [])
            for review in reviews:
                text = review.get("text")
                if not text:
                    continue
                rows.append(
                    {
                        "record_id": stable_id("google_reviews", place_id, review.get("author_name"), text[:200]),
                        "source": "google_reviews",
                        "content_type": "customer_review",
                        "brand": place["brand"],
                        "vehicle_model": None,
                        "comparison_type": None,
                        "location": details.get("result", {}).get("name", place["location"]),
                        "state": place["state"],
                        "rating": review.get("rating"),
                        "title": None,
                        "text": text,
                        "date": review.get("relative_time_description"),
                        "author_id": review.get("author_name"),
                        "helpful_count": None,
                        "score": None,
                        "thread_id": place_id,
                        "url": details.get("result", {}).get("url"),
                        "collected_at": now_utc(),
                    }
                )
            append_report_event(events, source="google_reviews", method="Google Places API", query_or_url=place["location"], records_found=len(reviews), records_added=len(reviews), errors="")
        except Exception as exc:
            logger.warning("Google collection failed for %s: %s", place["location"], exc)
            append_report_event(events, source="google_reviews", method="Google Places API", query_or_url=place["location"], records_found=0, records_added=0, errors=str(exc))
    df = enforce_schema(pd.DataFrame(rows))
    write_csv(df, config.RAW_DIR / "google_reviews.csv")
    return df

