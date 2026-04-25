"""Abstract base agent — provides Gemini client access and shared error handling."""

import json
import re
from abc import ABC, abstractmethod
from typing import Any

import structlog
from vertexai.generative_models import GenerativeModel

from app.services.gemini_client import llm, llm_flash, llm_json, llm_pro_json

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all LearnForge agents."""

    # Subclasses choose which model to use
    llm: GenerativeModel = llm
    llm_flash: GenerativeModel = llm_flash
    llm_json: GenerativeModel = llm_json
    llm_pro_json: GenerativeModel = llm_pro_json

    def _generate_json(self, prompt: str, use_pro: bool = False) -> dict[str, Any]:
        """Call Gemini and parse the JSON response.

        Args:
            prompt: The full prompt string.
            use_pro: Use Gemini Pro (better quality) instead of Flash.

        Returns:
            Parsed JSON dict.

        Raises:
            ValueError if Gemini does not return valid JSON.
        """
        model = self.llm_pro_json if use_pro else self.llm_json
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
        except Exception as exc:
            logger.error("Gemini generation failed", error=str(exc))
            raise RuntimeError(f"Gemini API error: {exc}") from exc

        # Strip markdown fences if model returns them despite mime type
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.error("JSON parse failed", raw=text[:500], error=str(exc))
            raise ValueError(f"Gemini returned invalid JSON: {exc}") from exc

    def _generate_text(self, prompt: str, use_flash: bool = False) -> str:
        """Call Gemini and return the text response.

        Args:
            prompt: The full prompt string.
            use_flash: Use Gemini Flash (faster/cheaper) instead of Pro.

        Returns:
            Response text string.
        """
        model = self.llm_flash if use_flash else self.llm
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as exc:
            logger.error("Gemini text generation failed", error=str(exc))
            raise RuntimeError(f"Gemini API error: {exc}") from exc
