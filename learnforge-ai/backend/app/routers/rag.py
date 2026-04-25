"""RAG router — document upload, querying, and management."""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.services.firestore_service import firestore_service
from app.services.gcs_service import gcs_service
from app.utils.helpers import generate_id, sanitize_filename
from app.utils.validators import validate_file_size, validate_upload_file

logger = structlog.get_logger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    doc_ids: list[str] | None = None


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    status: str
    uploaded_at: str | None
    chunk_count: int


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
) -> dict:
    """Upload a document, chunk it, embed it, and store in the user's FAISS index."""
    from app.rag.document_processor import DocumentProcessor
    from app.rag.embedder import Embedder
    from app.rag.vector_store import VectorStore

    user_id: str = user["uid"]

    validate_upload_file(file)
    data = await file.read()
    validate_file_size(data)

    doc_id = generate_id("doc_")
    safe_name = sanitize_filename(file.filename or "upload.txt")
    gcs_path = f"{user_id}/documents/{doc_id}/{safe_name}"

    # Upload raw file to GCS
    gcs_service.upload_bytes(data, gcs_path, content_type=file.content_type or "application/octet-stream")

    # Record document in Firestore with "processing" status
    now = datetime.now(tz=timezone.utc).isoformat()
    doc_record = {
        "doc_id": doc_id,
        "filename": file.filename,
        "gcs_path": gcs_path,
        "faiss_index_path": f"{user_id}/index.faiss",
        "uploaded_at": now,
        "chunk_count": 0,
        "status": "processing",
    }
    firestore_service.set_top_level_user_doc("documents", user_id, doc_id, doc_record)

    try:
        # Process document into chunks
        processor = DocumentProcessor()
        chunks = processor.process_bytes(
            data=data,
            filename=file.filename or "upload.txt",
            doc_id=doc_id,
        )

        # Embed and store in FAISS
        embedder = Embedder()
        store = VectorStore(user_id=user_id)
        store.load_from_gcs()  # load existing index (if any)
        store.add_chunks(chunks, embedder=embedder)
        store.save_to_gcs()

        # Update Firestore record
        firestore_service.update_top_level_user_doc(
            "documents",
            user_id,
            doc_id,
            {"status": "ready", "chunk_count": len(chunks)},
        )
        logger.info("Document processed", doc_id=doc_id, chunks=len(chunks))
    except Exception as exc:
        logger.error("Document processing failed", doc_id=doc_id, error=str(exc))
        firestore_service.update_top_level_user_doc(
            "documents", user_id, doc_id, {"status": "error"}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(exc)}",
        )

    return {"doc_id": doc_id, "status": "ready", "chunk_count": len(chunks)}


@router.post("/query")
async def query_documents(
    body: QueryRequest,
    user: dict = Depends(get_current_user),
) -> dict:
    """Answer a question using the user's uploaded documents (RAG)."""
    from app.agents.rag_agent import RAGAgent

    user_id: str = user["uid"]
    agent = RAGAgent(user_id=user_id)
    result = await agent.answer(question=body.question, doc_ids=body.doc_ids)
    return result


@router.get("/documents", response_model=list[DocumentInfo])
async def list_documents(user: dict = Depends(get_current_user)) -> list[dict]:
    """List all documents uploaded by the user."""
    user_id: str = user["uid"]
    docs = firestore_service.list_top_level_user_docs(
        "documents", user_id, order_by="uploaded_at", descending=True
    )
    return [
        {
            "doc_id": d.get("doc_id", d["id"]),
            "filename": d.get("filename", ""),
            "status": d.get("status", "unknown"),
            "uploaded_at": d.get("uploaded_at"),
            "chunk_count": d.get("chunk_count", 0),
        }
        for d in docs
    ]


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str, user: dict = Depends(get_current_user)
) -> dict:
    """Delete a document and remove it from the FAISS index."""
    user_id: str = user["uid"]

    doc = firestore_service.get_top_level_user_doc("documents", user_id, doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found.",
        )

    # Delete raw file from GCS
    gcs_path = doc.get("gcs_path", "")
    if gcs_path:
        gcs_service.delete_blob(gcs_path)

    # Remove from Firestore
    firestore_service.delete_top_level_user_doc("documents", user_id, doc_id)

    logger.info("Document deleted", doc_id=doc_id, user_id=user_id)
    return {"deleted": True}
