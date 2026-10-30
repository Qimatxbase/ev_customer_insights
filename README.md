# EV Customer Insights: Tesla and BYD

A customer-text analysis pipeline and synthetic-review NLP study of the Australian EV market.

**Technologies:** Python · pandas · NLTK · scikit-learn · Plotly

## Academic context and evidence

Developed for **UTS 24761 Data-Driven Insights, Assessments 1 and 2**, combining secondary-source market analysis with an illustrative customer-review analysis.

- The Tesla review study uses **500 synthetic reviews** to demonstrate cleaning, sentiment, themes and reporting methods.
- The survey component was proposed and **has not been conducted**.
- At the retained collection checkpoint, the Tesla/BYD pipeline recorded **zero raw and zero cleaned real-world observations**.

The synthetic review results demonstrate methods and do not establish actual buyer sentiment, representative market findings or survey outcomes.

## What is included

- Source collectors, a common review schema, relevance scoring and duplicate detection.
- Sentiment, value dimensions, n-grams, PMI, networks and topic analysis.
- A separate synthetic Tesla review notebook with summary figures.

## Insight poster

[Open the original assessment poster](docs/tesla_owner_experience_poster.pdf), designed for the Data-Driven Insights assessment. The original PDF is preserved with a descriptive filename; it combines historical secondary-source context, exploratory analysis of synthetic reviews and a proposed owner survey.

The synthetic CSV contains 500 rows and 306 unique normalised texts: 38.8% are repeated entries after the first occurrence. VADER classifies 66% of review text as positive, while 51% of ratings are 1–2 stars. These describe the supplied synthetic dataset and illustrate the need to compare sentiment, ratings and data quality. They do not establish real-owner satisfaction. Market-source statements retain their original assessment context.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m tesla_byd_customer_analysis.run_pipeline --skip-collection
```

Run the pipeline from this repository root. Open review_analysis/tesla_customer_review_nlp.ipynb with review_analysis/ as the notebook working directory. Its review dataset is synthetic: results demonstrate analytical methods and are not evidence of actual consumer sentiment. Collected review exports and interview records are excluded.

[Portfolio index](https://github.com/Qimatxbase/engineering_portfolio)
