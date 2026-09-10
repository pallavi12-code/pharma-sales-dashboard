"""Reusable data-generation and SQLite helpers for the analytics workflow."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "pharma_sales_data.csv"
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "pharma_sales.db"

DRUGS = {
    "Oncovir": {"category": "Oncology", "base_price": 4200, "launch_year": 2019},
    "Cardilux": {"category": "Cardiology", "base_price": 980, "launch_year": 2018},
    "Neuromab": {"category": "Neurology", "base_price": 3100, "launch_year": 2020},
    "Diabequil": {"category": "Diabetes", "base_price": 560, "launch_year": 2017},
    "Immuflex": {"category": "Immunology", "base_price": 2800, "launch_year": 2021},
    "Rheumastat": {"category": "Immunology", "base_price": 1750, "launch_year": 2019},
    "Pulmocare": {"category": "Respiratory", "base_price": 890, "launch_year": 2020},
    "Hepazone": {"category": "Hepatology", "base_price": 2100, "launch_year": 2018},
}
REGIONS = {
    "North India": {"multiplier": 1.15, "cities": ["Delhi", "Chandigarh", "Lucknow", "Jaipur"]},
    "South India": {"multiplier": 1.25, "cities": ["Hyderabad", "Chennai", "Bengaluru", "Kochi"]},
    "West India": {"multiplier": 1.20, "cities": ["Mumbai", "Pune", "Ahmedabad", "Surat"]},
    "East India": {"multiplier": 0.90, "cities": ["Kolkata", "Bhubaneswar", "Patna", "Ranchi"]},
    "Central India": {"multiplier": 0.85, "cities": ["Nagpur", "Bhopal", "Raipur", "Indore"]},
}
CHANNELS = ["Hospital", "Retail Pharmacy", "Online Pharmacy", "Clinic"]
YEARS = [2021, 2022, 2023, 2024]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
DATA_COLUMNS = [
    "year", "quarter", "period", "drug_name", "category", "region", "city",
    "channel", "units_sold", "unit_price", "revenue", "cogs", "gross_profit",
    "mkt_spend", "gross_margin_pct",
]


def generate_pharma_data(seed: int = 42) -> pd.DataFrame:
    """Generate the deterministic synthetic dataset for ``seed``."""
    if not isinstance(seed, (int, np.integer)):
        raise TypeError("seed must be an integer")

    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    for year in YEARS:
        for quarter in QUARTERS:
            for drug_name, drug_info in DRUGS.items():
                if year < drug_info["launch_year"]:
                    continue
                for region, region_info in REGIONS.items():
                    city = rng.choice(region_info["cities"])
                    channel = rng.choice(CHANNELS, p=[0.40, 0.30, 0.20, 0.10])
                    base_units = rng.integers(800, 3000)
                    growth = 1.12 ** (year - YEARS[0])
                    seasonal = 1.15 if quarter == "Q4" else 0.92 if quarter == "Q1" else 1.0
                    units_sold = int(base_units * growth * seasonal * region_info["multiplier"])
                    unit_price = drug_info["base_price"] * rng.uniform(0.95, 1.05)
                    revenue = round(units_sold * unit_price, 2)
                    cogs = round(revenue * rng.uniform(0.35, 0.50), 2)
                    gross_profit = round(revenue - cogs, 2)
                    mkt_spend = round(revenue * rng.uniform(0.08, 0.18), 2)
                    rows.append({
                        "year": year, "quarter": quarter, "period": f"{year}-{quarter}",
                        "drug_name": drug_name, "category": drug_info["category"],
                        "region": region, "city": city, "channel": channel,
                        "units_sold": units_sold, "unit_price": round(unit_price, 2),
                        "revenue": revenue, "cogs": cogs, "gross_profit": gross_profit,
                        "mkt_spend": mkt_spend,
                        "gross_margin_pct": round(gross_profit / revenue * 100, 2),
                    })
    return pd.DataFrame(rows, columns=DATA_COLUMNS)


def write_dataset(
    df: pd.DataFrame,
    csv_path: Path = DEFAULT_CSV_PATH,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Persist sales data and its product dimension to CSV and SQLite."""
    csv_path = Path(csv_path)
    db_path = Path(db_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    dim_drugs = pd.DataFrame([
        {"drug_name": name, **details} for name, details in DRUGS.items()
    ])
    with sqlite3.connect(db_path) as connection:
        df.to_sql("sales", connection, if_exists="replace", index=False)
        dim_drugs.to_sql("dim_drugs", connection, if_exists="replace", index=False)


def read_query(sql: str, db_path: Path = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Run one read-only analytical query with a safely scoped connection."""
    db_path = Path(db_path)
    if not db_path.is_file():
        raise FileNotFoundError(f"SQLite database not found: {db_path}")
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as connection:
        return pd.read_sql_query(sql, connection)
