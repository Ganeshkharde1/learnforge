"""Orchestrator Agent — classifies user intent and routes to the correct sub-agent.

Uses ORCHESTRATOR_PROMPT (Flash, fast classification).
"""

import structlog

from app.agents.base_agent import BaseAgent
from app.utils.prompts import ORCHESTRATOR_PROMPT

logger = structlog.get_logger(__name__)

VALID_INTENTS = {
    "tutor", "quiz", "plan", "rag", "flashcard", "summary", "mindmap", "video"
}


class OrchestratorAgent(BaseAgent):
    """Routes user messages to the appropriate sub-agent."""

    async def classify_intent(self, message: str) -> dict:
        """Classify the user's intent from a natural-language message.

        Args:
            message: The user's raw input.

        Returns:
            dict with 'intent', 'confidence', and 'extracted_topic'.
        """
        prompt = ORCHESTRATOR_PROMPT.format(message=message)

        try:
            result = self._generate_json(prompt, use_pro=False)  # Flash — fast
        except Exception as exc:
            logger.warning("Intent classification failed, defaulting to tutor", error=str(exc))
            return {"intent": "tutor", "confidence": 0.5, "extracted_topic": None}

        intent = result.get("intent", "tutor")
        if intent not in VALID_INTENTS:
            logger.warning("Unknown intent returned", intent=intent)
            intent = "tutor"

        return {
            "intent": intent,
            "confidence": result.get("confidence", 0.8),
            "extracted_topic": result.get("extracted_topic"),
        }

    async def route(self, message: str, user_id: str, **kwargs) -> dict:
        """Classify intent and call the appropriate agent method.

        Args:
            message: User message.
            user_id: Authenticated user ID.
            **kwargs: Additional context (topic, history, etc.)

        Returns:
            Agent response dict.
        """
        classification = await self.classify_intent(message)
        intent = classification["intent"]
        topic = classification.get("extracted_topic") or kwargs.get("topic", "")

        logger.info(
            "Orchestrator routing",
            intent=intent,
            confidence=classification["confidence"],
            user_id=user_id,
        )

        if intent == "plan":
            from app.agents.planner_agent import PlannerAgent
            agent = PlannerAgent()
            return {
                "intent": intent,
                "message": "I'll generate a learning plan. Please use the Plan Generator page for the full experience.",
                "redirect": "/plan",
            }

        if intent == "quiz":
            return {
                "intent": intent,
                "message": f"I'll create a quiz on {topic}. Head to the Quiz page to begin.",
                "redirect": "/quiz",
            }

        if intent == "video":
            return {
                "intent": intent,
                "message": f"I'll generate a video explaining {topic}. Visit the Video Generator page.",
                "redirect": "/video",
            }

        if intent == "rag":
            return {
                "intent": intent,
                "message": "To ask about your documents, please use the RAG Chat page.",
                "redirect": "/rag",
            }

        # Default: tutor handles it
        from app.agents.tutor_agent import TutorAgent
        agent = TutorAgent()
        # Non-streaming single response for orchestrator use
        from app.services.gemini_client import llm
        from app.utils.helpers import format_conversation_history
        from app.utils.prompts import TUTOR_SYSTEM_PROMPT

        history = kwargs.get("history", [])
        skill_level = kwargs.get("skill_level", "beginner")
        weak_areas = kwargs.get("weak_areas", [])

        full_chunks = []
        async for chunk in agent.stream_chat(
            message=message,
            history=history,
            skill_level=skill_level,
            weak_areas=weak_areas,
            topic=topic,
        ):
            full_chunks.append(chunk)

        return {"intent": "tutor", "response": "".join(full_chunks)}
