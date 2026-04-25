"""Planner Agent — generates structured week-by-week learning plans.

Uses Gemini 1.5 Pro with JSON output and the PLANNER_PROMPT verbatim
from MASTER_PLAN Section 10.2.
"""

import structlog

from app.agents.base_agent import BaseAgent
from app.utils.prompts import PLANNER_PROMPT

logger = structlog.get_logger(__name__)


class PlannerAgent(BaseAgent):
    """Generates structured learning plans from a user goal."""

    async def generate(
        self,
        goal: str,
        current_level: str,
        hours_per_week: float,
        duration_weeks: int,
    ) -> dict:
        """Generate a full structured learning plan.

        Args:
            goal: What the user wants to learn.
            current_level: beginner | intermediate | advanced
            hours_per_week: Available study hours per week.
            duration_weeks: How many weeks to plan for.

        Returns:
            Parsed plan dict matching the Section 3.2 schema.
        """
        prompt = PLANNER_PROMPT.format(
            goal=goal,
            current_level=current_level,
            hours_per_week=hours_per_week,
            duration_weeks=duration_weeks,
        )

        logger.info(
            "Generating learning plan",
            goal=goal,
            level=current_level,
            weeks=duration_weeks,
        )

        # Use Pro for complex reasoning, JSON output
        plan = self._generate_json(prompt, use_pro=True)

        # Validate and ensure required fields exist
        plan.setdefault("goal", goal)
        plan.setdefault("summary", "")
        plan.setdefault("prerequisites", [])
        plan.setdefault("duration_weeks", duration_weeks)
        plan.setdefault("modules", [])
        plan.setdefault("assessment_checkpoints", [])
        plan.setdefault("final_project", None)

        # Ensure each module has 'completed' field for progress tracking
        for module in plan.get("modules", []):
            module.setdefault("completed", False)
            module.setdefault("completed_at", None)
            module.setdefault("hands_on_project", None)
            module.setdefault("resources", [])
            module.setdefault("milestones", [])

        logger.info("Plan generated", goal=goal, modules=len(plan.get("modules", [])))
        return plan
