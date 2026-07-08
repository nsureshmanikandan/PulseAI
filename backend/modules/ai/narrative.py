import pandas as pd
from backend.modules.analytics.kpi_extractor import extract_kpis
from backend.modules.analytics.stats_engine import compute_stats


def _local_narrative(df: pd.DataFrame, dataset_name: str, kpis: list, stats: dict) -> str:
    """Generate a meaningful narrative locally without any LLM call."""
    rows, cols = len(df), len(df.columns)
    parts = [f"The dataset '{dataset_name}' contains {rows:,} records across {cols} columns."]

    # Summarise the most important KPIs
    kpi_lines = []
    for k in kpis[:4]:
        kpi_lines.append(f"{k['label']} is {k['value']}")
    if kpi_lines:
        parts.append("Key metrics: " + ", ".join(kpi_lines) + ".")

    # Outlier summary
    outlier_cols = [col for col, s in stats.items() if s.get("has_outliers")]
    if outlier_cols:
        parts.append(
            f"Statistical outliers detected in {len(outlier_cols)} column(s) "
            f"({', '.join(outlier_cols[:3])}{'…' if len(outlier_cols) > 3 else ''}) "
            "— these may warrant further investigation."
        )
    else:
        parts.append("No significant outliers were detected in the numeric columns.")

    return " ".join(parts)


def generate_narrative(df: pd.DataFrame, dataset_name: str = "Dataset") -> str:
    """Generate a 3-sentence executive narrative using the configured LLM.
    Falls back to a locally-computed narrative if the LLM is unavailable."""
    kpis = extract_kpis(df)
    stats = compute_stats(df)

    # Build kpi summary using new format (id / label / value)
    kpi_summary = "; ".join([f"{k['label']}: {k['value']}" for k in kpis[:4]])
    outliers = [col for col, s in stats.items() if s.get("has_outliers")]

    prompt = (
        f"You are a data analyst. Write exactly 3 sentences summarizing the dataset '{dataset_name}'. "
        f"Key metrics: {kpi_summary}. "
        f"{'Outliers detected in: ' + ', '.join(outliers) + '.' if outliers else 'No significant outliers.'} "
        "Be concise and executive-friendly. Do not use bullet points."
    )

    try:
        from backend.modules.ai.llm_factory import create_llm
        llm = create_llm()
        result = llm.call([{"role": "user", "content": prompt}])
        text = str(result).strip()
        if text:
            return text
    except Exception:
        pass

    # LLM unavailable — return a locally-computed narrative
    return _local_narrative(df, dataset_name, kpis, stats)
