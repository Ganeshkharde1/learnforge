"""Video router — async video generation via Cloud Tasks.

Rate limit: 5 requests per hour (video generation is expensive).
"""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.dependencies import get_current_user
from app.models.video import (
    GenerateVideoRequest,
    GenerateVideoResponse,
    VideoLibraryItem,
    VideoStatusResponse,
)
from app.services.firestore_service import firestore_service
from app.services.tasks_service import tasks_service
from app.utils.helpers import generate_id

logger = structlog.get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/generate", response_model=GenerateVideoResponse)
@limiter.limit("5/hour")
async def generate_video(
    request: Request,
    body: GenerateVideoRequest,
    user: dict = Depends(get_current_user),
) -> dict:
    """Enqueue an async video generation job.

    Returns a job_id immediately — the actual video is generated in the background.
    Poll /status/{job_id} or listen to Firestore for completion.
    """
    user_id: str = user["uid"]
    job_id = generate_id("job_")
    now = datetime.now(tz=timezone.utc).isoformat()

    job_record = {
        "job_id": job_id,
        "concept": body.concept,
        "depth": body.depth,
        "status": "queued",
        "progress": 0,
        "created_at": now,
        "user_id": user_id,
    }
    firestore_service.set_top_level_user_doc("video_jobs", user_id, job_id, job_record)

    # Enqueue Cloud Task
    tasks_service.enqueue_video_job(
        job_id=job_id,
        user_id=user_id,
        concept=body.concept,
        depth=body.depth,
    )

    logger.info("Video job queued", job_id=job_id, user_id=user_id)
    return {"job_id": job_id, "status": "queued"}


@router.get("/status/{job_id}", response_model=VideoStatusResponse)
async def video_status(
    job_id: str, user: dict = Depends(get_current_user)
) -> dict:
    """Poll the status of a video generation job."""
    user_id: str = user["uid"]
    job = firestore_service.get_top_level_user_doc("video_jobs", user_id, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video job {job_id} not found.",
        )
    return {
        "status": job.get("status", "unknown"),
        "video_url": job.get("video_url"),
        "progress": job.get("progress", 0),
        "error_message": job.get("error_message"),
    }


@router.get("/library", response_model=list[VideoLibraryItem])
async def video_library(user: dict = Depends(get_current_user)) -> list[dict]:
    """List all generated videos for the user."""
    user_id: str = user["uid"]
    docs = firestore_service.list_top_level_user_docs(
        "video_jobs", user_id, order_by="created_at", descending=True
    )
    return [
        {
            "job_id": d.get("job_id", d["id"]),
            "concept": d.get("concept", ""),
            "video_url": d.get("video_url"),
            "status": d.get("status", "unknown"),
            "created_at": d.get("created_at"),
        }
        for d in docs
    ]
