import pandas as pd
from itertools import combinations
from typing import Dict, List


def find_relationships(dfs: Dict[str, pd.DataFrame]) -> List[dict]:
    """Detect potential join columns between DataFrame pairs by matching column names."""
    relationships = []
    tab_pairs = list(combinations(dfs.keys(), 2))
    for tab_a, tab_b in tab_pairs:
        cols_a = set(dfs[tab_a].columns)
        cols_b = set(dfs[tab_b].columns)
        shared = cols_a & cols_b
        for col in shared:
            series_a = dfs[tab_a][col].dropna()
            series_b = dfs[tab_b][col].dropna()
            overlap = len(set(series_a) & set(series_b))
            if overlap > 0:
                confidence = "high" if overlap / max(len(set(series_a)), 1) > 0.5 else "low"
                relationships.append({
                    "tab_a": tab_a,
                    "tab_b": tab_b,
                    "column_a": col,
                    "column_b": col,
                    "confidence": confidence,
                })
    return relationships
