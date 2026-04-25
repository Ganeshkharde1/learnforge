"""FAISS vector store — per-user index persisted to GCS.

Index type: IndexFlatIP (inner product / cosine similarity)
Per-user namespace: {user_id}/index.faiss and {user_id}/metadata.json

Each entry in metadata.json:
  {chunk_id, source_file, page_num, text, doc_id}
"""

import json
import os
import tempfile
from typing import Optional

import numpy as np
import structlog
import faiss

from app.rag.document_processor import Chunk
from app.rag.embedder import Embedder
from app.services.gcs_service import gcs_service

logger = structlog.get_logger(__name__)

EMBEDDING_DIM = 768  # text-embedding-004 output size


class VectorStore:
    """Per-user FAISS IndexFlatIP vector store with GCS persistence."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self._index: Optional[faiss.Index] = None
        self._metadata: list[dict] = []

        # GCS blob paths
        self._index_blob = f"{user_id}/index.faiss"
        self._metadata_blob = f"{user_id}/metadata.json"

    @property
    def index(self) -> faiss.Index:
        """Lazy-create FAISS index if not loaded."""
        if self._index is None:
            self._index = faiss.IndexFlatIP(EMBEDDING_DIM)
        return self._index

    def add_chunks(self, chunks: list[Chunk], embedder: Embedder) -> None:
        """Embed chunks and add them to the FAISS index.

        Args:
            chunks: List of Chunk objects to add.
            embedder: Embedder instance to generate vectors.
        """
        if not chunks:
            return

        vectors = embedder.embed_chunks(chunks)
        matrix = np.array(vectors, dtype=np.float32)

        # Normalize for cosine similarity with IndexFlatIP
        faiss.normalize_L2(matrix)

        start_id = len(self._metadata)
        self.index.add(matrix)

        for i, chunk in enumerate(chunks):
            self._metadata.append({
                "chunk_id": start_id + i,
                "source_file": chunk.source,
                "page_num": chunk.page_num,
                "text": chunk.text,
                "doc_id": chunk.doc_id,
            })

        logger.info(
            "Chunks added to FAISS index",
            user_id=self.user_id,
            added=len(chunks),
            total=self.index.ntotal,
        )

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        """Search the index for the most similar chunks.

        Args:
            query_vector: Embedding of the query.
            top_k: Number of results to return.

        Returns:
            List of metadata dicts for the top-k closest chunks.
        """
        if self.index.ntotal == 0:
            return []

        matrix = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(matrix)

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(matrix, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            meta = self._metadata[idx].copy()
            meta["score"] = float(score)
            results.append(meta)

        return results

    def save_to_gcs(self) -> None:
        """Serialize and upload the FAISS index and metadata to GCS."""
        if self.index.ntotal == 0:
            logger.warning("Skipping save — FAISS index is empty", user_id=self.user_id)
            return

        # Write index to temp file then upload
        with tempfile.NamedTemporaryFile(suffix=".faiss", delete=False) as tmp:
            faiss.write_index(self.index, tmp.name)
            with open(tmp.name, "rb") as f:
                index_bytes = f.read()
            os.unlink(tmp.name)

        gcs_service.upload_bytes(
            index_bytes, self._index_blob, content_type="application/octet-stream"
        )

        # Upload metadata JSON
        metadata_bytes = json.dumps(self._metadata).encode("utf-8")
        gcs_service.upload_bytes(
            metadata_bytes, self._metadata_blob, content_type="application/json"
        )

        logger.info(
            "FAISS index saved to GCS",
            user_id=self.user_id,
            vectors=self.index.ntotal,
        )

    def load_from_gcs(self) -> bool:
        """Download and deserialize the FAISS index from GCS.

        Returns:
            True if loaded successfully, False if no index exists yet.
        """
        if not gcs_service.blob_exists(self._index_blob):
            logger.info("No existing FAISS index in GCS", user_id=self.user_id)
            return False

        try:
            # Download index
            index_path = gcs_service.download_to_temp_file(self._index_blob, suffix=".faiss")
            self._index = faiss.read_index(index_path)
            os.unlink(index_path)

            # Download metadata
            metadata_bytes = gcs_service.download_bytes(self._metadata_blob)
            self._metadata = json.loads(metadata_bytes.decode("utf-8"))

            logger.info(
                "FAISS index loaded from GCS",
                user_id=self.user_id,
                vectors=self._index.ntotal,
            )
            return True
        except Exception as exc:
            logger.error("Failed to load FAISS index", error=str(exc), user_id=self.user_id)
            self._index = None
            self._metadata = []
            return False

    def remove_doc_chunks(self, doc_id: str) -> int:
        """Remove all chunks belonging to a specific document.

        Since FAISS IndexFlatIP doesn't support in-place deletion, this
        rebuilds the index from the remaining chunks (re-embeds metadata only).

        Args:
            doc_id: Document ID whose chunks should be removed.

        Returns:
            Number of chunks removed.
        """
        remaining = [m for m in self._metadata if m.get("doc_id") != doc_id]
        removed_count = len(self._metadata) - len(remaining)

        if removed_count == 0:
            return 0

        # Rebuild index from remaining metadata (vectors must be re-fetched)
        # We store the text in metadata so we can re-embed
        from app.rag.embedder import Embedder

        self._index = faiss.IndexFlatIP(EMBEDDING_DIM)
        self._metadata = []

        if remaining:
            embedder = Embedder()
            texts = [m["text"] for m in remaining]
            vectors = embedder.embed_texts_raw(texts)
            matrix = np.array(vectors, dtype=np.float32)
            faiss.normalize_L2(matrix)
            self._index.add(matrix)

            for i, meta in enumerate(remaining):
                meta["chunk_id"] = i
                self._metadata.append(meta)

        logger.info(
            "Rebuilt FAISS index after deletion",
            doc_id=doc_id,
            removed=removed_count,
            remaining=len(self._metadata),
        )
        return removed_count
