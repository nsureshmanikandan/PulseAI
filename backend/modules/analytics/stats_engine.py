import pandas as pd
from typing import Dict, Any


def compute_stats(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Compute descriptive statistics for all numeric columns."""
    stats = {}
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        has_outliers = bool(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).any())
        stats[col] = {
            "mean": round(float(series.mean()), 4),
            "median": round(float(series.median()), 4),
            "std": round(float(series.std()), 4),
            "min": round(float(series.min()), 4),
            "max": round(float(series.max()), 4),
            "sum": round(float(series.sum()), 4),
            "has_outliers": has_outliers,
        }
    return stats
