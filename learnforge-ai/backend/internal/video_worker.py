"""Internal video worker — called by Cloud Task to run the full video pipeline.

Route: POST /internal/video/process/{job_id}
Body: {user_id: str, concept: str, depth: str}

This route is NOT mounted under /api/v1 and has no auth middleware.
It should be protected at the infrastructure level (Cloud Tasks OIDC).
"""

import os
import shutil
import tempfile
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.firestore_service import firestore_service
from app.services.gcs_service import gcs_service

logger = structlog.get_logger(__name__)
router = APIRouter()


class VideoProcessRequest(BaseModel):
    user_id: str
    concept: str
    depth: str = "detailed"


@router.post("/video/process/{job_id}")
async def process_video(job_id: str, body: VideoProcessRequest) -> dict:
    """Execute the full video generation pipeline for a queued job.

    Steps:
    1. Generate script (Gemini Pro via ContentAgent)
    2. Build slides (python-pptx → PNG via LibreOffice)
    3. Synthesize audio (Cloud TTS, one MP3 per slide)
    4. Compile MP4 (MoviePy)
    5. Upload MP4 to GCS
    6. Update Firestore job status to 'ready' with signed video URL
    """
    user_id = body.user_id
    concept = body.concept
    depth = body.depth

    def _update_job(status: str, progress: int = 0, **kwargs):
        update_data = {"status": status, "progress": progress, **kwargs}
        firestore_service.update_top_level_user_doc(
            "video_jobs", user_id, job_id, update_data
        )

    _update_job("generating", progress=5)
    tmp_dir = tempfile.mkdtemp(prefix="learnforge_video_")

    try:
        # Step 1: Generate script
        logger.info("Generating video script", job_id=job_id, concept=concept)
        from app.video.script_generator import generate_script
        script = await generate_script(concept=concept, depth=depth)
        _update_job("generating", progress=20)

        slides_data = script.get("slides", [])
        if not slides_data:
            raise RuntimeError("Script returned no slides.")

        # Step 2: Build slide PNGs
        logger.info("Building slides", job_id=job_id)
        slide_dir = os.path.join(tmp_dir, "slides")
        os.makedirs(slide_dir, exist_ok=True)

        from app.video.slide_builder import build_slides
        slide_paths = build_slides(script, slide_dir)
        _update_job("generating", progress=45)

        # Step 3: Synthesize audio
        logger.info("Synthesizing audio", job_id=job_id, slides=len(slides_data))
        audio_dir = os.path.join(tmp_dir, "audio")
        os.makedirs(audio_dir, exist_ok=True)

        from app.video.tts_service import tts_service
        audio_paths = tts_service.synthesize_all_slides(slides_data, audio_dir)
        _update_job("generating", progress=70)

        # Align slide_paths and audio_paths (take the minimum to avoid index errors)
        count = min(len(slide_paths), len(audio_paths))
        slide_paths = slide_paths[:count]
        audio_paths = audio_paths[:count]
        durations = [s.get("duration_seconds", 30) for s in slides_data[:count]]

        # Step 4: Compile MP4
        logger.info("Compiling MP4", job_id=job_id)
        output_mp4 = os.path.join(tmp_dir, "output.mp4")

        from app.video.video_compiler import compile_video
        compile_video(
            slide_paths=slide_paths,
            audio_paths=audio_paths,
            slide_durations=durations,
            output_path=output_mp4,
        )
        _update_job("generating", progress=90)

        # Step 5: Upload MP4 to GCS
        gcs_blob = f"{user_id}/videos/{job_id}.mp4"
        logger.info("Uploading MP4 to GCS", blob=gcs_blob)
        with open(output_mp4, "rb") as f:
            video_bytes = f.read()

        signed_url = gcs_service.upload_bytes(
            video_bytes, gcs_blob, content_type="video/mp4"
        )

        # Step 6: Update Firestore — job ready
        now = datetime.now(tz=timezone.utc).isoformat()
        _update_job(
            "ready",
            progress=100,
            video_url=signed_url,
            completed_at=now,
            gcs_blob=gcs_blob,
        )

        logger.info("Video job completed", job_id=job_id, url=signed_url)
        return {"status": "ready", "video_url": signed_url}

    except Exception as exc:
        logger.error("Video generation failed", job_id=job_id, error=str(exc))
        _update_job("error", progress=0, error_message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video generation failed: {str(exc)}",
        )
    finally:
        # Always clean up temp directory
        shutil.rmtree(tmp_dir, ignore_errors=True)
