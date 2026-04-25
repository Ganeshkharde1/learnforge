"""File and input validators for LearnForge AI."""

from fastapi import HTTPException, UploadFile, status

from app.config import settings

ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
    "text/markdown": ".md",
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def validate_upload_file(file: UploadFile) -> None:
    """Validate uploaded file type and size.

    Raises:
        HTTPException 400 if file type is not allowed.
        HTTPException 413 if file exceeds the size limit.
    """
    # Extension check
    if file.filename:
        ext = "." + file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}",
            )

    # Content-type check
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content type not allowed: {file.content_type}",
        )


def validate_file_size(data: bytes) -> None:
    """Validate that file bytes do not exceed MAX_FILE_SIZE_MB.

    Raises:
        HTTPException 413 if file too large.
    """
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max allowed: {settings.MAX_FILE_SIZE_MB}MB",
        )
