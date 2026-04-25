"""Embedder — batch-embeds chunks using Vertex AI text-embedding-004."""

import structlog

from app.rag.document_processor import Chunk
from app.services.gemini_client import embed_texts

logger = structlog.get_logger(__name__)

# Batch size — Vertex AI text embedding supports up to 250 inputs per call
EMBED_BATCH_SIZE = 100


class Embedder:
    """Converts Chunk objects into embedding vectors via Vertex AI."""

    def embed_chunks(self, chunks: list[Chunk]) -> list[list[float]]:
        """Embed all chunks in batches.

        Args:
            chunks: List of Chunk objects to embed.

        Returns:
            List of embedding vectors (one per chunk, same order).
        """
        if not chunks:
            return []

        all_embeddings: list[list[float]] = []

        for batch_start in range(0, len(chunks), EMBED_BATCH_SIZE):
            batch = chunks[batch_start : batch_start + EMBED_BATCH_SIZE]
            texts = [c.text for c in batch]
            embeddings = embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")
            all_embeddings.extend(embeddings)
            logger.info(
                "Batch embedded",
                batch_start=batch_start,
                batch_size=len(batch),
                total_so_far=len(all_embeddings),
            )

        return all_embeddings

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query string for retrieval.

        Args:
            query: The user's question text.

        Returns:
            Embedding vector.
        """
        from app.services.gemini_client import embed_text

        return embed_text(query, task_type="RETRIEVAL_QUERY")
