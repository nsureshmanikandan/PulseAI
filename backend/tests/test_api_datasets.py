import os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("LOCAL_STORAGE_PATH", "./test_uploads")

import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Use a separate in-memory engine with StaticPool so all connections share same DB
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

from backend.models.db import Base, get_db
Base.metadata.create_all(bind=TEST_ENGINE)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


from backend.main import app
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_list_datasets_empty():
    response = client.get("/api/datasets/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_upload_non_xlsx_rejected():
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test.csv", b"col1,col2\n1,2", "text/csv")},
    )
    assert response.status_code == 400


def test_upload_xlsx_accepted():
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(["revenue", "month"])
    ws.append([100, "Jan"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    with patch("backend.api.routes.datasets.process_upload", return_value={"status": "completed", "tab_count": 1}):
        response = client.post(
            "/api/datasets/upload",
            files={"file": ("sales.xlsx", buf.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_get_nonexistent_dataset():
    response = client.get("/api/datasets/nonexistent-id")
    assert response.status_code == 404
