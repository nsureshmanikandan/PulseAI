import pandas as pd
from typing import List, Dict, Any


def extract_kpis(df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """Extract top numeric columns as KPI cards for executive view."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    kpis = []
    for col in numeric_cols[:top_n]:
        series = df[col].dropna()
        kpis.append({
            "column": col,
            "sum": round(float(series.sum()), 2),
            "mean": round(float(series.mean()), 2),
            "min": round(float(series.min()), 2),
            "max": round(float(series.max()), 2),
            "count": int(len(series)),
        })
    return kpis
