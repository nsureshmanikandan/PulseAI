import pandas as pd
import pytest
from backend.modules.ingestion.schema_detector import detect_schema


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "Revenue": [1000.0, 2000.0],
        "Category": ["A", "B"],
        "Notes": ["long text here", "another note"],
    })


def test_detects_datetime_column(sample_df):
    schema = detect_schema(sample_df)
    assert schema["Date"]["type"] == "datetime"


def test_detects_numeric_column(sample_df):
    schema = detect_schema(sample_df)
    assert schema["Revenue"]["type"] == "numeric"


def test_detects_categorical_column(sample_df):
    schema = detect_schema(sample_df)
    assert schema["Category"]["type"] == "categorical"


def test_includes_null_percentage(sample_df):
    schema = detect_schema(sample_df)
    assert "null_pct" in schema["Revenue"]
    assert schema["Revenue"]["null_pct"] == 0.0


def test_includes_unique_count(sample_df):
    schema = detect_schema(sample_df)
    assert schema["Category"]["unique_count"] == 2
