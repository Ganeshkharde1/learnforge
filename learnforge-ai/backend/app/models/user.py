"""Pydantic models for user and profile data."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class UserProfile(BaseModel):
    skill_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    mastered_topics: list[str] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)
    total_sessions: int = 0
    study_streak: int = 0
    last_active: Optional[datetime] = None


class User(BaseModel):
    uid: str
    email: str
    display_name: Optional[str] = None
    created_at: Optional[datetime] = None
    profile: UserProfile = Field(default_factory=UserProfile)


class UpdateProfileRequest(BaseModel):
    skill_level: Optional[Literal["beginner", "intermediate", "advanced"]] = None
    mastered_topics: Optional[list[str]] = None
    weak_topics: Optional[list[str]] = None
