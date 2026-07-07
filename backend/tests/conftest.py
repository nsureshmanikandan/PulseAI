import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture
def client():
    with patch("backend.models.db.create_tables"):
        from backend.main import app
        return TestClient(app)
