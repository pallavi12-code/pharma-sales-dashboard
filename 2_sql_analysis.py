"""
STEP 2 — SQL Business Analysis
8 real-world business questions answered with SQL.
This is exactly what Roche GATE analysts do daily.
Run after 1_generate_dataset.py
"""

import sqlite3
import pandas as pd

conn = sqlite3.connect("pharma_sales.db")

def run_query(title, sql, insight=""):
    print(f"\n{'='*65}")
    print(f"📌 {title}")
    print('='*65)
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    if insight:
        print(f"\n💡 Insight: {insight}")
    return df

# ─────────────────────────────────────────────────────────────────────────────
# Q1: Total revenue by drug — which products drive the most value?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q1: Revenue by drug (all years)",
    """
    SELECT
        drug_name,
        category,
        ROUND(SUM(revenue) / 1e6, 2)       AS total_revenue_M,
        ROUND(AVG(gross_margin_pct), 1)     AS avg_margin_pct,
        SUM(units_sold)                     AS total_units
    FROM sales
    GROUP BY drug_name, category
    ORDER BY total_revenue_M DESC
    """,
    "Your top-revenue drug tells you where Roche is most dependent — useful for risk discussions."
)

# ─────────────────────────────────────────────────────────────────────────────
# Q2: Year-over-year revenue growth per drug (window function)
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q2: Year-over-year revenue growth per drug",
    """
    WITH yearly AS (
        SELECT
            drug_name,
            year,
            ROUND(SUM(revenue) / 1e6, 2) AS revenue_M
        FROM sales
        GROUP BY drug_name, year
    )
    SELECT
        drug_name,
        year,
        revenue_M,
        LAG(revenue_M) OVER (PARTITION BY drug_name ORDER BY year) AS prev_year_M,
        ROUND(
            (revenue_M - LAG(revenue_M) OVER (PARTITION BY drug_name ORDER BY year))
            / LAG(revenue_M) OVER (PARTITION BY drug_name ORDER BY year) * 100,
        1) AS yoy_growth_pct
    FROM yearly
    ORDER BY drug_name, year
    """,
    "LAG() is a window function — very common in pharma analytics to track trend vs prior period."
)

# ─────────────────────────────────────────────────────────────────────────────
# Q3: Regional performance — which geography contributes most?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q3: Revenue by region with % share",
    """
    SELECT
        region,
        ROUND(SUM(revenue) / 1e6, 2)                             AS revenue_M,
        ROUND(SUM(revenue) * 100.0 / SUM(SUM(revenue)) OVER (), 1) AS pct_share,
        ROUND(AVG(gross_margin_pct), 1)                           AS avg_margin_pct,
        SUM(units_sold)                                           AS total_units
    FROM sales
    GROUP BY region
    ORDER BY revenue_M DESC
    """,
    "% share tells you geographic concentration risk. If 1 region = 50%+ of revenue, that's a flag."
)

# ─────────────────────────────────────────────────────────────────────────────
# Q4: Seasonal trends — does Q4 really outperform?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q4: Quarterly revenue seasonality",
    """
    SELECT
        quarter,
        ROUND(SUM(revenue) / 1e6, 2)   AS total_revenue_M,
        ROUND(AVG(units_sold), 0)       AS avg_units_per_record,
        COUNT(*)                        AS num_records
    FROM sales
    GROUP BY quarter
    ORDER BY quarter
    """,
    "Q4 seasonality is a classic pharma pattern — patients fill prescriptions before year-end benefits reset."
)

# ─────────────────────────────────────────────────────────────────────────────
# Q5: Channel mix — where are sales coming from?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q5: Revenue and margin by sales channel",
    """
    SELECT
        channel,
        ROUND(SUM(revenue) / 1e6, 2)       AS revenue_M,
        ROUND(AVG(gross_margin_pct), 1)     AS avg_margin_pct,
        ROUND(SUM(mkt_spend) / 1e6, 2)      AS mkt_spend_M,
        ROUND(SUM(mkt_spend) / SUM(revenue) * 100, 1) AS mkt_as_pct_revenue
    FROM sales
    GROUP BY channel
    ORDER BY revenue_M DESC
    """,
    "Online Pharmacy often has lower margin but lower marketing spend — the net picture matters more."
)

# ─────────────────────────────────────────────────────────────────────────────
# Q6: Top 5 drug-region combos (the highest-value segments)
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q6: Top 10 drug × region revenue segments",
    """
    SELECT
        drug_name,
        region,
        ROUND(SUM(revenue) / 1e6, 2) AS revenue_M,
        ROUND(AVG(gross_margin_pct), 1) AS avg_margin_pct
    FROM sales
    GROUP BY drug_name, region
    ORDER BY revenue_M DESC
    LIMIT 10
    """,
    "Segment-level analysis helps affiliates decide where to double down sales rep resources."
)

# ─────────────────────────────────────────────────────────────────────────────
# Q7: Marketing ROI — which drugs have the best spend efficiency?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q7: Marketing ROI by drug",
    """
    SELECT
        drug_name,
        category,
        ROUND(SUM(revenue) / 1e6, 2)           AS revenue_M,
        ROUND(SUM(mkt_spend) / 1e6, 2)          AS mkt_spend_M,
        ROUND(SUM(revenue) / SUM(mkt_spend), 2) AS revenue_per_mkt_rupee
    FROM sales
    GROUP BY drug_name, category
    ORDER BY revenue_per_mkt_rupee DESC
    """,
    "Revenue-per-rupee-spent is a simple ROI metric. Present this to a marketing stakeholder and they'll lean forward."
)

# ─────────────────────────────────────────────────────────────────────────────
# Q8: New drug ramp-up — how fast did Immuflex (launched 2021) grow?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q8: New drug ramp-up trajectory (Immuflex, launched 2021)",
    """
    SELECT
        year,
        quarter,
        ROUND(SUM(revenue) / 1e6, 2) AS revenue_M,
        SUM(units_sold) AS units_sold
    FROM sales
    WHERE drug_name = 'Immuflex'
    GROUP BY year, quarter
    ORDER BY year, quarter
    """,
    "Launch trajectory analysis tells lifecycle teams whether a drug is on track vs forecast."
)

conn.close()
print("\n\n✅ All SQL queries complete. These 8 questions = a complete business story.")
print("   → Next: run 3_streamlit_dashboard.py to see the visual dashboard")
