"""Summary router — summarize text or URL content."""

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, HttpUrl

from app.auth.dependencies import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()


class SummarizeTextRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=50000)


class SummarizeUrlRequest(BaseModel):
    url: str = Field(..., min_length=5)


@router.post("/text")
async def summarize_text(
    body: SummarizeTextRequest, user: dict = Depends(get_current_user)
) -> dict:
    """Summarize a text passage using Gemini Flash."""
    from app.agents.content_agent import ContentAgent

    agent = ContentAgent()
    return await agent.summarize(text=body.text)


@router.post("/url")
async def summarize_url(
    body: SummarizeUrlRequest, user: dict = Depends(get_current_user)
) -> dict:
    """Scrape a URL and summarize its content using Gemini Flash."""
    import re

    import requests
    from bs4 import BeautifulSoup

    from app.agents.content_agent import ContentAgent
    from app.utils.helpers import truncate_text

    try:
        resp = requests.get(body.url, timeout=15, headers={"User-Agent": "LearnForge/1.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove navigation and boilerplate
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = truncate_text(text, max_chars=30000)
    except Exception as exc:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch URL: {str(exc)}",
        )

    agent = ContentAgent()
    return await agent.summarize(text=text)
