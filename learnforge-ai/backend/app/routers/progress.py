"""Progress router — user learning analytics and weak area detection."""

import structlog
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.services.firestore_service import firestore_service

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/overview")
async def progress_overview(user: dict = Depends(get_current_user)) -> dict:
    """Return aggregated learning stats for the user dashboard."""
    user_id: str = user["uid"]

    profile = firestore_service.get_user_doc(user_id, "profile", "main") or {}
    plans = firestore_service.list_top_level_user_docs("plans", user_id, limit=100)
    sessions = firestore_service.list_top_level_user_docs("sessions", user_id, limit=100)
    quizzes = firestore_service.list_top_level_user_docs("quizzes", user_id, limit=100)

    # Count completed modules across all plans
    total_modules = sum(len(p.get("modules", [])) for p in plans)
    completed_modules = sum(
        sum(1 for m in p.get("modules", []) if m.get("completed")) for p in plans
    )

    # Average quiz score
    scores = [q.get("score", 0) for q in quizzes if q.get("score") is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    active_plans = sum(1 for p in plans if p.get("status") == "active")

    return {
        "total_sessions": len(sessions),
        "topics_covered": len(profile.get("mastered_topics", [])),
        "avg_quiz_score": avg_score,
        "study_streak": profile.get("study_streak", 0),
        "plans_active": active_plans,
        "total_modules": total_modules,
        "completed_modules": completed_modules,
        "completion_pct": (
            round(completed_modules / total_modules * 100, 1) if total_modules else 0
        ),
    }


@router.get("/weak-areas")
async def weak_areas(user: dict = Depends(get_current_user)) -> list[dict]:
    """Return topics where the user consistently scores below 60%."""
    user_id: str = user["uid"]

    quizzes = firestore_service.list_top_level_user_docs("quizzes", user_id, limit=200)
    profile = firestore_service.get_user_doc(user_id, "profile", "main") or {}

    # Aggregate per-topic scores
    topic_scores: dict[str, list[float]] = {}
    topic_dates: dict[str, str] = {}
    for q in quizzes:
        topic = q.get("topic", "")
        score = q.get("score")
        if topic and score is not None:
            topic_scores.setdefault(topic, []).append(score)
            if q.get("created_at"):
                topic_dates[topic] = q["created_at"]

    weak = []
    for topic, scores in topic_scores.items():
        avg = sum(scores) / len(scores)
        if avg < 60:
            weak.append(
                {
                    "topic": topic,
                    "avg_score": round(avg, 1),
                    "last_tested": topic_dates.get(topic),
                    "recommended_resources": [
                        f"Review {topic} fundamentals",
                        f"Practice {topic} exercises",
                    ],
                }
            )

    # Also include profile-flagged weak topics
    for t in profile.get("weak_topics", []):
        if not any(w["topic"] == t for w in weak):
            weak.append(
                {
                    "topic": t,
                    "avg_score": None,
                    "last_tested": None,
                    "recommended_resources": [f"Review {t} basics"],
                }
            )

    return sorted(weak, key=lambda x: (x["avg_score"] or 0))
