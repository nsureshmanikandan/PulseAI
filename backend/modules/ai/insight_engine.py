import pandas as pd
import numpy as np
from typing import List, Dict, Any
from backend.modules.analytics.stats_engine import compute_stats


def extract_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Auto-detect anomalies and notable patterns in a DataFrame."""
    insights = []
    stats = compute_stats(df)

    # Outlier detection
    for col, s in stats.items():
        if s.get("has_outliers"):
            insights.append({
                "type": "outlier",
                "column": col,
                "message": f"Column '{col}' contains outlier values that may skew analysis.",
                "severity": "warning",
            })

    # Missing data detection
    for col in df.columns:
        null_count = df[col].isna().sum()
        null_pct = null_count / len(df) * 100 if len(df) > 0 else 0
        if null_pct > 10:
            insights.append({
                "type": "missing_data",
                "column": col,
                "message": f"Column '{col}' has {null_pct:.1f}% missing (null) values.",
                "severity": "warning" if null_pct < 50 else "critical",
            })

    return insights
