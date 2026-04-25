"""Pydantic models for learning plans."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Resource(BaseModel):
    type: Literal["article", "video", "book", "practice"]
    title: str
    url_hint: str


class Module(BaseModel):
    week: int
    title: str
    description: str
    topics: list[str]
    resources: list[Resource] = Field(default_factory=list)
    milestones: list[str] = Field(default_factory=list)
    estimated_hours: float
    hands_on_project: Optional[str] = None
    completed: bool = False
    completed_at: Optional[datetime] = None


class AssessmentCheckpoint(BaseModel):
    after_week: int
    assessment_type: Literal["quiz", "project", "review"]


class FinalProject(BaseModel):
    title: str
    description: str


class LearningPlan(BaseModel):
    plan_id: Optional[str] = None
    goal: str
    summary: str
    prerequisites: list[str] = Field(default_factory=list)
    duration_weeks: int
    modules: list[Module]
    assessment_checkpoints: list[AssessmentCheckpoint] = Field(default_factory=list)
    final_project: Optional[FinalProject] = None
    status: Literal["active", "completed", "paused"] = "active"
    created_at: Optional[datetime] = None


class GeneratePlanRequest(BaseModel):
    goal: str = Field(..., min_length=5, max_length=500)
    current_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    hours_per_week: float = Field(..., gt=0, le=168)
    duration_weeks: int = Field(..., gt=0, le=52)


class GeneratePlanResponse(BaseModel):
    plan_id: str
    plan: LearningPlan


class UpdateProgressRequest(BaseModel):
    module_index: int = Field(..., ge=0)
    completed: bool
