"""Pydantic models for tutor chat sessions."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "model"]
    content: str
    timestamp: Optional[datetime] = None


class ChatSession(BaseModel):
    session_id: str
    topic: Optional[str] = None
    created_at: Optional[datetime] = None
    messages: list[Message] = Field(default_factory=list)
    message_count: int = 0


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=4000)
    topic: Optional[str] = None


class SessionSummary(BaseModel):
    session_id: str
    topic: Optional[str]
    created_at: Optional[datetime]
    message_count: int
