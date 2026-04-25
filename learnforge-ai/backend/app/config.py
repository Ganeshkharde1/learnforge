"""LearnForge AI — Application Configuration.

Reads all environment variables via pydantic-settings.
All values have sensible defaults for local development.
Never hardcode secrets — use .env file or GCP Secret Manager.
"""

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── GCP / Vertex AI ──────────────────────────────────────────────────────────
    GCP_PROJECT_ID: str = "learnforge-dev"
    VERTEX_LOCATION: str = "us-central1"

    # ── Google Application Credentials (ADC for Vertex AI) ─────────────────────
    GOOGLE_APPLICATION_CREDENTIALS: str | None = "./service-account.json"
    GOOGLE_CREDENTIALS_JSON: str | None = None  # For Cloud Run Secrets

    BACKEND_URL: str = "http://localhost:8000"


    TTS_VOICE_NAME: str = "en-US-Wavenet-D"
    TTS_LANGUAGE_CODE: str = "en-US"

    # ── App ────────────────────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    MAX_FILE_SIZE_MB: int = 20
    FAISS_TOP_K: int = 5

    # ── CORS ───────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["*"]

    # ── Gemini model names (Vertex AI) ───────────────────────────────────────────
    MODEL_PRO: str = "gemini-1.5-pro-002"
    MODEL_FLASH: str = "gemini-1.5-flash-002"
    EMBEDDING_MODEL: str = "text-embedding-004"

    # ── Chunk settings ─────────────────────────────────────────────────────────
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64


settings = Settings()

# ── Export Credentials to Environment ─────────────────────────────────────────
# This ensures that Vertex AI and other GCP SDKs find the service account.
if settings.GOOGLE_CREDENTIALS_JSON:
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, 'w') as f:
        f.write(settings.GOOGLE_CREDENTIALS_JSON)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
elif settings.GOOGLE_APPLICATION_CREDENTIALS:
    cred_path = Path(settings.GOOGLE_APPLICATION_CREDENTIALS)
    if not cred_path.is_absolute():
        # Resolve relative to the backend directory (config.py is in backend/app/)
        backend_root = Path(__file__).resolve().parent.parent
        cred_path = backend_root / settings.GOOGLE_APPLICATION_CREDENTIALS
    
    if cred_path.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_path.resolve())
