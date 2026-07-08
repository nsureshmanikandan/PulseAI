import math
import pandas as pd
from typing import Optional

SUPPORTED_TYPES = {"bar", "line", "scatter", "pie", "histogram", "heatmap"}


def _safe_list(series: pd.Series) -> list:
    """Convert a Series to a JSON-safe list (replace NaN/Inf with None)."""
    def _clean(v):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        # numpy scalar → python native
        try:
            return v.item()
        except AttributeError:
            return v
    return [_clean(v) for v in series]


def build_chart(df: pd.DataFrame, chart_type: str, x: str, y: Optional[str] = None) -> dict:
    if chart_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported chart type: {chart_type}. Choose from {sorted(SUPPORTED_TYPES)}")

    if x not in df.columns:
        raise ValueError(f"Column '{x}' not found. Available: {list(df.columns)}")
    if y and y not in df.columns:
        raise ValueError(f"Column '{y}' not found. Available: {list(df.columns)}")

    dark_layout = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(255,255,255,0.04)",
        "font": {"color": "#e2e8f0", "size": 12},
        "xaxis": {"gridcolor": "rgba(255,255,255,0.08)", "title": x},
        "yaxis": {"gridcolor": "rgba(255,255,255,0.08)", "title": y or ""},
        "margin": {"l": 50, "r": 20, "t": 30, "b": 50},
    }

    if chart_type == "bar":
        return {
            "data": [{"x": _safe_list(df[x]), "y": _safe_list(df[y]), "type": "bar",
                      "marker": {"color": "#3b82f6"}}],
            "layout": {**dark_layout},
        }

    if chart_type == "line":
        return {
            "data": [{"x": _safe_list(df[x]), "y": _safe_list(df[y]),
                      "type": "scatter", "mode": "lines+markers",
                      "line": {"color": "#3b82f6"}}],
            "layout": {**dark_layout},
        }

    if chart_type == "scatter":
        return {
            "data": [{"x": _safe_list(df[x]), "y": _safe_list(df[y]),
                      "type": "scatter", "mode": "markers",
                      "marker": {"color": "#3b82f6", "opacity": 0.7}}],
            "layout": {**dark_layout},
        }

    if chart_type == "pie":
        counts = df[x].value_counts()
        return {
            "data": [{"labels": counts.index.tolist(), "values": _safe_list(counts),
                      "type": "pie", "hole": 0.4}],
            "layout": {**dark_layout, "xaxis": {}, "yaxis": {}},
        }

    if chart_type == "histogram":
        return {
            "data": [{"x": _safe_list(df[x]), "type": "histogram",
                      "marker": {"color": "#3b82f6"}}],
            "layout": {**dark_layout},
        }

    if chart_type == "heatmap":
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if len(num_cols) < 2:
            raise ValueError("Heatmap requires at least 2 numeric columns")
        corr = df[num_cols].corr().round(2)
        return {
            "data": [{"z": corr.values.tolist(), "x": corr.columns.tolist(),
                      "y": corr.index.tolist(), "type": "heatmap",
                      "colorscale": "Blues"}],
            "layout": {**dark_layout, "xaxis": {"title": ""}, "yaxis": {"title": ""}},
        }

    return {}
