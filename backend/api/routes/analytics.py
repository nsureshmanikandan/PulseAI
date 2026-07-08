import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.models.db import Dataset, TabProfile, get_db
from backend.modules.analytics.stats_engine import compute_stats
from backend.modules.analytics.kpi_extractor import extract_kpis
from backend.modules.analytics.chart_builder import build_chart
from backend.modules.ingestion.parser import parse_excel

router = APIRouter()


def _load_tab_df(dataset_id: str, tab_name: str, db: Session):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    dfs = parse_excel(ds.blob_path)
    if tab_name not in dfs:
        raise HTTPException(status_code=404, detail=f"Tab '{tab_name}' not found")
    return dfs[tab_name]


@router.get("/{dataset_id}/stats/{tab_name}")
def get_stats(dataset_id: str, tab_name: str, db: Session = Depends(get_db)):
    df = _load_tab_df(dataset_id, tab_name, db)
    return compute_stats(df)


@router.get("/{dataset_id}/kpis/{tab_name}")
def get_kpis(dataset_id: str, tab_name: str, db: Session = Depends(get_db)):
    df = _load_tab_df(dataset_id, tab_name, db)
    return extract_kpis(df)


class ChartRequest(BaseModel):
    tab_name: str
    chart_type: str
    x: str
    y: Optional[str] = None


@router.post("/{dataset_id}/chart")
def generate_chart(dataset_id: str, req: ChartRequest, db: Session = Depends(get_db)):
    df = _load_tab_df(dataset_id, req.tab_name, db)
    try:
        return build_chart(df, req.chart_type, req.x, req.y)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{dataset_id}/auto-charts/{tab_name}")
def auto_charts(dataset_id: str, tab_name: str, db: Session = Depends(get_db)):
    """Return a set of automatically chosen charts that best describe the dataset."""
    from backend.modules.analytics.chart_builder import build_chart, _safe_list
    import math

    df = _load_tab_df(dataset_id, tab_name, db)
    charts = []

    num_cols = df.select_dtypes(include="number").columns.tolist()
    # Exclude ID-like columns: >80% unique values or column name hints at an identifier
    _id_hints = ("id", "uuid", "key", "code", "ref", "no", "num", "number", "serial")
    def _is_id_col(col: str) -> bool:
        col_lower = col.lower()
        if any(col_lower == h or col_lower.endswith(f"_{h}") or col_lower.endswith(h) for h in _id_hints):
            return True
        nunique = df[col].nunique()
        return nunique > 0 and (nunique / len(df)) > 0.8
    cat_cols = [c for c in df.select_dtypes(include=["object", "category"]).columns.tolist()
                if not _is_id_col(c)]

    dark = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(255,255,255,0.03)",
        "font": {"color": "#cbd5e1", "size": 11},
        "margin": {"l": 50, "r": 20, "t": 40, "b": 50},
        "xaxis": {"gridcolor": "rgba(255,255,255,0.07)", "zerolinecolor": "rgba(255,255,255,0.07)"},
        "yaxis": {"gridcolor": "rgba(255,255,255,0.07)", "zerolinecolor": "rgba(255,255,255,0.07)"},
    }

    BLUE_PALETTE = ["#3b82f6", "#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#ec4899"]
    # High-contrast palette for pie/donut — each color is visually distinct
    DISTINCT_PALETTE = [
        "#3b82f6",  # blue
        "#10b981",  # emerald green
        "#f59e0b",  # amber
        "#ef4444",  # red
        "#8b5cf6",  # violet
        "#06b6d4",  # cyan
        "#f97316",  # orange
        "#ec4899",  # pink
        "#84cc16",  # lime
        "#14b8a6",  # teal
        "#a855f7",  # purple
        "#eab308",  # yellow
    ]

    # 1. Histograms for up to 4 numeric columns
    for col in num_cols[:4]:
        charts.append({
            "title": f"Distribution — {col}",
            "subtitle": "Histogram",
            "data": [{"x": _safe_list(df[col].dropna()), "type": "histogram",
                      "name": col, "marker": {"color": "#3b82f6", "opacity": 0.85},
                      "nbinsx": 30}],
            "layout": {**dark, "title": {"text": f"Distribution of {col}", "font": {"size": 13, "color": "#e2e8f0"}},
                       "xaxis": {**dark["xaxis"], "title": col}, "yaxis": {**dark["yaxis"], "title": "Count"}},
        })

    # 2. Top 8 categories for up to 3 categorical columns
    for col in cat_cols[:3]:
        counts = df[col].value_counts().head(8)
        charts.append({
            "title": f"Top Categories — {col}",
            "subtitle": "Bar Chart",
            "data": [{"x": counts.index.tolist(), "y": counts.values.tolist(),
                      "type": "bar", "marker": {"color": DISTINCT_PALETTE[:len(counts)]}}],
            "layout": {**dark, "title": {"text": f"Top Values: {col}", "font": {"size": 13, "color": "#e2e8f0"}},
                       "xaxis": {**dark["xaxis"], "title": col}, "yaxis": {**dark["yaxis"], "title": "Count"}},
        })

    # 3. Correlation heatmap (if ≥2 numeric cols)
    if len(num_cols) >= 2:
        corr = df[num_cols].corr().round(2)
        charts.append({
            "title": "Correlation Matrix",
            "subtitle": "Heatmap — numeric columns",
            "data": [{"z": corr.values.tolist(), "x": corr.columns.tolist(),
                      "y": corr.index.tolist(), "type": "heatmap",
                      "colorscale": [[0, "#1e3a5f"], [0.5, "#3b82f6"], [1, "#93c5fd"]],
                      "zmin": -1, "zmax": 1, "text": corr.values.round(2).tolist(),
                      "texttemplate": "%{text}", "showscale": True}],
            "layout": {**dark, "title": {"text": "Feature Correlation", "font": {"size": 13, "color": "#e2e8f0"}},
                       "xaxis": {**dark["xaxis"], "title": ""},
                       "yaxis": {**dark["yaxis"], "title": ""}},
        })

    # 4. Scatter: top 2 numeric cols (relationships)
    if len(num_cols) >= 2:
        x_col, y_col = num_cols[0], num_cols[1]
        charts.append({
            "title": f"{x_col} vs {y_col}",
            "subtitle": "Scatter — relationship",
            "data": [{"x": _safe_list(df[x_col]), "y": _safe_list(df[y_col]),
                      "type": "scatter", "mode": "markers",
                      "marker": {"color": "#6366f1", "size": 5, "opacity": 0.6}}],
            "layout": {**dark, "title": {"text": f"{x_col} vs {y_col}", "font": {"size": 13, "color": "#e2e8f0"}},
                       "xaxis": {**dark["xaxis"], "title": x_col},
                       "yaxis": {**dark["yaxis"], "title": y_col}},
        })

    # 5. Box plots for numeric cols (outlier visibility)
    if num_cols:
        box_cols = num_cols[:5]
        # normalise so different scales don't collapse
        charts.append({
            "title": "Outlier Overview",
            "subtitle": "Box plots — numeric columns",
            "data": [
                {"y": _safe_list(df[c].dropna()), "type": "box", "name": c,
                 "marker": {"color": BLUE_PALETTE[i % len(BLUE_PALETTE)]},
                 "boxmean": True}
                for i, c in enumerate(box_cols)
            ],
            "layout": {**dark, "title": {"text": "Distribution & Outliers", "font": {"size": 13, "color": "#e2e8f0"}},
                       "yaxis": {**dark["yaxis"], "title": "Value"}, "showlegend": True},
        })

    # 6. Pie for first categorical col with meaningful cardinality (2–30 distinct values)
    _donut_cols = [c for c in cat_cols if 2 <= df[c].nunique() <= 30]
    if _donut_cols:
        cat_cols_for_donut = _donut_cols
    elif cat_cols:
        cat_cols_for_donut = cat_cols
    else:
        cat_cols_for_donut = []
    if cat_cols_for_donut:
        counts = df[cat_cols_for_donut[0]].value_counts().head(8)
        charts.append({
            "title": f"Share — {cat_cols_for_donut[0]}",
            "subtitle": "Donut chart",
            "data": [{"labels": counts.index.tolist(), "values": counts.values.tolist(),
                      "type": "pie", "hole": 0.45,
                      "marker": {"colors": DISTINCT_PALETTE}}],
            "layout": {**dark, "title": {"text": f"Composition: {cat_cols_for_donut[0]}", "font": {"size": 13, "color": "#e2e8f0"}},
                       "showlegend": True, "legend": {"font": {"color": "#94a3b8"}}},
        })

    return charts
