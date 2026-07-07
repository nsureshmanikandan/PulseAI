import pandas as pd
from typing import Dict, Any


def detect_schema(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Classify each column by type and compute basic profile stats."""
    schema = {}
    for col in df.columns:
        series = df[col]
        null_pct = round(series.isna().mean() * 100, 2)
        unique_count = int(series.nunique(dropna=True))
        col_type = _classify_column(series)
        schema[col] = {"type": col_type, "null_pct": null_pct, "unique_count": unique_count}
    return schema


def _classify_column(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if series.dtype == object:
        try:
            pd.to_datetime(series.dropna().head(20), infer_datetime_format=True)
            return "datetime"
        except Exception:
            pass
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    unique_ratio = series.nunique(dropna=True) / max(len(series.dropna()), 1)
    if unique_ratio < 0.5:
        return "categorical"
    return "text"
