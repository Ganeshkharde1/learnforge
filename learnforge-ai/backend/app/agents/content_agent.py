"""Content Agent — generates flashcards, summaries, mind maps, and video scripts.

Uses Gemini Flash for all operations (fast, cheap).
Prompts: FLASHCARD_PROMPT, SUMMARIZER_PROMPT, MINDMAP_PROMPT, VIDEO_SCRIPT_PROMPT
all verbatim from MASTER_PLAN Section 10.
"""

import structlog

from app.agents.base_agent import BaseAgent
from app.utils.helpers import truncate_text
from app.utils.prompts import (
    FLASHCARD_PROMPT,
    MINDMAP_PROMPT,
    SUMMARIZER_PROMPT,
    VIDEO_SCRIPT_PROMPT,
)

logger = structlog.get_logger(__name__)


class ContentAgent(BaseAgent):
    """Generates all structured content: flashcards, summaries, mind maps, video scripts."""

    async def generate_flashcards(self, topic: str, num_cards: int = 10) -> dict:
        """Generate a flashcard deck for a topic using Gemini Flash.

        Args:
            topic: The learning topic.
            num_cards: Number of flashcards to generate.

        Returns:
            dict with 'deck_title' and 'cards' list.
        """
        prompt = FLASHCARD_PROMPT.format(num_cards=num_cards, topic=topic)
        logger.info("Generating flashcards", topic=topic, num_cards=num_cards)

        deck = self._generate_json(prompt, use_pro=False)  # Flash
        deck.setdefault("deck_title", f"{topic} Flashcards")
        deck.setdefault("cards", [])

        for i, card in enumerate(deck.get("cards", []), start=1):
            card.setdefault("id", f"card_{i}")
            card.setdefault("difficulty", "medium")
            card.setdefault("tags", [topic])

        return deck

    async def summarize(self, text: str) -> dict:
        """Summarize text and extract key concepts using Gemini Flash.

        Args:
            text: Text to summarize (will be truncated if too long).

        Returns:
            dict with summary, key_concepts, definitions, analogies.
        """
        truncated = truncate_text(text, max_chars=30000)
        prompt = SUMMARIZER_PROMPT.format(text=truncated)
        logger.info("Summarizing text", length=len(text))

        result = self._generate_json(prompt, use_pro=False)  # Flash
        result.setdefault("summary", "")
        result.setdefault("key_concepts", [])
        result.setdefault("definitions", [])
        result.setdefault("analogies", [])

        return result

    async def generate_mindmap(self, topic: str, depth: int = 2) -> dict:
        """Generate a mind map node-edge graph for React Flow.

        Args:
            topic: The topic to map.
            depth: 1=core only, 2=subtopics, 3=detailed.

        Returns:
            dict with 'nodes' and 'edges' lists.
        """
        prompt = MINDMAP_PROMPT.format(topic=topic, depth=depth)
        logger.info("Generating mind map", topic=topic, depth=depth)

        result = self._generate_json(prompt, use_pro=False)  # Flash
        result.setdefault("nodes", [{"id": "1", "label": topic, "level": 0}])
        result.setdefault("edges", [])

        return result

    async def generate_video_script(
        self,
        concept: str,
        level: str = "intermediate",
        duration_minutes: int = 3,
    ) -> dict:
        """Generate a structured video script with slides and narration.

        Args:
            concept: The concept to explain.
            level: Target audience level.
            duration_minutes: Target video duration.

        Returns:
            dict with 'title', 'total_duration_seconds', and 'slides'.
        """
        prompt = VIDEO_SCRIPT_PROMPT.format(
            concept=concept,
            level=level,
            duration_minutes=duration_minutes,
        )
        logger.info(
            "Generating video script",
            concept=concept,
            level=level,
            duration=duration_minutes,
        )

        # Use Pro for video scripts (higher quality narration matters)
        script = self._generate_json(prompt, use_pro=True)
        script.setdefault("title", concept)
        script.setdefault("total_duration_seconds", duration_minutes * 60)
        script.setdefault("slides", [])

        for i, slide in enumerate(script.get("slides", []), start=1):
            slide.setdefault("slide_number", i)
            slide.setdefault("slide_type", "concept")
            slide.setdefault("bullet_points", [])
            slide.setdefault("code_snippet", None)
            slide.setdefault("visual_description", "")
            slide.setdefault("duration_seconds", 30)

        return script
