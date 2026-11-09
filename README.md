# Tesla Market Research & Customer Insights

An integrated **UTS 24761 Data-Driven Insights project** connecting secondary market research, AI-assisted analysis of existing customer reviews and primary research design. Findings and recommendations are communicated through an insight poster.

**Keywords:** Market research · Customer insights · AI-assisted analysis · Data validation · NLP · Sentiment analysis · Thematic analysis · Research design · Analytical reporting

**Tools:** Python · Jupyter · pandas · VADER · NLTK · scikit-learn · Plotly

## Research workflow

| Stage | Focus | Deliverable |
| --- | --- | --- |
| Secondary research | Australian passenger-EV market context, Tesla/BYD comparison and the ownership value proposition | Research problem and analytical questions |
| AI-assisted review analysis | AI-supported exploration of existing review text and customer-experience themes | Initial findings and themes |
| Cross-checking and validation | VADER sentiment, thematic coding, star-rating comparisons and data-quality checks | Cross-checked findings and documented limitations |
| Synthesis — Research design and communication | Proposed owner survey comparing attribute importance and satisfaction | Likert-scale research proposal, managerial implications and poster |

[Open the insight poster](docs/tesla_owner_experience_poster.pdf).

**Methods note:** AI supported the analysis of existing reviews. VADER sentiment and thematic coding were used to cross-check and validate the findings, alongside rating comparisons and missing-value and repeated-text checks. The owner survey is a proposed research design. The original poster retains its historical secondary-source context.

## Code and supporting material

- `review_analysis/`: Tesla review analysis notebook and its input data.
- `tesla_byd_customer_analysis/`: supporting collection/schema, relevance scoring, deduplication and reporting pipeline. Its retained collection checkpoint is documented in `outputs/data_collection_report.md`.
- `docs/tesla_owner_experience_poster.pdf`: research poster with the student ID removed for portfolio sharing. The original assessment copy remains in the local subject archive.

## Setup and run

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m tesla_byd_customer_analysis.run_pipeline --skip-collection
```

Run the pipeline from the repository root. Open `review_analysis/tesla_customer_review_nlp.ipynb` with `review_analysis/` as the notebook working directory. Raw owner-survey responses, interview records and private collection exports are not included.
