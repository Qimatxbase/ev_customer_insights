# Tesla vs BYD Australia Customer Analysis Pipeline

This project collects and preprocesses customer-generated text for an academic marketing/NLP analysis of Tesla and BYD in the Australian EV market. It is designed to test, not assume, whether BYD is compressing Tesla Australia's customer value proposition.

## What Reuses The Existing Notebooks

- `sentiment_analysis.ipynb`: transparent token-based sentiment logic and rating/sentiment summaries.
- `interview_thematic_analysis.ipynb`: keyword-assisted theme coding and exportable summary tables.

The pipeline extends those ideas into source collection, harmonised review schema, Australian relevance scoring, duplicate detection, NLP cleaning, value-dimension tagging, aspect sentiment, n-grams, PMI, network graphs, and topic-ready tables.

## Setup

```bash
cd ev_customer_insights
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp tesla_byd_customer_analysis/.env.example .env
```

Add API credentials to `.env` only when authorised:

- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`
- `GOOGLE_MAPS_API_KEY`
- `YOUTUBE_API_KEY`

Credentials are never hard-coded.

## Run

From the repository root:

```bash
python -m tesla_byd_customer_analysis.run_pipeline
```

To process existing approved CSV exports without making web requests:

```bash
python -m tesla_byd_customer_analysis.run_pipeline --skip-collection
```

To test one collector:

```bash
python -m tesla_byd_customer_analysis.run_pipeline --sources reddit
```

## Input Schema

Each raw source should map to:

```text
record_id, source, content_type, brand, vehicle_model, comparison_type,
location, state, rating, title, text, date, author_id, helpful_count,
score, thread_id, url, collected_at
```

Social comments can be ingested from approved CSV exports placed in:

```text
data/raw/social_exports/
```

with at least a `text` or `comment` column.

## Outputs

- `data/raw/productreview.csv`
- `data/raw/google_reviews.csv`
- `data/raw/carsales.csv`
- `data/raw/reddit.csv`
- `data/raw/social.csv`
- `data/processed/tesla_byd_customer_raw.csv`
- `data/processed/tesla_byd_customer_clean.csv`
- `data/processed/tesla_byd_customer_low_relevance.csv`
- `data/processed/tesla_byd_comparisons.csv`
- `outputs/tables/source_summary.csv`
- `outputs/tables/brand_summary.csv`
- `outputs/tables/model_summary.csv`
- `outputs/tables/sentiment_by_brand.csv`
- `outputs/tables/sentiment_by_source.csv`
- `outputs/tables/value_dimension_comparison.csv`
- `outputs/tables/top_words_by_brand.csv`
- `outputs/tables/ngrams_by_brand.csv`
- `outputs/tables/pmi_brand_comparison.csv`
- `outputs/tables/topic_brand_distribution.csv`
- `outputs/tables/final_research_table.csv`
- `outputs/data_collection_report.md`

## Ethics

The collectors do not bypass authentication, CAPTCHA, Cloudflare, login walls, or private APIs. Google, Reddit, YouTube, Facebook, and Instagram should be collected through official APIs or approved exports. Sources that cannot be accessed are recorded in `outputs/data_collection_report.md`.

