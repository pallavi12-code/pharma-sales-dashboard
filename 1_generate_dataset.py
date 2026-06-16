"""
STEP 1 — Generate Dataset
Creates a realistic pharma sales dataset (1200 rows) and loads it into SQLite.
Run this first before anything else.
"""

import pandas as pd
import numpy as np
import sqlite3
import os

np.random.seed(42)

# ── Config ────────────────────────────────────────────────────────────────────

DRUGS = {
    "Oncovir":    {"category": "Oncology",      "base_price": 4200, "launch_year": 2019},
    "Cardilux":   {"category": "Cardiology",    "base_price": 980,  "launch_year": 2018},
    "Neuromab":   {"category": "Neurology",     "base_price": 3100, "launch_year": 2020},
    "Diabequil":  {"category": "Diabetes",      "base_price": 560,  "launch_year": 2017},
    "Immuflex":   {"category": "Immunology",    "base_price": 2800, "launch_year": 2021},
    "Rheumastat": {"category": "Immunology",    "base_price": 1750, "launch_year": 2019},
    "Pulmocare":  {"category": "Respiratory",   "base_price": 890,  "launch_year": 2020},
    "Hepazone":   {"category": "Hepatology",    "base_price": 2100, "launch_year": 2018},
}

REGIONS = {
    "North India":  {"multiplier": 1.15, "cities": ["Delhi", "Chandigarh", "Lucknow", "Jaipur"]},
    "South India":  {"multiplier": 1.25, "cities": ["Hyderabad", "Chennai", "Bengaluru", "Kochi"]},
    "West India":   {"multiplier": 1.20, "cities": ["Mumbai", "Pune", "Ahmedabad", "Surat"]},
    "East India":   {"multiplier": 0.90, "cities": ["Kolkata", "Bhubaneswar", "Patna", "Ranchi"]},
    "Central India":{"multiplier": 0.85, "cities": ["Nagpur", "Bhopal", "Raipur", "Indore"]},
}

CHANNELS = ["Hospital", "Retail Pharmacy", "Online Pharmacy", "Clinic"]
QUARTERS  = ["Q1", "Q2", "Q3", "Q4"]
YEARS     = [2021, 2022, 2023, 2024]

# ── Generate rows ─────────────────────────────────────────────────────────────

rows = []
for year in YEARS:
    for quarter in QUARTERS:
        for drug_name, drug_info in DRUGS.items():
            # Drug only exists after launch year
            if year < drug_info["launch_year"]:
                continue
            for region, reg_info in REGIONS.items():
                city = np.random.choice(reg_info["cities"])
                channel = np.random.choice(CHANNELS, p=[0.40, 0.30, 0.20, 0.10])

                # Units sold — grows ~12% YoY, seasonal bump in Q4
                base_units = np.random.randint(800, 3000)
                yoy_growth = (1.12 ** (year - 2021))
                seasonal   = 1.15 if quarter == "Q4" else (0.92 if quarter == "Q1" else 1.0)
                units_sold = int(base_units * yoy_growth * seasonal * reg_info["multiplier"])

                # Price with small random variance
                unit_price  = drug_info["base_price"] * np.random.uniform(0.95, 1.05)
                revenue     = round(units_sold * unit_price, 2)

                # Cost of goods ~35–50% of revenue
                cogs        = round(revenue * np.random.uniform(0.35, 0.50), 2)
                gross_profit = round(revenue - cogs, 2)

                # Marketing spend as % of revenue
                mkt_spend   = round(revenue * np.random.uniform(0.08, 0.18), 2)

                rows.append({
                    "year":          year,
                    "quarter":       quarter,
                    "period":        f"{year}-{quarter}",
                    "drug_name":     drug_name,
                    "category":      drug_info["category"],
                    "region":        region,
                    "city":          city,
                    "channel":       channel,
                    "units_sold":    units_sold,
                    "unit_price":    round(unit_price, 2),
                    "revenue":       revenue,
                    "cogs":          cogs,
                    "gross_profit":  gross_profit,
                    "mkt_spend":     mkt_spend,
                    "gross_margin_pct": round((gross_profit / revenue) * 100, 2),
                })

df = pd.DataFrame(rows)

# ── Save CSV ──────────────────────────────────────────────────────────────────

csv_path = "pharma_sales_data.csv"
df.to_csv(csv_path, index=False)
print(f"✅ CSV saved: {csv_path}  ({len(df):,} rows)")

# ── Load into SQLite ──────────────────────────────────────────────────────────

db_path = "pharma_sales.db"
conn    = sqlite3.connect(db_path)

df.to_sql("sales", conn, if_exists="replace", index=False)

# Create a dim_drugs lookup table
dim_drugs = pd.DataFrame([
    {"drug_name": k, "category": v["category"],
     "base_price": v["base_price"], "launch_year": v["launch_year"]}
    for k, v in DRUGS.items()
])
dim_drugs.to_sql("dim_drugs", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print(f"✅ SQLite DB saved: {db_path}")
print(f"\n📊 Dataset preview:")
print(df.head(5).to_string(index=False))
print(f"\nShape: {df.shape}")
print(f"Years: {sorted(df['year'].unique())}")
print(f"Drugs: {sorted(df['drug_name'].unique())}")
print(f"Regions: {sorted(df['region'].unique())}")
