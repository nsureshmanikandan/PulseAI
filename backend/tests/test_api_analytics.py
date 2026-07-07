import os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

import uuid
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Use a separate in-memory engine with StaticPool so all connections share same DB
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

from backend.models.db import Base, get_db, Dataset
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


def test_stats_endpoint_404_for_bad_dataset():
    response = client.get("/api/analytics/no-such-id/stats/Sheet1")
    assert response.status_code == 404


def test_chart_bad_type_returns_400():
    ds_id = str(uuid.uuid4())
    with TestSessionLocal() as db:
        db.add(Dataset(id=ds_id, name="test.xlsx", blob_path="fake.xlsx", storage_backend="local", tab_names=["Sheet1"]))
        db.commit()

    mock_df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    with patch("backend.api.routes.analytics.parse_excel", return_value={"Sheet1": mock_df}):
        response = client.post(f"/api/analytics/{ds_id}/chart", json={
            "tab_name": "Sheet1", "chart_type": "radar", "x": "x", "y": "y"
        })
    assert response.status_code == 400
