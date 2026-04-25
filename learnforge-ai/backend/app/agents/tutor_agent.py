"""Tutor Agent — conversational, adaptive, streaming AI tutor.

Uses Gemini 1.5 Pro with the TUTOR_SYSTEM_PROMPT verbatim from Section 10.1.
Streams response via async generator for SSE delivery.
"""

import asyncio
from typing import AsyncGenerator

import structlog

from app.agents.base_agent import BaseAgent
from app.utils.helpers import format_conversation_history
from app.utils.prompts import TUTOR_SYSTEM_PROMPT

logger = structlog.get_logger(__name__)


class TutorAgent(BaseAgent):
    """Conversational AI tutor with streaming and adaptive difficulty."""

    async def stream_chat(
        self,
        message: str,
        history: list[dict],
        skill_level: str = "beginner",
        weak_areas: list[str] | None = None,
        topic: str = "",
    ) -> AsyncGenerator[str, None]:
        """Stream a tutor response chunk by chunk.

        Args:
            message: The user's current message.
            history: List of {role, content} message dicts (conversation history).
            skill_level: User's current skill level.
            weak_areas: Topics the user struggles with.
            topic: Current learning topic.

        Yields:
            Text chunks of the streaming response.
        """
        weak_areas_str = ", ".join(weak_areas) if weak_areas else "none identified yet"
        history_str = format_conversation_history(history)

        system_prompt = TUTOR_SYSTEM_PROMPT.format(
            skill_level=skill_level,
            topic=topic or "general learning",
            weak_areas=weak_areas_str,
            conversation_history=history_str,
        )

        full_prompt = f"{system_prompt}\n\nUser: {message}\n\nLearnForge:"

        logger.info(
            "Tutor streaming",
            skill_level=skill_level,
            topic=topic,
            history_len=len(history),
        )

        try:
            # Gemini Vertex AI streaming
            stream = self.llm.generate_content(full_prompt, stream=True)

            for chunk in stream:
                try:
                    text = chunk.text
                    if text:
                        # Yield to async context via asyncio.sleep(0)
                        await asyncio.sleep(0)
                        yield text
                except Exception:
                    # Some chunks may be empty or have no text attribute
                    continue

        except Exception as exc:
            logger.error("Tutor streaming failed", error=str(exc))
            yield f"\n\n[Error: {str(exc)}]"
