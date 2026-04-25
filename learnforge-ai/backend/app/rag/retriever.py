"""Retriever — embeds a query and searches the user's FAISS index."""

import structlog

from app.config import settings
from app.rag.embedder import Embedder
from app.rag.vector_store import VectorStore

logger = structlog.get_logger(__name__)


class Retriever:
    """Retrieves top-k relevant chunks for a query from the user's FAISS index."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self._store: VectorStore | None = None
        self._embedder = Embedder()

    @property
    def store(self) -> VectorStore:
        if self._store is None:
            self._store = VectorStore(user_id=self.user_id)
            self._store.load_from_gcs()
        return self._store

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        doc_ids: list[str] | None = None,
    ) -> list[dict]:
        """Retrieve top-k chunks relevant to the query.

        Args:
            query: User question string.
            top_k: Number of chunks to retrieve (defaults to settings.FAISS_TOP_K).
            doc_ids: Optional list of doc_ids to filter results to specific documents.

        Returns:
            List of chunk metadata dicts with score, text, source, page_num.
        """
        k = top_k or settings.FAISS_TOP_K

        query_vector = self._embedder.embed_query(query)
        results = self.store.search(query_vector, top_k=k * 2)  # over-fetch to allow filtering

        if doc_ids:
            results = [r for r in results if r.get("doc_id") in doc_ids]

        results = results[:k]
        logger.info(
            "Retrieved chunks",
            user_id=self.user_id,
            query_len=len(query),
            results=len(results),
        )
        return results
