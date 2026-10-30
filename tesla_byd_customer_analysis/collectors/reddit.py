"""Reddit collector using PRAW when API credentials are configured."""

from __future__ import annotations

import logging

import pandas as pd

from .. import config
from ..utils import append_report_event, enforce_schema, now_utc, stable_id, write_csv


def collect(events: list[dict], logger: logging.Logger) -> pd.DataFrame:
    rows: list[dict] = []
    if not (config.REDDIT_CLIENT_ID and config.REDDIT_CLIENT_SECRET):
        append_report_event(
            events,
            source="reddit",
            method="Reddit API/PRAW",
            query_or_url="; ".join(config.REDDIT_QUERIES),
            records_found=0,
            records_added=0,
            errors="REDDIT_CLIENT_ID/REDDIT_CLIENT_SECRET not set. Use PRAW credentials or an approved export.",
        )
        df = enforce_schema(pd.DataFrame(rows))
        write_csv(df, config.RAW_DIR / "reddit.csv")
        return df

    import praw

    reddit = praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
    )
    subreddits = "CarsAustralia+AusEV+TeslaMotors+electricvehicles"
    for query in config.REDDIT_QUERIES:
        try:
            before = len(rows)
            submissions = list(reddit.subreddit(subreddits).search(query, limit=25, sort="new"))
            for submission in submissions:
                url = f"https://www.reddit.com{submission.permalink}"
                body = submission.selftext or ""
                if body:
                    rows.append(
                        {
                            "record_id": stable_id("reddit_post", submission.id),
                            "source": "reddit",
                            "content_type": "forum_post",
                            "brand": None,
                            "vehicle_model": None,
                            "comparison_type": None,
                            "location": None,
                            "state": None,
                            "rating": None,
                            "title": submission.title,
                            "text": body,
                            "date": pd.to_datetime(submission.created_utc, unit="s", utc=True).date().isoformat(),
                            "author_id": str(submission.author) if submission.author else None,
                            "helpful_count": None,
                            "score": submission.score,
                            "thread_id": submission.id,
                            "url": url,
                            "collected_at": now_utc(),
                        }
                    )
                submission.comments.replace_more(limit=0)
                for comment in submission.comments.list():
                    text = comment.body or ""
                    if len(text.strip()) < 10:
                        continue
                    rows.append(
                        {
                            "record_id": stable_id("reddit_comment", comment.id),
                            "source": "reddit",
                            "content_type": "forum_comment",
                            "brand": None,
                            "vehicle_model": None,
                            "comparison_type": None,
                            "location": None,
                            "state": None,
                            "rating": None,
                            "title": submission.title,
                            "text": text,
                            "date": pd.to_datetime(comment.created_utc, unit="s", utc=True).date().isoformat(),
                            "author_id": str(comment.author) if comment.author else None,
                            "helpful_count": None,
                            "score": comment.score,
                            "thread_id": submission.id,
                            "url": url,
                            "collected_at": now_utc(),
                        }
                    )
            append_report_event(events, source="reddit", method="Reddit API/PRAW", query_or_url=query, records_found=len(submissions), records_added=len(rows) - before, errors="")
        except Exception as exc:
            logger.warning("Reddit collection failed for %s: %s", query, exc)
            append_report_event(events, source="reddit", method="Reddit API/PRAW", query_or_url=query, records_found=0, records_added=0, errors=str(exc))
    df = enforce_schema(pd.DataFrame(rows))
    write_csv(df, config.RAW_DIR / "reddit.csv")
    return df
