"""Command-line entry point for the Tesla/BYD Australia customer NLP pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

if __package__ is None or __package__ == "":
    import sys

    sys.path.append(str(Path(__file__).resolve().parent.parent))

from tesla_byd_customer_analysis import config
from tesla_byd_customer_analysis.analysis.basic_eda import run_basic_eda
from tesla_byd_customer_analysis.analysis.ngrams import ngrams_by_brand
from tesla_byd_customer_analysis.analysis.networks import save_bigram_networks
from tesla_byd_customer_analysis.analysis.pmi import pmi_brand_comparison
from tesla_byd_customer_analysis.analysis.topics import run_nmf_topics, topic_brand_distribution
from tesla_byd_customer_analysis.analysis.value_index import final_research_table, value_dimension_comparison
from tesla_byd_customer_analysis.analysis.word_frequency import comparative_terms, top_words
from tesla_byd_customer_analysis.collectors import carsales, google_reviews, productreview, reddit, social
from tesla_byd_customer_analysis.processing.comparisons import add_comparison_fields
from tesla_byd_customer_analysis.processing.deduplicate import flag_duplicates
from tesla_byd_customer_analysis.processing.normalise import normalise_records
from tesla_byd_customer_analysis.processing.preprocess import preprocess_text
from tesla_byd_customer_analysis.processing.sentiment import add_sentiment
from tesla_byd_customer_analysis.processing.value_dimensions import add_value_dimensions
from tesla_byd_customer_analysis.utils import empty_schema_frame, enforce_schema, setup_logging, write_csv


COLLECTORS = {
    "productreview": productreview.collect,
    "google_reviews": google_reviews.collect,
    "carsales": carsales.collect,
    "reddit": reddit.collect,
    "social": social.collect,
}


def collect_sources(selected_sources: list[str] | None = None) -> tuple[pd.DataFrame, list[dict]]:
    logger = setup_logging()
    events: list[dict] = []
    frames = []
    sources = selected_sources or list(COLLECTORS)
    for source in sources:
        logger.info("Collecting %s", source)
        try:
            frames.append(COLLECTORS[source](events, logger))
        except Exception as exc:
            logger.exception("Collector %s failed", source)
            events.append({"source": source, "method": "collector", "query_or_url": "", "records_found": 0, "records_added": 0, "errors": str(exc)})
    raw = pd.concat(frames, ignore_index=True) if frames else empty_schema_frame()
    raw = enforce_schema(raw)
    write_csv(raw, config.PROCESSED_DIR / "tesla_byd_customer_raw.csv")
    return raw, events


def process_records(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    normalised = normalise_records(raw)
    deduped = flag_duplicates(normalised)
    enriched = preprocess_text(deduped)
    enriched = add_value_dimensions(enriched)
    enriched = add_sentiment(enriched)
    enriched = add_comparison_fields(enriched)

    write_csv(enriched, config.INTERIM_DIR / "tesla_byd_customer_all_observations.csv")
    low = enriched[enriched["australia_relevance"] == "Low"].copy()
    write_csv(low, config.PROCESSED_DIR / "tesla_byd_customer_low_relevance.csv")

    clean = enriched[
        enriched["australia_relevance"].isin(["High", "Medium"])
        & ~enriched["is_duplicate"]
        & (enriched["text_quality"] == "usable")
        & (enriched["content_type"] != "professional_review")
    ].copy()
    write_csv(clean, config.PROCESSED_DIR / "tesla_byd_customer_clean.csv")

    comparisons = clean[clean["comparison_type"] == "Direct comparison"].copy()
    write_csv(comparisons, config.PROCESSED_DIR / "tesla_byd_comparisons.csv")
    return enriched, clean, comparisons


def run_analysis(clean: pd.DataFrame) -> None:
    run_basic_eda(clean)
    top_words(clean)
    comparative_terms(clean)
    ngrams_by_brand(clean)
    pmi_brand_comparison(clean, min_freq=2)
    save_bigram_networks(clean)
    value_dimension_comparison(clean)
    final_research_table(clean)
    run_nmf_topics(clean)
    topic_brand_distribution(clean)


def write_collection_report(events: list[dict], raw: pd.DataFrame, clean: pd.DataFrame) -> None:
    events_df = pd.DataFrame(events)
    report_path = config.OUTPUT_DIR / "data_collection_report.md"
    lines = [
        "# Tesla/BYD Australia Customer Data Collection Report",
        "",
        "This report documents publicly accessible and API/export-based collection attempts for an academic NLP dataset. The pipeline does not bypass CAPTCHA, login walls, Cloudflare, authentication, or private APIs.",
        "",
        "## Existing Notebook Reuse",
        "",
        "- `sentiment_analysis.ipynb` provides a transparent rule-based token sentiment approach and rating/sentiment summary workflow.",
        "- `interview_thematic_analysis.ipynb` provides reusable keyword-assisted theme coding and CSV/table output patterns.",
        "- This project extends those ideas for customer-review data with source collection, harmonised schema, Australian relevance scoring, deduplication, EV value dimensions, aspect sentiment, n-grams, PMI, networks, and topic-ready outputs.",
        "",
        "## Collection Summary",
        "",
        f"- Raw observations saved: {len(raw)}",
        f"- Clean analysis observations saved: {len(clean)}",
        f"- Collection date: {pd.Timestamp.utcnow().isoformat()}",
        "",
    ]
    if events_df.empty:
        lines.append("No collection events were recorded.")
    else:
        columns = list(events_df.columns)
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        for _, row in events_df.iterrows():
            values = [str(row.get(col, "")).replace("\n", " ").replace("|", "\\|") for col in columns]
            lines.append("| " + " | ".join(values) + " |")
    lines.extend(
        [
            "",
            "## Source Restrictions And Compliant Alternatives",
            "",
            "- Google Reviews: use Google Places API or an approved third-party/export workflow; bulk scraping is not attempted.",
            "- Reddit: use Reddit API/PRAW credentials; HTML scraping is avoided.",
            "- Social platforms: ingest official API outputs or approved public comment exports only.",
            "- ProductReview/Carsales: public HTML is attempted only with ordinary GET requests and respectful delays; failures are reported rather than bypassed.",
            "",
            "## Bias And Limitations",
            "",
            "- Online reviews and forum comments are self-selected and are not representative of all Australian EV buyers.",
            "- Platform populations differ, and ratings are not directly comparable across sources.",
            "- Reddit and social commenters may not be verified vehicle owners.",
            "- Tesla and BYD have different market ages and review volumes, so use percentages and within-brand shares alongside raw counts.",
            "- The final evidence table is labelled as sentiment within the collected online customer-discussion sample, not a population estimate.",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    load_dotenv(config.PROJECT_ROOT / ".env")
    config.ensure_directories()
    parser = argparse.ArgumentParser(description="Collect and process Tesla/BYD Australia customer text.")
    parser.add_argument("--skip-collection", action="store_true", help="Use existing data/raw/*.csv files.")
    parser.add_argument("--sources", nargs="*", choices=list(COLLECTORS), help="Limit collection to selected sources.")
    args = parser.parse_args()

    if args.skip_collection:
        frames = []
        for path in [config.RAW_DIR / f"{source}.csv" for source in COLLECTORS]:
            if path.exists():
                frames.append(pd.read_csv(path))
        raw = enforce_schema(pd.concat(frames, ignore_index=True) if frames else empty_schema_frame())
        events: list[dict] = []
        write_csv(raw, config.PROCESSED_DIR / "tesla_byd_customer_raw.csv")
    else:
        raw, events = collect_sources(args.sources)

    all_observations, clean, comparisons = process_records(raw)
    run_analysis(clean)
    write_collection_report(events, raw, clean)

    preview_cols = ["source", "brand", "vehicle_model", "comparison_type", "australia_relevance", "sentiment", "text"]
    print("\nCollected raw shape:", raw.shape)
    print("Clean analysis shape:", clean.shape)
    print("Direct comparisons shape:", comparisons.shape)
    print("\nClean dataframe preview:")
    print(clean[preview_cols].head(10).to_string(index=False) if not clean.empty else "No clean records available.")
    print(f"\nOutputs written under {config.PROJECT_ROOT}")


if __name__ == "__main__":
    main()
