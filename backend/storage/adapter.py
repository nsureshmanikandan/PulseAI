import os
from pathlib import Path
from backend.config import Settings


def _get_storage_path() -> Path:
    settings = Settings()
    base = Path(settings.local_storage_path)
    base.mkdir(parents=True, exist_ok=True)
    return base


def save_file(content: bytes, filename: str, dataset_id: str) -> str:
    """Save file bytes to local storage. Returns the file path string."""
    settings = Settings()
    backend = settings.storage_backend.lower()

    if backend == "local":
        dest_dir = _get_storage_path() / dataset_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename
        dest.write_bytes(content)
        return str(dest)

    elif backend in ("azure_blob", "s3"):
        # Placeholder: fall back to local for now until cloud credentials provided
        dest_dir = _get_storage_path() / dataset_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename
        dest.write_bytes(content)
        return str(dest)

    else:
        raise ValueError(f"Unsupported storage backend: {backend}")


def load_file(path: str) -> bytes:
    """Load file bytes from local path."""
    return Path(path).read_bytes()
