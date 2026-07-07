import pandas as pd
from backend.modules.analytics.stats_engine import compute_stats


def test_computes_mean_for_numeric():
    df = pd.DataFrame({"revenue": [100, 200, 300]})
    stats = compute_stats(df)
    assert stats["revenue"]["mean"] == 200.0


def test_computes_outlier_flag():
    df = pd.DataFrame({"revenue": [100, 110, 105, 10000]})
    stats = compute_stats(df)
    assert stats["revenue"]["has_outliers"] is True


def test_skips_non_numeric_columns():
    df = pd.DataFrame({"name": ["a", "b"], "value": [1, 2]})
    stats = compute_stats(df)
    assert "name" not in stats
    assert "value" in stats
