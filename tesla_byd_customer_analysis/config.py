"""Central configuration for the Tesla/BYD Australia customer analysis pipeline."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"
LOG_DIR = OUTPUT_DIR / "logs"
CACHE_DIR = PROJECT_ROOT / "cache"
os.environ.setdefault("MPLCONFIGDIR", str(CACHE_DIR / "matplotlib"))

BRANDS = ["Tesla", "BYD"]
TESLA_MODELS = ["Model 3", "Model Y"]
BYD_MODELS = ["Atto 3", "Seal", "Sealion 7", "Dolphin"]
COUNTRY = "Australia"

START_DATE = None
END_DATE = None
MAX_RECORDS_PER_SOURCE = None
REQUEST_DELAY = 2.0
REQUEST_DELAY_JITTER = 1.0
RANDOM_SEED = 42
USER_AGENT = "UTS academic research bot; contact: configure-in-config.py"

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", USER_AGENT)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

SCHEMA_COLUMNS = [
    "record_id",
    "source",
    "content_type",
    "brand",
    "vehicle_model",
    "comparison_type",
    "location",
    "state",
    "rating",
    "title",
    "text",
    "date",
    "author_id",
    "helpful_count",
    "score",
    "thread_id",
    "url",
    "collected_at",
]

ANALYSIS_STOPWORDS = [
    "tesla",
    "byd",
    "car",
    "cars",
    "vehicle",
    "vehicles",
    "ev",
    "evs",
    "electric",
    "australia",
    "australian",
]

IMPORTANT_AUTOMOTIVE_WORDS = {
    "price",
    "cheap",
    "expensive",
    "value",
    "quality",
    "range",
    "battery",
    "charging",
    "charger",
    "software",
    "technology",
    "service",
    "delivery",
    "reliability",
    "interior",
    "warranty",
    "insurance",
    "autopilot",
    "adas",
    "repair",
    "maintenance",
}

AUSTRALIAN_STATES = {
    "nsw": "NSW",
    "new south wales": "NSW",
    "vic": "VIC",
    "victoria": "VIC",
    "qld": "QLD",
    "queensland": "QLD",
    "wa": "WA",
    "western australia": "WA",
    "sa": "SA",
    "south australia": "SA",
    "tas": "TAS",
    "tasmania": "TAS",
    "act": "ACT",
    "nt": "NT",
    "northern territory": "NT",
}

AUSTRALIAN_CONTEXT_TERMS = {
    "australia",
    "australian",
    "aud",
    "$a",
    "rego",
    "stamp duty",
    "novated",
    "fbT",
    "sydney",
    "melbourne",
    "brisbane",
    "perth",
    "adelaide",
    "canberra",
    "hobart",
    "darwin",
    "gold coast",
    "wollongong",
    "newcastle",
}

REDDIT_QUERIES = [
    "Tesla vs BYD Australia",
    "Model Y vs Sealion 7",
    "Tesla Model 3 vs BYD Seal",
    "BYD or Tesla Australia",
    "Tesla Australia service",
    "BYD Australia service",
    "Tesla price Australia",
    "BYD value Australia",
    "Tesla quality Australia",
    "BYD quality Australia",
]

PRODUCTREVIEW_URLS = [
    "https://www.productreview.com.au/listings/tesla-model-3",
    "https://www.productreview.com.au/listings/byd-atto-3",
    "https://www.productreview.com.au/listings/byd-australia",
]

CARSales_URLS = [
    "https://www.carsales.com.au/owner-reviews/tesla/",
    "https://www.carsales.com.au/owner-reviews/byd/",
]

GOOGLE_PLACES = [
    {"brand": "Tesla", "location": "Tesla Sydney", "state": "NSW"},
    {"brand": "Tesla", "location": "Tesla Melbourne", "state": "VIC"},
    {"brand": "BYD", "location": "BYD Sydney", "state": "NSW"},
    {"brand": "BYD", "location": "BYD Melbourne", "state": "VIC"},
]


def ensure_directories() -> None:
    """Create all expected output directories."""
    for path in [RAW_DIR, INTERIM_DIR, PROCESSED_DIR, TABLE_DIR, FIGURE_DIR, LOG_DIR, CACHE_DIR]:
        path.mkdir(parents=True, exist_ok=True)
