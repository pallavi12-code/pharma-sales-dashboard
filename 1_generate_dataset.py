"""Generate the reproducible synthetic dataset and SQLite database."""

from __future__ import annotations

import argparse

from analytics import DEFAULT_CSV_PATH, DEFAULT_DB_PATH, generate_pharma_data, write_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--csv", type=str, default=str(DEFAULT_CSV_PATH))
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB_PATH))
    args = parser.parse_args()

    df = generate_pharma_data(args.seed)
    write_dataset(df, args.csv, args.db)
    print(f"CSV saved: {args.csv} ({len(df):,} rows)")
    print(f"SQLite database saved: {args.db}")
    print(f"Seed: {args.seed}")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()
