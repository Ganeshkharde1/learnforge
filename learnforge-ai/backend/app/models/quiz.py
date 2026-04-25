"""Pydantic models for quiz and assessment."""

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    id: str
    type: Literal["mcq", "true_false", "short_answer", "fill_blank", "code_complete"]
    question: str
    options: Optional[list[str]] = None  # MCQ only
    correct_answer: str
    explanation: str
    difficulty: Literal["easy", "medium", "hard"] = "medium"


class Quiz(BaseModel):
    quiz_id: Optional[str] = None
    quiz_title: str
    topic: str
    questions: list[QuizQuestion]
    created_at: Optional[datetime] = None


class GenerateQuizRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=300)
    num_questions: int = Field(5, ge=1, le=20)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    types: list[str] = Field(default_factory=lambda: ["mcq", "short_answer"])
    use_rag: bool = False  # Generate from uploaded docs instead


class SubmitAnswerItem(BaseModel):
    question_id: str
    answer: str


class SubmitQuizRequest(BaseModel):
    quiz_id: str
    answers: list[SubmitAnswerItem]


class AnswerFeedback(BaseModel):
    question_id: str
    correct: bool
    explanation: str
    score: float = Field(ge=0.0, le=1.0)


class QuizSubmitResponse(BaseModel):
    score: float  # 0-100
    total_questions: int
    correct_count: int
    feedback: list[AnswerFeedback]
    weak_areas: list[str]


class QuizHistoryItem(BaseModel):
    quiz_id: str
    topic: str
    score: float
    total_questions: int
    created_at: Optional[datetime]
