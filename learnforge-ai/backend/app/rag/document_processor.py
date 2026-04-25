"""Document processor — parses PDF, DOCX, TXT, and URL into text chunks.

Uses LangChain RecursiveCharacterTextSplitter:
  chunk_size=512, overlap=64  (as per MASTER_PLAN Section 3.1)

Returns list of dicts: {text, source, page_num, doc_id}
"""

import io
import re
from pathlib import Path
from typing import Optional

import structlog
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

logger = structlog.get_logger(__name__)

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)


class Chunk:
    """Represents a single text chunk from a document."""

    __slots__ = ("text", "source", "page_num", "doc_id")

    def __init__(self, text: str, source: str, page_num: int, doc_id: str) -> None:
        self.text = text
        self.source = source
        self.page_num = page_num
        self.doc_id = doc_id

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "source": self.source,
            "page_num": self.page_num,
            "doc_id": self.doc_id,
        }


class DocumentProcessor:
    """Parses documents into Chunk objects ready for embedding."""

    def process_bytes(
        self,
        data: bytes,
        filename: str,
        doc_id: str,
    ) -> list[Chunk]:
        """Route to the correct parser based on file extension.

        Args:
            data: Raw file bytes
            filename: Original filename (used to determine type)
            doc_id: Unique document ID for metadata

        Returns:
            List of Chunk objects.
        """
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            return self._process_pdf(data, filename, doc_id)
        elif ext == ".docx":
            return self._process_docx(data, filename, doc_id)
        elif ext in {".txt", ".md"}:
            return self._process_text(data, filename, doc_id)
        else:
            # Fallback — try treating as UTF-8 text
            logger.warning("Unknown extension, treating as text", ext=ext)
            return self._process_text(data, filename, doc_id)

    def _process_pdf(self, data: bytes, source: str, doc_id: str) -> list[Chunk]:
        """Parse PDF using pypdf, extract text per page, then chunk."""
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        all_chunks: list[Chunk] = []

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = self._clean_text(text)
            if not text.strip():
                continue
            raw_chunks = _splitter.split_text(text)
            for chunk_text in raw_chunks:
                if chunk_text.strip():
                    all_chunks.append(Chunk(
                        text=chunk_text.strip(),
                        source=source,
                        page_num=page_num,
                        doc_id=doc_id,
                    ))

        logger.info("PDF processed", source=source, pages=len(reader.pages), chunks=len(all_chunks))
        return all_chunks

    def _process_docx(self, data: bytes, source: str, doc_id: str) -> list[Chunk]:
        """Parse DOCX using python-docx, extract paragraph text, then chunk."""
        from docx import Document

        doc = Document(io.BytesIO(data))
        full_text = "\n".join(
            para.text for para in doc.paragraphs if para.text.strip()
        )
        full_text = self._clean_text(full_text)
        raw_chunks = _splitter.split_text(full_text)

        chunks = [
            Chunk(text=c.strip(), source=source, page_num=1, doc_id=doc_id)
            for c in raw_chunks
            if c.strip()
        ]
        logger.info("DOCX processed", source=source, chunks=len(chunks))
        return chunks

    def _process_text(self, data: bytes, source: str, doc_id: str) -> list[Chunk]:
        """Parse plain text or markdown file, then chunk."""
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1")

        text = self._clean_text(text)
        raw_chunks = _splitter.split_text(text)

        chunks = [
            Chunk(text=c.strip(), source=source, page_num=1, doc_id=doc_id)
            for c in raw_chunks
            if c.strip()
        ]
        logger.info("Text file processed", source=source, chunks=len(chunks))
        return chunks

    def process_url(self, url: str, doc_id: str) -> list[Chunk]:
        """Scrape a URL and chunk the text content.

        Args:
            url: The URL to scrape
            doc_id: Document ID for metadata

        Returns:
            List of Chunk objects.
        """
        import requests
        from bs4 import BeautifulSoup

        resp = requests.get(url, timeout=15, headers={"User-Agent": "LearnForge/1.0"})
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        text = self._clean_text(text)
        raw_chunks = _splitter.split_text(text)

        chunks = [
            Chunk(text=c.strip(), source=url, page_num=1, doc_id=doc_id)
            for c in raw_chunks
            if c.strip()
        ]
        logger.info("URL processed", url=url, chunks=len(chunks))
        return chunks

    @staticmethod
    def _clean_text(text: str) -> str:
        """Remove excessive whitespace and non-printable characters."""
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        text = re.sub(r"\n{4,}", "\n\n\n", text)
        text = re.sub(r" {3,}", "  ", text)
        return text.strip()
