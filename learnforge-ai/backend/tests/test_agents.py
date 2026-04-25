"""Tests for AI agents."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _mock_json_response(data: dict):
    """Create a mock Gemini response returning JSON."""
    m = MagicMock()
    m.text = json.dumps(data)
    return m


@pytest.mark.asyncio
async def test_planner_agent_returns_valid_plan():
    """PlannerAgent generates a plan with the expected schema."""
    plan_data = {
        "goal": "Learn React",
        "summary": "A plan to learn React in 4 weeks.",
        "prerequisites": ["JavaScript basics"],
        "duration_weeks": 4,
        "modules": [
            {
                "week": i,
                "title": f"Week {i}",
                "description": "desc",
                "topics": ["topic"],
                "resources": [],
                "milestones": [],
                "estimated_hours": 10,
                "hands_on_project": None,
            }
            for i in range(1, 5)
        ],
        "assessment_checkpoints": [],
        "final_project": {"title": "Todo App", "description": "Build a todo app"},
    }

    with patch("app.agents.base_agent.BaseAgent._generate_json", return_value=plan_data):
        from app.agents.planner_agent import PlannerAgent

        agent = PlannerAgent()
        result = await agent.generate(
            goal="Learn React",
            current_level="beginner",
            hours_per_week=10,
            duration_weeks=4,
        )

    assert "modules" in result
    assert len(result["modules"]) == 4
    assert result["goal"] == "Learn React"


@pytest.mark.asyncio
async def test_assessment_agent_generates_quiz():
    """AssessmentAgent generates a quiz with the correct number of questions."""
    quiz_data = {
        "quiz_title": "Python Basics Quiz",
        "questions": [
            {
                "id": f"q{i}",
                "type": "mcq",
                "question": f"Question {i}?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Because A",
                "difficulty": "medium",
            }
            for i in range(1, 6)
        ],
    }

    with patch("app.agents.base_agent.BaseAgent._generate_json", return_value=quiz_data):
        from app.agents.assessment_agent import AssessmentAgent

        agent = AssessmentAgent()
        result = await agent.generate_quiz(topic="Python basics", num_questions=5)

    assert len(result["questions"]) == 5


@pytest.mark.asyncio
async def test_assessment_agent_evaluates_mcq():
    """AssessmentAgent correctly evaluates MCQ answers without Gemini call."""
    from app.agents.assessment_agent import AssessmentAgent

    agent = AssessmentAgent()
    questions = [
        {
            "id": "q1",
            "type": "mcq",
            "question": "What is Python?",
            "options": ["A language", "A snake", "A DB", "A framework"],
            "correct_answer": "A language",
            "explanation": "Python is a programming language",
        }
    ]
    answers = [{"question_id": "q1", "answer": "A language"}]
    result = await agent.evaluate_submission(questions=questions, answers=answers)

    assert result["score"] == 100.0
    assert result["correct_count"] == 1


@pytest.mark.asyncio
async def test_content_agent_generates_flashcards():
    """ContentAgent generates flashcards with the correct structure."""
    deck_data = {
        "deck_title": "Python Flashcards",
        "cards": [
            {"id": f"card_{i}", "front": f"Q{i}", "back": f"A{i}", "difficulty": "medium", "tags": ["python"]}
            for i in range(1, 6)
        ],
    }

    with patch("app.agents.base_agent.BaseAgent._generate_json", return_value=deck_data):
        from app.agents.content_agent import ContentAgent

        agent = ContentAgent()
        result = await agent.generate_flashcards(topic="Python", num_cards=5)

    assert len(result["cards"]) == 5
    assert result["deck_title"] == "Python Flashcards"
