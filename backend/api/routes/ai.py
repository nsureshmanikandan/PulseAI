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
