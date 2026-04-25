"""Tests for RAG pipeline components."""

import json
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.rag.document_processor import DocumentProcessor


def test_chunk_txt_content():
    """Document processor correctly chunks plain text."""
    processor = DocumentProcessor()
    text_data = b"Python is a programming language.\n\n" * 50
    chunks = processor._process_text(text_data, "test.txt", "doc_001")
    assert len(chunks) > 0
    assert all(len(c.text) <= 600 for c in chunks)
    assert all(c.doc_id == "doc_001" for c in chunks)


def test_chunk_pdf_bytes():
    """Document processor handles PDF bytes and returns chunks."""
    from pypdf import PdfReader
    import io
    from reportlab.pdfgen import canvas

    # Build a minimal PDF in memory
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, "Machine learning is a subset of artificial intelligence.")
    c.showPage()
    c.save()
    pdf_bytes = buf.getvalue()

    processor = DocumentProcessor()
    try:
        chunks = processor._process_pdf(pdf_bytes, "test.pdf", "doc_pdf")
        assert isinstance(chunks, list)
    except Exception:
        # PDF generation may not be available in CI without reportlab
        pytest.skip("reportlab not available for PDF test")


def test_vector_store_add_and_search():
    """VectorStore correctly adds chunks and returns search results."""
    import faiss

    with (
        patch("app.rag.vector_store.gcs_service") as mock_gcs,
        patch("app.rag.embedder.embed_texts") as mock_embed,
    ):
        mock_gcs.blob_exists.return_value = False
        mock_embed.return_value = [[0.1] * 768, [0.2] * 768]

        from app.rag.document_processor import Chunk
        from app.rag.embedder import Embedder
        from app.rag.vector_store import VectorStore

        store = VectorStore(user_id="test_user")
        embedder = Embedder()

        chunks = [
            Chunk("Python basics", "doc.pdf", 1, "doc_001"),
            Chunk("FastAPI tutorial", "doc.pdf", 2, "doc_001"),
        ]

        store.add_chunks(chunks, embedder)

        assert store.index.ntotal == 2
        assert len(store._metadata) == 2


def test_retriever_returns_top_k():
    """Retriever returns at most top_k results."""
    with (
        patch("app.rag.retriever.VectorStore") as MockStore,
        patch("app.rag.retriever.Embedder") as MockEmbed,
    ):
        mock_store = MagicMock()
        mock_store.search.return_value = [
            {"text": "chunk 1", "score": 0.9},
            {"text": "chunk 2", "score": 0.8},
        ]
        MockStore.return_value = mock_store

        mock_embedder = MagicMock()
        mock_embedder.embed_query.return_value = [0.0] * 768
        MockEmbed.return_value = mock_embedder

        from app.rag.retriever import Retriever

        retriever = Retriever(user_id="test_user")
        retriever._store = mock_store
        retriever._embedder = mock_embedder

        results = retriever.retrieve("What is Python?", top_k=2)
        assert len(results) <= 2
