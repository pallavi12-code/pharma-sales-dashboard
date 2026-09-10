"""Run the project's SQL business analyses against the generated database."""

from __future__ import annotations

from analytics import DEFAULT_DB_PATH, read_query

QUERIES = {
    "Revenue by drug": """
        SELECT drug_name, category, ROUND(SUM(revenue) / 1e6, 2) AS revenue_m,
               ROUND(AVG(gross_margin_pct), 1) AS avg_margin_pct,
               SUM(units_sold) AS total_units
        FROM sales GROUP BY drug_name, category ORDER BY revenue_m DESC
    """,
    "Year-over-year revenue growth": """
        WITH yearly AS (
            SELECT drug_name, year, SUM(revenue) / 1e6 AS revenue_m
            FROM sales GROUP BY drug_name, year
        ), with_previous AS (
            SELECT *, LAG(revenue_m) OVER (PARTITION BY drug_name ORDER BY year) AS previous_m
            FROM yearly
        )
        SELECT drug_name, year, ROUND(revenue_m, 2) AS revenue_m,
               ROUND((revenue_m - previous_m) / NULLIF(previous_m, 0) * 100, 1) AS yoy_growth_pct
        FROM with_previous ORDER BY drug_name, year
    """,
    "Revenue by region": """
        SELECT region, ROUND(SUM(revenue) / 1e6, 2) AS revenue_m,
               ROUND(SUM(revenue) * 100.0 / SUM(SUM(revenue)) OVER (), 1) AS pct_share,
               ROUND(AVG(gross_margin_pct), 1) AS avg_margin_pct,
               SUM(units_sold) AS total_units
        FROM sales GROUP BY region ORDER BY revenue_m DESC
    """,
    "Quarterly seasonality": """
        SELECT quarter, ROUND(SUM(revenue) / 1e6, 2) AS revenue_m,
               ROUND(AVG(units_sold), 0) AS avg_units_per_record, COUNT(*) AS records
        FROM sales GROUP BY quarter ORDER BY CASE quarter WHEN 'Q1' THEN 1 WHEN 'Q2' THEN 2
             WHEN 'Q3' THEN 3 ELSE 4 END
    """,
    "Revenue and margin by channel": """
        SELECT channel, ROUND(SUM(revenue) / 1e6, 2) AS revenue_m,
               ROUND(AVG(gross_margin_pct), 1) AS avg_margin_pct,
               ROUND(SUM(mkt_spend) / 1e6, 2) AS marketing_spend_m,
               ROUND(SUM(mkt_spend) / NULLIF(SUM(revenue), 0) * 100, 1) AS marketing_pct
        FROM sales GROUP BY channel ORDER BY revenue_m DESC
    """,
    "Top drug-region segments": """
        SELECT drug_name, region, ROUND(SUM(revenue) / 1e6, 2) AS revenue_m,
               ROUND(AVG(gross_margin_pct), 1) AS avg_margin_pct
        FROM sales GROUP BY drug_name, region ORDER BY revenue_m DESC LIMIT 10
    """,
    "Marketing ROI by drug": """
        SELECT drug_name, category, ROUND(SUM(revenue) / 1e6, 2) AS revenue_m,
               ROUND(SUM(mkt_spend) / 1e6, 2) AS marketing_spend_m,
               ROUND(SUM(revenue) / NULLIF(SUM(mkt_spend), 0), 2) AS revenue_per_marketing_rupee
        FROM sales GROUP BY drug_name, category ORDER BY revenue_per_marketing_rupee DESC
    """,
    "Immuflex ramp-up": """
        SELECT year, quarter, ROUND(SUM(revenue) / 1e6, 2) AS revenue_m, SUM(units_sold) AS units_sold
        FROM sales WHERE drug_name = 'Immuflex'
        GROUP BY year, quarter ORDER BY year, CASE quarter WHEN 'Q1' THEN 1 WHEN 'Q2' THEN 2
        WHEN 'Q3' THEN 3 ELSE 4 END
    """,
}


def main() -> None:
    for title, query in QUERIES.items():
        print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")
        print(read_query(query).to_string(index=False))


if __name__ == "__main__":
    main()
