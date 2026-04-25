"""Local File Storage service replacing GCS for LearnForge AI."""

import os
import shutil
import tempfile
from pathlib import Path

import structlog

from app.config import settings

logger = structlog.get_logger(__name__)

STORAGE_DIR = Path("data/storage")

class LocalStorageService:
    """Local filesystem operations scoped to data/storage directory."""

    def __init__(self) -> None:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_path(self, dest_blob: str) -> Path:
        path = STORAGE_DIR / dest_blob
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def upload_file(self, source_path: str | Path, dest_blob: str) -> str:
        dest_path = self._get_path(dest_blob)
        shutil.copy2(source_path, dest_path)
        logger.info("File saved locally", path=str(dest_path))
        return f"local://{dest_blob}"

    def upload_bytes(
        self,
        data: bytes,
        dest_blob: str,
        content_type: str = "application/octet-stream",
        signed_url_expiry_seconds: int = 604800,
    ) -> str:
        dest_path = self._get_path(dest_blob)
        dest_path.write_bytes(data)
        logger.info("Bytes saved locally", path=str(dest_path), size=len(data))
        return self.get_signed_url(dest_blob)

    def download_bytes(self, blob_name: str) -> bytes:
        file_path = self._get_path(blob_name)
        if not file_path.exists():
            raise FileNotFoundError(f"Local blob not found: {blob_name}")
        return file_path.read_bytes()

    def download_to_temp_file(self, blob_name: str, suffix: str = "") -> str:
        data = self.download_bytes(blob_name)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(data)
        tmp.flush()
        tmp.close()
        return tmp.name

    def blob_exists(self, blob_name: str) -> bool:
        return self._get_path(blob_name).exists()

    def delete_blob(self, blob_name: str) -> bool:
        file_path = self._get_path(blob_name)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def list_blobs_with_prefix(self, prefix: str) -> list[str]:
        prefix_path = STORAGE_DIR / prefix
        if not prefix_path.parent.exists():
            return []
        
        # Simple prefix matching
        blobs = []
        for root, _, files in os.walk(STORAGE_DIR):
            for file in files:
                rel_path = Path(root) / file
                rel_str = str(rel_path.relative_to(STORAGE_DIR)).replace('\\', '/')
                if rel_str.startswith(prefix):
                    blobs.append(rel_str)
        return blobs

    def get_signed_url(self, blob_name: str, expiry_seconds: int = 604800) -> str:
        # For local dev, we just serve via a mounted static directory in FastAPI
        # e.g., http://localhost:8000/storage/blob_name
        base = settings.BACKEND_URL.rstrip('/')
        return f"{base}/storage/{blob_name}"

# Keep the same singleton instance name so imports don't break
gcs_service = LocalStorageService()
