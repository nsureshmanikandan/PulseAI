import pandas as pd
from backend.modules.analytics.kpi_extractor import extract_kpis


def test_extracts_top_numeric_columns():
    df = pd.DataFrame({"revenue": [100, 200], "cost": [50, 80], "name": ["A", "B"]})
    kpis = extract_kpis(df)
    assert any(k["column"] == "revenue" for k in kpis)
    assert not any(k["column"] == "name" for k in kpis)


def test_kpi_includes_sum_and_mean():
    df = pd.DataFrame({"revenue": [100, 200]})
    kpis = extract_kpis(df)
    kpi = kpis[0]
    assert "sum" in kpi
    assert "mean" in kpi
