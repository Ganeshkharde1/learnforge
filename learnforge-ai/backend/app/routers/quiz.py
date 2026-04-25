"""Quiz router — generate quizzes and submit answers."""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.quiz import (
    GenerateQuizRequest,
    QuizHistoryItem,
    QuizSubmitResponse,
    SubmitQuizRequest,
)
from app.services.firestore_service import firestore_service
from app.utils.helpers import generate_id

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/generate")
async def generate_quiz(
    body: GenerateQuizRequest, user: dict = Depends(get_current_user)
) -> dict:
    """Generate an AI quiz on a topic."""
    from app.agents.assessment_agent import AssessmentAgent

    user_id: str = user["uid"]
    agent = AssessmentAgent()

    quiz_data = await agent.generate_quiz(
        topic=body.topic,
        num_questions=body.num_questions,
        difficulty=body.difficulty,
        question_types=body.types,
    )

    quiz_id = generate_id("quiz_")
    now = datetime.now(tz=timezone.utc).isoformat()
    quiz_data["quiz_id"] = quiz_id
    quiz_data["topic"] = body.topic
    quiz_data["created_at"] = now

    firestore_service.set_top_level_user_doc("quizzes", user_id, quiz_id, quiz_data)
    logger.info("Quiz generated", quiz_id=quiz_id, user_id=user_id, topic=body.topic)

    return {"quiz_id": quiz_id, "questions": quiz_data.get("questions", [])}


@router.post("/submit", response_model=QuizSubmitResponse)
async def submit_quiz(
    body: SubmitQuizRequest, user: dict = Depends(get_current_user)
) -> dict:
    """Submit quiz answers and receive score + feedback."""
    from app.agents.assessment_agent import AssessmentAgent

    user_id: str = user["uid"]

    quiz = firestore_service.get_top_level_user_doc("quizzes", user_id, body.quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz {body.quiz_id} not found.",
        )

    agent = AssessmentAgent()
    result = await agent.evaluate_submission(
        questions=quiz.get("questions", []),
        answers=[a.model_dump() for a in body.answers],
    )

    # Persist score to Firestore
    firestore_service.update_top_level_user_doc(
        "quizzes",
        user_id,
        body.quiz_id,
        {
            "score": result["score"],
            "answers": result["feedback"],
            "submitted_at": datetime.now(tz=timezone.utc).isoformat(),
        },
    )

    # Update weak topics in user profile
    if result.get("weak_areas"):
        profile = firestore_service.get_user_doc(user_id, "profile", "main") or {}
        existing_weak = set(profile.get("weak_topics", []))
        existing_weak.update(result["weak_areas"])
        firestore_service.set_user_doc(
            user_id, "profile", "main", {"weak_topics": list(existing_weak)}, merge=True
        )

    return result


@router.get("/history", response_model=list[QuizHistoryItem])
async def quiz_history(user: dict = Depends(get_current_user)) -> list[dict]:
    """Get the user's past quiz scores."""
    user_id: str = user["uid"]
    docs = firestore_service.list_top_level_user_docs(
        "quizzes", user_id, order_by="created_at", descending=True, limit=50
    )
    return [
        {
            "quiz_id": d.get("quiz_id", d["id"]),
            "topic": d.get("topic", ""),
            "score": d.get("score", 0),
            "total_questions": len(d.get("questions", [])),
            "created_at": d.get("created_at"),
        }
        for d in docs
    ]
