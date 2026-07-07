import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Provide a valid SQLite URL so db.py can call create_engine at import time
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture
def client():
    with patch("backend.models.db.create_tables"):
        from backend.main import app
        return TestClient(app)
