import pandas as pd
import pytest

from analytics import DATA_COLUMNS, generate_pharma_data, read_query, write_dataset


def test_generation_is_reproducible_and_has_expected_schema():
    first = generate_pharma_data(seed=7)
    second = generate_pharma_data(seed=7)

    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 640
    assert list(first.columns) == DATA_COLUMNS
    assert (first["revenue"] > 0).all()
    assert (first["gross_margin_pct"].between(50, 65)).all()


def test_different_seeds_change_simulated_values():
    assert not generate_pharma_data(1).equals(generate_pharma_data(2))


def test_invalid_seed_is_rejected():
    with pytest.raises(TypeError, match="seed must be an integer"):
        generate_pharma_data("42")


def test_write_dataset_creates_both_tables_and_read_query_is_read_only(tmp_path):
    csv_path = tmp_path / "nested" / "sales.csv"
    db_path = tmp_path / "nested" / "sales.db"
    write_dataset(generate_pharma_data(42), csv_path, db_path)

    assert csv_path.exists()
    tables = read_query(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name", db_path
    )["name"].tolist()
    assert tables == ["dim_drugs", "sales"]
    assert read_query("SELECT COUNT(*) AS count FROM sales", db_path).at[0, "count"] == 640

    with pytest.raises(pd.errors.DatabaseError):
        read_query("INSERT INTO sales(year) VALUES (2025)", db_path)
