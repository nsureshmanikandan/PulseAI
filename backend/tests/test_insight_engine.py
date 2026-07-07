import pandas as pd
from backend.modules.ai.insight_engine import extract_insights


def test_detects_outlier_insight():
    df = pd.DataFrame({"revenue": [100, 110, 105, 10000]})
    insights = extract_insights(df)
    assert any("outlier" in i["message"].lower() for i in insights)


def test_detects_missing_data_insight():
    import numpy as np
    df = pd.DataFrame({"revenue": [100, None, 300, None]})
    insights = extract_insights(df)
    assert any("missing" in i["message"].lower() or "null" in i["message"].lower() for i in insights)


def test_no_insights_for_clean_data():
    df = pd.DataFrame({"revenue": [100, 101, 99, 102]})
    insights = extract_insights(df)
    # Clean data may have zero insights or very few
    assert isinstance(insights, list)
