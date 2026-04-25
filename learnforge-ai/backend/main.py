"""LearnForge AI — FastAPI Application Entry Point."""

import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings

from app.routers import (
    flashcards,
    learn,
    mindmap,
    plan,
    progress,
    quiz,
    rag,
    summary,
    video,
)
from internal import video_worker

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    logger.info("LearnForge AI starting up", environment=settings.ENVIRONMENT)
    yield
    logger.info("LearnForge AI shutting down")


app = FastAPI(
    title="LearnForge AI API",
    description="Intelligent Learning Companion powered by Gemini and GCP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Attach rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure local storage dir exists and mount it
os.makedirs("data/storage", exist_ok=True)
app.mount("/storage", StaticFiles(directory="data/storage"), name="storage")

# Mount all routers under /api/v1
API_PREFIX = "/api/v1"

app.include_router(learn.router, prefix=f"{API_PREFIX}/learn", tags=["Learn (Tutor)"])
app.include_router(plan.router, prefix=f"{API_PREFIX}/plan", tags=["Learning Plan"])
app.include_router(rag.router, prefix=f"{API_PREFIX}/rag", tags=["RAG (Document Chat)"])
app.include_router(quiz.router, prefix=f"{API_PREFIX}/quiz", tags=["Quiz & Assessment"])
app.include_router(video.router, prefix=f"{API_PREFIX}/video", tags=["Video Generation"])
app.include_router(
    flashcards.router, prefix=f"{API_PREFIX}/flashcards", tags=["Flashcards"]
)
app.include_router(summary.router, prefix=f"{API_PREFIX}/summary", tags=["Summarizer"])
app.include_router(mindmap.router, prefix=f"{API_PREFIX}/mindmap", tags=["Mind Map"])
app.include_router(
    progress.router, prefix=f"{API_PREFIX}/progress", tags=["Progress"]
)

# Internal endpoint for Cloud Tasks (no auth middleware, protected by OIDC at infra level)
app.include_router(video_worker.router, prefix="/internal", tags=["Internal"])


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint for Cloud Run liveness probe."""
    return {"status": "healthy", "service": "learnforge-ai", "version": "1.0.0"}


@app.get("/", tags=["Health"])
async def root() -> dict:
    """Root endpoint — API welcome message."""
    return {
        "message": "Welcome to LearnForge AI API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all exception handler — log and return 500."""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )
