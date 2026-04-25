"""Centralized Gemini client via Vertex AI SDK for LearnForge AI.

Uses `vertexai` (google-cloud-aiplatform) — not the standalone google-generativeai.

Three model objects are exposed:
  llm          — Gemini 1.5 Pro  (complex reasoning: tutor, plan, quiz eval)
  llm_flash    — Gemini 1.5 Flash (fast cheap ops: flashcards, summary, mindmap)
  llm_json     — Gemini 1.5 Flash forced JSON output (all structured outputs)
  llm_pro_json — Gemini 1.5 Pro   forced JSON output (learning plan)

Embedding:
  embed_text(text)      → list[float]
  embed_texts(texts)    → list[list[float]]
"""

from typing import Any

import structlog
import vertexai
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

from app.config import settings

logger = structlog.get_logger(__name__)

# Initialize Vertex AI once at module load
vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.VERTEX_LOCATION)

# Safety settings — block medium and above for all harm categories
_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

# ── Gemini 1.5 Pro — complex reasoning ─────────────────────────────────────
llm = GenerativeModel(
    model_name=settings.MODEL_PRO,
    generation_config=GenerationConfig(
        temperature=0.7,
        top_p=0.95,
        max_output_tokens=8192,
    ),
    safety_settings=_SAFETY_SETTINGS,
)

# ── Gemini 1.5 Flash — fast cheap ops ──────────────────────────────────────
llm_flash = GenerativeModel(
    model_name=settings.MODEL_FLASH,
    generation_config=GenerationConfig(
        temperature=0.5,
        top_p=0.9,
        max_output_tokens=4096,
    ),
    safety_settings=_SAFETY_SETTINGS,
)

# ── Gemini 1.5 Flash — forced JSON output ──────────────────────────────────
llm_json = GenerativeModel(
    model_name=settings.MODEL_FLASH,
    generation_config=GenerationConfig(
        temperature=0.3,
        response_mime_type="application/json",
        max_output_tokens=8192,
    ),
    safety_settings=_SAFETY_SETTINGS,
)

# ── Gemini 1.5 Pro — forced JSON output (complex structured outputs) ────────
llm_pro_json = GenerativeModel(
    model_name=settings.MODEL_PRO,
    generation_config=GenerationConfig(
        temperature=0.4,
        response_mime_type="application/json",
        max_output_tokens=8192,
    ),
    safety_settings=_SAFETY_SETTINGS,
)

# ── Embedding model ─────────────────────────────────────────────────────────
_embedding_model = TextEmbeddingModel.from_pretrained(settings.EMBEDDING_MODEL)


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """Embed a single text string using Vertex AI text embedding.

    Args:
        text: Text to embed.
        task_type: RETRIEVAL_DOCUMENT | RETRIEVAL_QUERY | SEMANTIC_SIMILARITY

    Returns:
        List of floats (768-dim vector).
    """
    inputs = [TextEmbeddingInput(text=text, task_type=task_type)]
    embeddings = _embedding_model.get_embeddings(inputs)
    return embeddings[0].values


def embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Batch embed multiple texts using Vertex AI text embedding.

    Args:
        texts: List of strings.
        task_type: Embedding task type.

    Returns:
        List of embedding vectors.
    """
    if not texts:
        return []
    try:
        inputs = [TextEmbeddingInput(text=t, task_type=task_type) for t in texts]
        # Vertex AI supports batch embedding natively
        embeddings = _embedding_model.get_embeddings(inputs)
        return [e.values for e in embeddings]
    except Exception as exc:
        logger.error("Batch embedding failed", error=str(exc))
        # Fall back to zero vectors to keep FAISS index consistent
        return [[0.0] * 768 for _ in texts]
