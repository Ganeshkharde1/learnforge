"""Pytest configuration and shared fixtures for LearnForge AI tests."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def client():
    """FastAPI test client with mocked GCP dependencies."""
    with (
        patch("app.services.gemini_client.vertexai.init"),
        patch("app.services.gemini_client.GenerativeModel"),
        patch("app.services.gemini_client.TextEmbeddingModel"),
        patch("app.services.firestore_service.firestore.Client"),
        patch("app.services.gcs_service.storage.Client"),
    ):
        from main import app
        yield TestClient(app)


@pytest.fixture
def mock_gemini_json():
    """Mock Gemini JSON model response."""
    mock = MagicMock()
    mock.generate_content.return_value.text = '{"result": "mocked"}'
    return mock


@pytest.fixture
def mock_gemini_text():
    """Mock Gemini text model response."""
    mock = MagicMock()
    mock.generate_content.return_value.text = "Mocked text response from Gemini."
    return mock


@pytest.fixture
def sample_chunks():
    """Sample document chunks for testing RAG components."""
    from app.rag.document_processor import Chunk
    return [
        Chunk(
            text="Python is a high-level programming language known for its simplicity.",
            source="test_doc.pdf",
            page_num=1,
            doc_id="doc_test123",
        ),
        Chunk(
            text="FastAPI is a modern, fast web framework for building APIs with Python.",
            source="test_doc.pdf",
            page_num=2,
            doc_id="doc_test123",
        ),
    ]
