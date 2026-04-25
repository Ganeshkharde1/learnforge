"""Video script generator — uses ContentAgent with VIDEO_SCRIPT_PROMPT."""

import structlog

from app.agents.content_agent import ContentAgent

logger = structlog.get_logger(__name__)


async def generate_script(concept: str, depth: str = "detailed") -> dict:
    """Generate a structured video script for a concept.

    Args:
        concept: The educational concept to explain.
        depth: 'brief' (2 min) or 'detailed' (5 min).

    Returns:
        Video script dict with slides.
    """
    duration_minutes = 2 if depth == "brief" else 5
    level = "intermediate"

    agent = ContentAgent()
    script = await agent.generate_video_script(
        concept=concept,
        level=level,
        duration_minutes=duration_minutes,
    )

    logger.info(
        "Video script generated",
        concept=concept,
        slides=len(script.get("slides", [])),
    )
    return script
