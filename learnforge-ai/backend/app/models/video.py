"""Pydantic models for video generation jobs."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Slide(BaseModel):
    slide_number: int
    slide_type: Literal["title", "concept", "example", "code", "summary"]
    title: str
    narration: str
    bullet_points: list[str] = Field(default_factory=list)
    code_snippet: Optional[str] = None
    visual_description: str = ""
    duration_seconds: int = 30


class VideoScript(BaseModel):
    title: str
    total_duration_seconds: int
    slides: list[Slide]


class VideoJob(BaseModel):
    job_id: Optional[str] = None
    concept: str
    depth: Literal["brief", "detailed"] = "detailed"
    status: Literal["queued", "generating", "ready", "error"] = "queued"
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    progress: int = 0  # 0-100
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class GenerateVideoRequest(BaseModel):
    concept: str = Field(..., min_length=3, max_length=300)
    depth: Literal["brief", "detailed"] = "detailed"


class GenerateVideoResponse(BaseModel):
    job_id: str
    status: Literal["queued"] = "queued"


class VideoStatusResponse(BaseModel):
    status: str
    video_url: Optional[str] = None
    progress: int = 0
    error_message: Optional[str] = None


class VideoLibraryItem(BaseModel):
    job_id: str
    concept: str
    video_url: Optional[str]
    status: str
    created_at: Optional[datetime]
