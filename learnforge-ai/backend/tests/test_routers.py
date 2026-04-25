"""Tests for API routers using FastAPI TestClient."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _headers(user_id: str = "test_user_123") -> dict:
    return {"X-User-ID": user_id}


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_list_sessions_empty(client):
    with patch(
        "app.services.firestore_service.firestore_service.list_top_level_user_docs",
        return_value=[],
    ):
        resp = client.get("/api/v1/learn/sessions", headers=_headers())
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_plans_empty(client):
    with patch(
        "app.services.firestore_service.firestore_service.list_top_level_user_docs",
        return_value=[],
    ):
        resp = client.get("/api/v1/plan/", headers=_headers())
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_documents_empty(client):
    with patch(
        "app.services.firestore_service.firestore_service.list_top_level_user_docs",
        return_value=[],
    ):
        resp = client.get("/api/v1/rag/documents", headers=_headers())
    assert resp.status_code == 200
    assert resp.json() == []


def test_quiz_history_empty(client):
    with patch(
        "app.services.firestore_service.firestore_service.list_top_level_user_docs",
        return_value=[],
    ):
        resp = client.get("/api/v1/quiz/history", headers=_headers())
    assert resp.status_code == 200
    assert resp.json() == []


def test_video_library_empty(client):
    with patch(
        "app.services.firestore_service.firestore_service.list_top_level_user_docs",
        return_value=[],
    ):
        resp = client.get("/api/v1/video/library", headers=_headers())
    assert resp.status_code == 200
    assert resp.json() == []


def test_progress_overview(client):
    with (
        patch(
            "app.services.firestore_service.firestore_service.get_user_doc",
            return_value={"skill_level": "beginner"},
        ),
        patch(
            "app.services.firestore_service.firestore_service.list_top_level_user_docs",
            return_value=[],
        ),
    ):
        resp = client.get("/api/v1/progress/overview", headers=_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert "total_sessions" in data
    assert "avg_quiz_score" in data


def test_missing_user_id_returns_422(client):
    """Missing X-User-ID header returns 422."""
    resp = client.get("/api/v1/learn/sessions")
    assert resp.status_code == 422
