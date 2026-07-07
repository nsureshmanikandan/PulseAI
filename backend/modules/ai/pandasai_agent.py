import pandas as pd
from typing import Dict, Any

try:
    from pandasai import SmartDatalake
except ImportError:
    SmartDatalake = None

from backend.modules.ai.llm_factory import create_llm


def query_datalake(dfs: Dict[str, pd.DataFrame], question: str) -> Any:
    """Run a natural language query across all DataFrames using PandasAI."""
    if not dfs:
        raise ValueError("No DataFrames provided to query_datalake")

    llm = create_llm()
    lake = SmartDatalake(list(dfs.values()), config={"llm": llm, "verbose": False})
    return lake.chat(question)
