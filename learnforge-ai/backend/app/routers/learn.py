"""Learn router — AI tutor chat with SSE streaming.

Rate limit: 30 messages per minute (enforced in this router).
"""

import asyncio
import json
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.dependencies import get_current_user
from app.models.chat import ChatRequest, SessionSummary
from app.services.firestore_service import firestore_service
from app.utils.helpers import generate_id

logger = structlog.get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/chat")
@limiter.limit("30/minute")
async def chat(
    request: Request,
    body: ChatRequest,
    user: dict = Depends(get_current_user),
) -> StreamingResponse:
    """Send a message to the AI tutor and stream the response via SSE.

    Returns a Server-Sent Events stream of text chunks.
    """
    from app.agents.tutor_agent import TutorAgent

    user_id: str = user["uid"]

    # Load or create session
    session = firestore_service.get_top_level_user_doc(
        "sessions", user_id, body.session_id
    )
    if not session:
        session = {
            "session_id": body.session_id,
            "topic": body.topic,
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
            "messages": [],
            "message_count": 0,
        }

    # Load user profile for adaptive tutoring
    profile = firestore_service.get_user_doc(user_id, "profile", "main") or {}
    skill_level = profile.get("skill_level", "beginner")
    weak_topics = profile.get("weak_topics", [])

    history = session.get("messages", [])

    async def event_stream():
        agent = TutorAgent()
        full_response = ""
        try:
            async for chunk in agent.stream_chat(
                message=body.message,
                history=history,
                skill_level=skill_level,
                weak_areas=weak_topics,
                topic=body.topic or session.get("topic", ""),
            ):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            # Persist messages to Firestore after streaming completes
            now = datetime.now(tz=timezone.utc).isoformat()
            history.append({"role": "user", "content": body.message, "timestamp": now})
            history.append(
                {"role": "model", "content": full_response, "timestamp": now}
            )
            session["messages"] = history
            session["message_count"] = len(history)
            if body.topic:
                session["topic"] = body.topic

            firestore_service.set_top_level_user_doc(
                "sessions", user_id, body.session_id, session, merge=True
            )
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as exc:
            logger.error("Tutor streaming failed", error=str(exc), user_id=user_id)
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sessions", response_model=list[SessionSummary])
async def list_sessions(user: dict = Depends(get_current_user)) -> list[dict]:
    """List all chat sessions for the authenticated user."""
    user_id: str = user["uid"]
    docs = firestore_service.list_top_level_user_docs(
        "sessions", user_id, order_by="created_at", descending=True, limit=50
    )
    return [
        {
            "session_id": d.get("session_id", d["id"]),
            "topic": d.get("topic"),
            "created_at": d.get("created_at"),
            "message_count": d.get("message_count", 0),
        }
        for d in docs
    ]


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str, user: dict = Depends(get_current_user)
) -> dict:
    """Delete a specific chat session."""
    user_id: str = user["uid"]
    deleted = firestore_service.delete_top_level_user_doc(
        "sessions", user_id, session_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found.",
        )
    return {"deleted": True}
