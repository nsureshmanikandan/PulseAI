"""PandasAI agent — query a set of DataFrames using natural language."""

import pandas as pd
from typing import Any, Dict

from backend.modules.ai._pandasai_compat import SmartDatalake
from backend.modules.ai.llm_factory import create_llm


def query_datalake(dfs: Dict[str, pd.DataFrame], question: str) -> Any:
    """Run a natural-language question against one or more DataFrames.

    Args:
        dfs: Mapping of name -> DataFrame to query.
        question: Natural-language question to ask.

    Returns:
        The answer produced by the LLM (string, number, or DataFrame).

    Raises:
        ValueError: If no DataFrames are provided.
    """
    if not dfs:
        raise ValueError("No DataFrames provided to query_datalake")

    llm = create_llm()
    lake = SmartDatalake(list(dfs.values()), config={"llm": llm, "verbose": False})
    return lake.chat(question)
