"""Shared utilities for collection, logging, caching, and schema handling."""

from __future__ import annotations

import hashlib
import json
import logging
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from . import config


def setup_logging() -> logging.Logger:
    """Configure file and console logging."""
    config.ensure_directories()
    logger = logging.getLogger("tesla_byd_pipeline")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(config.LOG_DIR / "pipeline.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_id(*parts: Any) -> str:
    joined = "||".join("" if part is None else str(part) for part in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def empty_schema_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=config.SCHEMA_COLUMNS)


def enforce_schema(df: pd.DataFrame) -> pd.DataFrame:
    for col in config.SCHEMA_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[config.SCHEMA_COLUMNS].copy()


def polite_get(url: str, logger: logging.Logger, *, params: dict[str, Any] | None = None) -> requests.Response:
    """GET with a clear User-Agent, retries, backoff, and local response caching."""
    cache_key = stable_id(url, json.dumps(params or {}, sort_keys=True))
    cache_path = config.CACHE_DIR / f"{cache_key}.html"
    if cache_path.exists():
        response = requests.Response()
        response.status_code = 200
        response._content = cache_path.read_bytes()
        response.url = url
        return response

    headers = {"User-Agent": config.USER_AGENT}
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            if response.status_code == 200:
                cache_path.write_bytes(response.content)
                delay = config.REQUEST_DELAY + random.random() * config.REQUEST_DELAY_JITTER
                time.sleep(delay)
                return response
            logger.warning("GET %s returned %s", url, response.status_code)
        except requests.RequestException as exc:
            logger.warning("GET %s failed on attempt %s: %s", url, attempt + 1, exc)
        time.sleep(2**attempt)
    raise RuntimeError(f"Failed to fetch {url}")


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def append_report_event(events: list[dict[str, Any]], **kwargs: Any) -> None:
    event = {"timestamp": now_utc()}
    event.update(kwargs)
    events.append(event)

