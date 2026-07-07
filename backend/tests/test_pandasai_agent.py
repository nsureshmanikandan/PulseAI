import pandas as pd
import pytest
from unittest.mock import patch, MagicMock


def test_query_returns_result():
    mock_llm = MagicMock()
    dfs = {"sales": pd.DataFrame({"revenue": [100, 200], "month": ["Jan", "Feb"]})}

    with patch("backend.modules.ai.pandasai_agent.create_llm", return_value=mock_llm):
        with patch("backend.modules.ai.pandasai_agent.SmartDatalake") as mock_lake_cls:
            mock_lake = MagicMock()
            mock_lake.chat.return_value = "Revenue in Jan was 100"
            mock_lake_cls.return_value = mock_lake

            from backend.modules.ai.pandasai_agent import query_datalake
            result = query_datalake(dfs, "What was revenue in Jan?")
            assert result == "Revenue in Jan was 100"


def test_empty_dataframes_raises():
    from backend.modules.ai.pandasai_agent import query_datalake
    with pytest.raises(ValueError, match="No DataFrames"):
        query_datalake({}, "Any question")
