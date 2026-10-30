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
