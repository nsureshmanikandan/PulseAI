import pytest
import pandas as pd
from backend.modules.analytics.chart_builder import build_chart


def test_bar_chart_returns_plotly_json():
    df = pd.DataFrame({"Category": ["A", "B", "C"], "Revenue": [100, 200, 150]})
    config = build_chart(df, chart_type="bar", x="Category", y="Revenue")
    assert config["type"] == "bar"
    assert "data" in config
    assert len(config["data"][0]["x"]) == 3


def test_line_chart_returns_plotly_json():
    df = pd.DataFrame({"Month": ["Jan", "Feb"], "Sales": [500, 700]})
    config = build_chart(df, chart_type="line", x="Month", y="Sales")
    assert config["type"] == "line"


def test_invalid_chart_type_raises():
    df = pd.DataFrame({"x": [1], "y": [2]})
    with pytest.raises(ValueError, match="Unsupported chart type"):
        build_chart(df, chart_type="radar", x="x", y="y")
