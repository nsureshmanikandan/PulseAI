import os
import tempfile
import pytest
from pathlib import Path


def test_local_save_and_load(tmp_path):
    with __import__('unittest.mock', fromlist=['patch']).patch.dict(os.environ, {
        "STORAGE_BACKEND": "local",
        "LOCAL_STORAGE_PATH": str(tmp_path),
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/0",
    }):
        from backend.storage.adapter import save_file, load_file
        content = b"test excel content"
        path = save_file(content, "test.xlsx", "dataset-123")
        loaded = load_file(path)
        assert loaded == content


def test_save_returns_path_string(tmp_path):
    with __import__('unittest.mock', fromlist=['patch']).patch.dict(os.environ, {
        "STORAGE_BACKEND": "local",
        "LOCAL_STORAGE_PATH": str(tmp_path),
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/0",
    }):
        from backend.storage.adapter import save_file
        path = save_file(b"data", "myfile.xlsx", "ds-456")
        assert isinstance(path, str)
        assert "myfile.xlsx" in path
