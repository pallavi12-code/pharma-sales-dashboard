# Synthetic Pharma Sales Analytics

An end-to-end analytics project that generates **simulated pharmaceutical sales data**, stores it in SQLite, answers business questions with SQL, and presents the results in Streamlit. The dataset is synthetic and does not represent real pharmaceutical market data, companies, products, or business impact.

## Architecture

```text
analytics.py
  ├── deterministic data generator
  ├── CSV + SQLite persistence
  └── read-only SQL helper
        ↓
1_generate_dataset.py → data/pharma_sales_data.csv
                       → data/pharma_sales.db
        ↓
2_sql_analysis.py     → eight analytical SQL result sets
        ↓
3_streamlit_dashboard.py → interactive filtered charts and KPIs
```

The dashboard generates its own in-memory copy by default, so it can run on Streamlit hosting without a checked-in database. The command-line workflow writes generated artifacts under `data/`; those files are ignored by Git.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Reproducible data generation

The default seed is `42`. Use `--seed` to create a different, repeatable simulation:

```bash
python 1_generate_dataset.py --seed 42
python 1_generate_dataset.py --seed 123 --csv /tmp/sales.csv --db /tmp/sales.db
```

The generator produces 640 rows across 2021–2024, with configured products, regions, channels, prices, costs, marketing spend, and synthetic seasonality. It also creates a `dim_drugs` lookup table.

## SQL analysis

Generate the database first, then run:

```bash
python 2_sql_analysis.py
```

The analysis demonstrates aggregations, `NULLIF`-guarded ratios, CTEs, `LAG()` window functions, regional share, channel mix, segment ranking, marketing spend ratios, and launch-period analysis. SQLite connections are scoped with context managers and analytical reads use read-only connections.

## Dashboard

```bash
streamlit run 3_streamlit_dashboard.py
```

Use the sidebar to filter year, region, therapeutic area, and channel. The dashboard includes revenue trends, portfolio comparisons, regional views, seasonality, segment rankings, and a raw filtered-data explorer. Empty filter results are handled with a visible warning.

## Tests and CI

Run the local test suite:

```bash
python -m pytest -q
```

GitHub Actions runs the tests and both command-line pipeline steps on pushes to `main` and pull requests.

## Limitations

- All records and relationships are simulated for portfolio analytics practice.
- The generator's growth, regional, channel, pricing, and seasonal assumptions are illustrative.
- Revenue-to-marketing-spend is a descriptive ratio, not causal marketing ROI.
- No clinical, regulatory, patient, prescribing, or actual market data is included.
- Streamlit visual behavior is not covered by the unit tests; the CLI generation and SQL workflow are covered.
