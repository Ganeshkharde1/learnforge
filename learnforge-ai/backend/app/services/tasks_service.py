"""Local Tasks service — enqueue async jobs natively via FastAPI BackgroundTasks/asyncio."""

import asyncio
import json

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)

class LocalTasksService:
    """Local Tasks client for enqueueing async background jobs via asyncio."""

    def __init__(self) -> None:
        pass

    async def _execute_job(self, job_id: str, payload: dict) -> None:
        """Call the internal video worker endpoint using httpx in the background."""
        url = f"{settings.BACKEND_URL}/internal/video/process/{job_id}"
        
        # Small delay to ensure the calling request returns first
        await asyncio.sleep(1)
        
        logger.info("Executing local background job", url=url)
        async with httpx.AsyncClient(timeout=600.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info("Local background job completed", job_id=job_id, status=response.status_code)
            except Exception as e:
                logger.error("Local background job failed", job_id=job_id, error=str(e))

    def enqueue_video_job(
        self, job_id: str, user_id: str, concept: str, depth: str = "detailed"
    ) -> str:
        """Enqueue a video generation job locally using asyncio.create_task."""
        payload = {"user_id": user_id, "concept": concept, "depth": depth}
        
        # Fire and forget
        asyncio.create_task(self._execute_job(job_id, payload))
        
        logger.info(
            "Local video job enqueued",
            job_id=job_id,
            user_id=user_id,
        )
        return f"local-task-{job_id}"

# Keep the same singleton instance name so imports don't break
tasks_service = LocalTasksService()
