import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.models.db import Dataset, TabProfile, TabRelationship, get_db
from backend.storage.adapter import save_file
from backend.workers.tasks import process_upload

router = APIRouter()


class DatasetOut(BaseModel):
    id: str
    name: str
    tab_names: Optional[List[str]] = None
    storage_backend: str

    class Config:
        from_attributes = True


def _ensure_tab_names(ds: Dataset) -> Dataset:
    """If tab_names is empty/null, parse the file and backfill the DB."""
    if ds.tab_names:
        return ds
    try:
        from backend.modules.ingestion.parser import parse_excel
        from backend.models.db import SessionLocal
        dfs = parse_excel(ds.blob_path)
        tabs = list(dfs.keys())
        with SessionLocal() as db2:
            row = db2.query(Dataset).filter(Dataset.id == ds.id).first()
            if row:
                row.tab_names = tabs
                db2.commit()
        ds.tab_names = tabs
    except Exception:
        pass
    return ds


@router.get("/", response_model=List[DatasetOut])
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(Dataset).all()
    return [_ensure_tab_names(ds) for ds in datasets]


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(status_code=400, detail="Only .xlsx, .xls, and .csv files are supported")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 50MB limit")

    dataset_id = str(uuid.uuid4())
    file_path = save_file(content, file.filename, dataset_id)

    dataset = Dataset(
        id=dataset_id,
        name=file.filename,
        blob_path=file_path,
        storage_backend="local",
        tab_names=[],
    )
    db.add(dataset)
    db.commit()

    result = process_upload(file_path, dataset_id)

    return {"dataset_id": dataset_id, "status": result.get("status", "completed"), "tab_count": result.get("tab_count", 0)}


@router.get("/{dataset_id}")
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    ds = _ensure_tab_names(ds)
    return {"id": ds.id, "name": ds.name, "tab_names": ds.tab_names or [], "storage_backend": ds.storage_backend}


@router.get("/{dataset_id}/relationships")
def get_relationships(dataset_id: str, db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    rels = db.query(TabRelationship).filter(TabRelationship.dataset_id == dataset_id).all()
    # If no relationships stored yet, run detection now (handles files uploaded before this feature)
    if not rels:
        try:
            import uuid
            from backend.modules.ingestion.parser import parse_excel
            from backend.modules.ingestion.relationship_finder import find_relationships
            dfs = parse_excel(ds.blob_path)
            detected = find_relationships(dfs)
            for rel in detected:
                r = TabRelationship(
                    id=str(uuid.uuid4()),
                    dataset_id=dataset_id,
                    tab_a=rel.get("tab_a", ""),
                    tab_b=rel.get("tab_b", ""),
                    column_a=rel.get("column_a", ""),
                    column_b=rel.get("column_b", ""),
                    confidence=str(rel.get("confidence", "")),
                )
                db.add(r)
            db.commit()
            rels = db.query(TabRelationship).filter(TabRelationship.dataset_id == dataset_id).all()
        except Exception:
            pass
    return [
        {"tab_a": r.tab_a, "column_a": r.column_a, "tab_b": r.tab_b, "column_b": r.column_b, "confidence": r.confidence}
        for r in rels
    ]


@router.delete("/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    db.delete(ds)
    db.commit()
