"""RAG Agent — retrieves context from FAISS and answers using Gemini Pro.

Uses RAG_SYSTEM_PROMPT verbatim from MASTER_PLAN Section 10.5.
"""

import structlog

from app.agents.base_agent import BaseAgent
from app.rag.retriever import Retriever
from app.utils.prompts import RAG_SYSTEM_PROMPT

logger = structlog.get_logger(__name__)


class RAGAgent(BaseAgent):
    """Answers questions using retrieved document context."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self._retriever = Retriever(user_id=user_id)

    async def answer(
        self,
        question: str,
        doc_ids: list[str] | None = None,
    ) -> dict:
        """Retrieve relevant chunks and generate a Gemini answer with citations.

        Args:
            question: User's question.
            doc_ids: Optional list of doc_ids to restrict retrieval to.

        Returns:
            dict with 'answer' and 'citations' list.
        """
        # Retrieve top-k chunks
        chunks = self._retriever.retrieve(question, doc_ids=doc_ids)

        if not chunks:
            return {
                "answer": "I couldn't find this in your uploaded documents. Please upload relevant materials first.",
                "citations": [],
            }

        # Format context for the prompt
        context_parts = []
        for i, chunk in enumerate(chunks, start=1):
            source = chunk.get("source_file", "Unknown")
            page = chunk.get("page_num", 1)
            text = chunk.get("text", "")
            context_parts.append(f"[{i}] Source: {source} (page {page})\n{text}")

        context = "\n\n---\n\n".join(context_parts)

        prompt = RAG_SYSTEM_PROMPT.format(context=context, question=question)

        logger.info(
            "RAG answering",
            user_id=self.user_id,
            chunks_retrieved=len(chunks),
            question_len=len(question),
        )

        answer_text = self._generate_text(prompt, use_flash=False)  # Pro for accuracy

        # Build citation list
        citations = [
            {
                "doc_id": chunk.get("doc_id", ""),
                "filename": chunk.get("source_file", ""),
                "chunk_text": chunk.get("text", "")[:200],
                "page": chunk.get("page_num", 1),
                "score": chunk.get("score", 0),
            }
            for chunk in chunks
        ]

        return {"answer": answer_text, "citations": citations}
