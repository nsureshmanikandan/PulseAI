import os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("LOCAL_STORAGE_PATH", "./test_uploads")

# Patch the engine before any app imports so SQLite :memory: uses a single
# shared connection (StaticPool), which is required for in-memory SQLite to
# work correctly across multiple ORM sessions inside the same process.
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from backend.models import db as _db_module

_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_db_module.engine = _test_engine
_db_module.SessionLocal.configure(bind=_test_engine)

from fastapi.testclient import TestClient
from backend.models.db import Base
from backend.main import app

Base.metadata.create_all(bind=_test_engine)
client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"


def test_docs_accessible():
    response = client.get("/docs")
    assert response.status_code == 200


def test_datasets_list_returns_200():
    response = client.get("/api/datasets/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
