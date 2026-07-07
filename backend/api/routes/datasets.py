import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.models.db import Dataset, TabProfile, get_db
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


@router.get("/", response_model=List[DatasetOut])
def list_datasets(db: Session = Depends(get_db)):
    return db.query(Dataset).all()


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx and .xls files are supported")

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
    return ds


@router.delete("/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    db.delete(ds)
    db.commit()
