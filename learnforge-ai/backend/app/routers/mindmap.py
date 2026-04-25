"""Mind map router — generate interactive mind map data."""

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()


class MindMapRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=300)
    depth: int = Field(2, ge=1, le=3)


@router.post("/generate")
async def generate_mindmap(
    body: MindMapRequest, user: dict = Depends(get_current_user)
) -> dict:
    """Generate an interactive mind map node-edge graph using Gemini Flash."""
    from app.agents.content_agent import ContentAgent

    agent = ContentAgent()
    return await agent.generate_mindmap(topic=body.topic, depth=body.depth)
