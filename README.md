# Pharma Sales Analytics Dashboard

An end-to-end analytics project that turns synthetic pharmaceutical sales data into SQL-driven business insights and an interactive Streamlit dashboard.

## Overview

The project follows a simple analytics workflow:

**Data generation → relational storage → SQL analysis → dashboard → business insights**

It is designed to demonstrate practical skills in Python data processing, relational analytics, SQL, and BI-style application development.

## What it answers

- Which products generate the most revenue?
- How does revenue change year over year?
- Which regions contribute the most sales?
- Is there seasonal concentration in Q4?
- Which sales channels produce stronger margins?
- Which product-region segments are most valuable?
- Which products show stronger marketing ROI?
- How does a newly launched product ramp over time?

## Tech stack

| Layer | Technology |
|---|---|
| Data generation | Python, Pandas, NumPy |
| Storage | SQLite |
| Analysis | SQL, CTEs, aggregations, window functions |
| Dashboard | Streamlit, Plotly |

## Project structure

```text
.
├── 1_generate_dataset.py
├── 2_sql_analysis.py
├── 3_streamlit_dashboard.py
├── pharma_sales_data.csv
├── requirements.txt
└── README.md
```

## Dataset

The repository uses a synthetic dataset designed for analytics practice rather than real pharmaceutical data. It contains 1,200+ records spanning 2021–2024, multiple products and therapeutic areas, Indian regions/cities, sales channels, revenue, cost, margin, and marketing-spend fields.

## Run locally

```bash
git clone https://github.com/pallavi12-code/pharma-sales-dashboard.git
cd pharma-sales-dashboard
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python 1_generate_dataset.py
python 2_sql_analysis.py
streamlit run 3_streamlit_dashboard.py
```

## Engineering notes

- SQL is used for business analysis instead of doing every aggregation in Python.
- The dashboard is separated from data generation and analysis logic.
- The dataset is explicitly synthetic, so results should be interpreted as demonstration outputs rather than pharmaceutical market facts.

## Future improvements

- Add automated data-quality checks
- Add dashboard tests for key metrics
- Containerize the application
- Add scheduled data refresh
- Add role-based dashboard views

## Author

**Pallavi Reddy** — AI & Machine Learning Engineering Student, CBIT
