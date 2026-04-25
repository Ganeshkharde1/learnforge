"""Plan router — AI learning plan generation and progress tracking."""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.plan import (
    GeneratePlanRequest,
    GeneratePlanResponse,
    LearningPlan,
    UpdateProgressRequest,
)
from app.services.firestore_service import firestore_service
from app.utils.helpers import generate_id

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/generate", response_model=GeneratePlanResponse)
async def generate_plan(
    body: GeneratePlanRequest, user: dict = Depends(get_current_user)
) -> dict:
    """Generate a structured AI learning plan."""
    from app.agents.planner_agent import PlannerAgent

    user_id: str = user["uid"]
    agent = PlannerAgent()

    plan_data = await agent.generate(
        goal=body.goal,
        current_level=body.current_level,
        hours_per_week=body.hours_per_week,
        duration_weeks=body.duration_weeks,
    )

    plan_id = generate_id("plan_")
    now = datetime.now(tz=timezone.utc).isoformat()
    plan_data["plan_id"] = plan_id
    plan_data["status"] = "active"
    plan_data["created_at"] = now

    firestore_service.set_top_level_user_doc("plans", user_id, plan_id, plan_data)
    logger.info("Plan generated", user_id=user_id, plan_id=plan_id)

    return {"plan_id": plan_id, "plan": plan_data}


@router.get("/", response_model=list[LearningPlan])
async def list_plans(user: dict = Depends(get_current_user)) -> list[dict]:
    """List all learning plans for the authenticated user."""
    user_id: str = user["uid"]
    return firestore_service.list_top_level_user_docs(
        "plans", user_id, order_by="created_at", descending=True
    )


@router.patch("/{plan_id}/progress")
async def update_progress(
    plan_id: str,
    body: UpdateProgressRequest,
    user: dict = Depends(get_current_user),
) -> dict:
    """Mark a module as completed or uncompleted."""
    user_id: str = user["uid"]

    plan = firestore_service.get_top_level_user_doc("plans", user_id, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} not found.",
        )

    modules = plan.get("modules", [])
    if body.module_index >= len(modules):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module index {body.module_index} out of range.",
        )

    modules[body.module_index]["completed"] = body.completed
    if body.completed:
        modules[body.module_index]["completed_at"] = datetime.now(
            tz=timezone.utc
        ).isoformat()

    firestore_service.update_top_level_user_doc(
        "plans", user_id, plan_id, {"modules": modules}
    )
    return {"updated": True}
