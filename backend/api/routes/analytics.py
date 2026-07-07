import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.models.db import Dataset, TabProfile, get_db
from backend.modules.analytics.stats_engine import compute_stats
from backend.modules.analytics.kpi_extractor import extract_kpis
from backend.modules.analytics.chart_builder import build_chart
from backend.modules.ingestion.parser import parse_excel

router = APIRouter()


def _load_tab_df(dataset_id: str, tab_name: str, db: Session):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    dfs = parse_excel(ds.blob_path)
    if tab_name not in dfs:
        raise HTTPException(status_code=404, detail=f"Tab '{tab_name}' not found")
    return dfs[tab_name]


@router.get("/{dataset_id}/stats/{tab_name}")
def get_stats(dataset_id: str, tab_name: str, db: Session = Depends(get_db)):
    df = _load_tab_df(dataset_id, tab_name, db)
    return compute_stats(df)


@router.get("/{dataset_id}/kpis/{tab_name}")
def get_kpis(dataset_id: str, tab_name: str, db: Session = Depends(get_db)):
    df = _load_tab_df(dataset_id, tab_name, db)
    return extract_kpis(df)


class ChartRequest(BaseModel):
    tab_name: str
    chart_type: str
    x: str
    y: Optional[str] = None


@router.post("/{dataset_id}/chart")
def generate_chart(dataset_id: str, req: ChartRequest, db: Session = Depends(get_db)):
    df = _load_tab_df(dataset_id, req.tab_name, db)
    try:
        return build_chart(df, req.chart_type, req.x, req.y)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
