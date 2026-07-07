import pandas as pd
from unittest.mock import patch, MagicMock


def test_generate_narrative_returns_string():
    df = pd.DataFrame({"revenue": [100, 200, 300], "month": ["Jan", "Feb", "Mar"]})
    mock_llm = MagicMock()
    mock_llm.call.return_value = "Revenue grew steadily. Jan had lowest at 100. Mar peaked at 300."

    with patch("backend.modules.ai.narrative.create_llm", return_value=mock_llm):
        from backend.modules.ai.narrative import generate_narrative
        result = generate_narrative(df, dataset_name="Sales Data")
        assert isinstance(result, str)
        assert len(result) > 0


def test_generate_narrative_fallback_on_error():
    df = pd.DataFrame({"revenue": [100, 200]})

    with patch("backend.modules.ai.narrative.create_llm", side_effect=Exception("LLM unavailable")):
        from backend.modules.ai.narrative import generate_narrative
        result = generate_narrative(df, dataset_name="Sales")
        assert "unable" in result.lower() or "data" in result.lower()
