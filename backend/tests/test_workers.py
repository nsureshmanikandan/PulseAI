import pandas as pd
import pytest
from unittest.mock import patch, MagicMock


def test_process_upload_task_runs():
    mock_dfs = {"Sheet1": pd.DataFrame({"col": [1, 2, 3]})}

    with patch("backend.workers.tasks.parse_excel", return_value=mock_dfs) as mock_parse, \
         patch("backend.workers.tasks.detect_schema", return_value={"col": "numeric"}) as mock_schema, \
         patch("backend.workers.tasks.find_relationships", return_value=[]) as mock_rel, \
         patch("backend.workers.tasks.extract_insights", return_value=[]) as mock_insights, \
         patch("backend.workers.tasks.SessionLocal") as mock_session:

        mock_db = MagicMock()
        mock_session.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_session.return_value.__exit__ = MagicMock(return_value=False)

        from backend.workers.tasks import process_upload
        result = process_upload("fake/path.xlsx", "dataset-123")

        assert result["status"] == "completed"
        assert result["tab_count"] == 1
        mock_parse.assert_called_once_with("fake/path.xlsx")


def test_process_upload_handles_parse_error():
    with patch("backend.workers.tasks.parse_excel", side_effect=Exception("File corrupt")):
        from backend.workers.tasks import process_upload
        result = process_upload("bad/path.xlsx", "dataset-999")
        assert result["status"] == "failed"
        assert "error" in result
