from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.models.db import Dataset, get_db
from backend.modules.ai.narrative import generate_narrative
from backend.modules.ai.insight_engine import extract_insights
from backend.modules.ingestion.parser import parse_excel

router = APIRouter()


@router.get("/{dataset_id}/narrative/{tab_name}")
def get_narrative(dataset_id: str, tab_name: str, db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    dfs = parse_excel(ds.blob_path)
    if tab_name not in dfs:
        raise HTTPException(status_code=404, detail=f"Tab '{tab_name}' not found")
    narrative = generate_narrative(dfs[tab_name], dataset_name=f"{ds.name} / {tab_name}")
    return {"narrative": narrative}


@router.get("/{dataset_id}/insights/{tab_name}")
def get_insights(dataset_id: str, tab_name: str, db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    dfs = parse_excel(ds.blob_path)
    if tab_name not in dfs:
        raise HTTPException(status_code=404, detail=f"Tab '{tab_name}' not found")
    return extract_insights(dfs[tab_name])


@router.get("/{dataset_id}/suggested-questions/{tab_name}")
def get_suggested_questions(dataset_id: str, tab_name: str, db: Session = Depends(get_db)):
    """Generate 10 dataset-specific analytical questions using GPT-4o."""
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    dfs = parse_excel(ds.blob_path)
    if tab_name not in dfs:
        raise HTTPException(status_code=404, detail=f"Tab '{tab_name}' not found")

    df = dfs[tab_name]
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    sample = df.head(3).to_csv(index=False)

    prompt = f"""You are a data analyst. Given this dataset, generate exactly 10 specific, insightful questions a business user would want answered.

Dataset name: {ds.name} / {tab_name}
Total rows: {len(df)}
Numeric columns: {', '.join(num_cols) or 'none'}
Categorical columns: {', '.join(cat_cols) or 'none'}
Sample data (first 3 rows):
{sample}

Rules:
- Each question must reference actual column names from the dataset
- Cover ALL of these types — at least one question per type:
  1. Summary stats (total, average, min, max of a numeric column)
  2. Distribution / histogram (how values spread across a numeric column)
  3. Ranking table (top 10 or bottom 10 rows sorted by a column)
  4. Filtered table (show rows where a condition is true, e.g. past_due_days > 0)
  5. Group-by comparison (compare a metric across categories)
  6. Correlation (relationship between two numeric columns)
  7. Outlier detection (which rows have unusually high/low values)
  8. Segment breakdown (count or % split by a categorical column)
  9. Cross-tab / pivot (two categorical columns combined)
  10. Trend or pattern insight (any interesting observation about the data)
- Questions should be directly answerable from the data
- Be specific and actionable, not generic — use real column names
- No numbering, no bullet points — return ONLY the 10 questions, one per line

Return exactly 10 lines, each a complete question."""

    try:
        from backend.modules.ai.llm_factory import AccentureLbpassLLM
        from backend.config import Settings
        llm = AccentureLbpassLLM(Settings())
        raw = llm.chat(prompt)
        questions = [q.strip().lstrip("0123456789.-) ") for q in raw.strip().splitlines() if q.strip()]
        questions = [q for q in questions if len(q) > 10][:10]
        if len(questions) < 5:
            raise ValueError("Too few questions returned")
        return {"questions": questions}
    except Exception:
        # Fallback: schema-driven questions without LLM
        questions = []
        if num_cols:
            questions.append(f"What is the total and average of {num_cols[0]}?")
            questions.append(f"Show me the top 10 rows sorted by {num_cols[0]} descending as a table.")
            questions.append(f"What is the distribution of {num_cols[0]}?")
        if len(num_cols) >= 2:
            questions.append(f"Is there a correlation between {num_cols[0]} and {num_cols[1]}?")
            questions.append(f"Show rows where {num_cols[0]} is above average as a table.")
        if cat_cols:
            questions.append(f"What are the top 5 values in {cat_cols[0]} by count?")
            questions.append(f"How does {num_cols[0] if num_cols else 'count'} vary across {cat_cols[0]} categories?")
            questions.append(f"Show a breakdown table of row counts grouped by {cat_cols[0]}.")
        if len(cat_cols) >= 2:
            questions.append(f"Show a cross-tab of {cat_cols[0]} vs {cat_cols[1]}.")
        questions.append(f"Are there any missing values in this dataset?")
        questions.append(f"What are the outliers in this dataset?")
        questions.append(f"Give me a complete summary of this dataset.")
        return {"questions": questions[:10]}
