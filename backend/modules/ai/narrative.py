import pandas as pd
from backend.modules.analytics.kpi_extractor import extract_kpis
from backend.modules.analytics.stats_engine import compute_stats
from backend.modules.ai.llm_factory import create_llm


def generate_narrative(df: pd.DataFrame, dataset_name: str = "Dataset") -> str:
    """Generate a 3-sentence executive narrative using the configured LLM."""
    try:
        llm = create_llm()

        kpis = extract_kpis(df)
        stats = compute_stats(df)

        kpi_summary = "; ".join([f"{k['column']}: sum={k['sum']}, mean={k['mean']}" for k in kpis[:3]])
        outliers = [col for col, s in stats.items() if s.get("has_outliers")]

        prompt = (
            f"You are a data analyst. Write exactly 3 sentences summarizing the dataset '{dataset_name}'. "
            f"Key metrics: {kpi_summary}. "
            f"{'Outliers detected in: ' + ', '.join(outliers) + '.' if outliers else 'No significant outliers.'} "
            "Be concise and executive-friendly."
        )

        result = llm.call([{"role": "user", "content": prompt}])
        return str(result)
    except Exception as exc:
        return f"Unable to generate AI narrative at this time. The data contains {len(df)} rows and {len(df.columns)} columns."
