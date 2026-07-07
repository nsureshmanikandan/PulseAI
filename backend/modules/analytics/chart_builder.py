import pandas as pd
from typing import Optional

SUPPORTED_TYPES = {"bar", "line", "scatter", "pie", "histogram", "heatmap"}


def build_chart(df: pd.DataFrame, chart_type: str, x: str, y: Optional[str] = None) -> dict:
    """Generate a Plotly-compatible chart config dict from a DataFrame."""
    if chart_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported chart type: {chart_type}. Choose from {SUPPORTED_TYPES}")

    if chart_type == "bar":
        return {"type": "bar", "data": [{"x": df[x].tolist(), "y": df[y].tolist(), "type": "bar"}],
                "layout": {"xaxis": {"title": x}, "yaxis": {"title": y}}}

    if chart_type == "line":
        return {"type": "line", "data": [{"x": df[x].tolist(), "y": df[y].tolist(), "type": "scatter", "mode": "lines+markers"}],
                "layout": {"xaxis": {"title": x}, "yaxis": {"title": y}}}

    if chart_type == "scatter":
        return {"type": "scatter", "data": [{"x": df[x].tolist(), "y": df[y].tolist(), "type": "scatter", "mode": "markers"}],
                "layout": {"xaxis": {"title": x}, "yaxis": {"title": y}}}

    if chart_type == "pie":
        return {"type": "pie", "data": [{"labels": df[x].tolist(), "values": df[y].tolist(), "type": "pie"}], "layout": {}}

    if chart_type == "histogram":
        return {"type": "histogram", "data": [{"x": df[x].tolist(), "type": "histogram"}],
                "layout": {"xaxis": {"title": x}}}

    if chart_type == "heatmap":
        pivot = df.pivot_table(index=df.columns[0], columns=df.columns[1], values=y, aggfunc="sum").fillna(0)
        return {"type": "heatmap", "data": [{"z": pivot.values.tolist(), "x": pivot.columns.tolist(),
                "y": pivot.index.tolist(), "type": "heatmap"}], "layout": {}}

    return {}
