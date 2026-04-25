"""Flashcards router — generate and review spaced-repetition flashcard decks."""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.services.firestore_service import firestore_service
from app.utils.helpers import generate_id

logger = structlog.get_logger(__name__)
router = APIRouter()

LEITNER_REVIEW_DAYS = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}


class GenerateFlashcardsRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=300)
    num_cards: int = Field(10, ge=1, le=50)


class ReviewCardRequest(BaseModel):
    card_id: str
    confidence: int = Field(..., ge=1, le=5)


@router.post("/generate")
async def generate_flashcards(
    body: GenerateFlashcardsRequest, user: dict = Depends(get_current_user)
) -> dict:
    """Generate a spaced-repetition flashcard deck on a topic using Gemini Flash."""
    from app.agents.content_agent import ContentAgent

    user_id: str = user["uid"]
    agent = ContentAgent()

    deck_data = await agent.generate_flashcards(
        topic=body.topic, num_cards=body.num_cards
    )

    deck_id = generate_id("deck_")
    now = datetime.now(tz=timezone.utc).isoformat()

    # Initialise Leitner box and review schedule for each card
    for card in deck_data.get("cards", []):
        card["box"] = 1
        card["last_reviewed"] = None

    deck_record = {
        "deck_id": deck_id,
        "topic": body.topic,
        "deck_title": deck_data.get("deck_title", body.topic),
        "cards": deck_data.get("cards", []),
        "created_at": now,
    }
    firestore_service.set_top_level_user_doc("flashcards", user_id, deck_id, deck_record)

    return {"deck_id": deck_id, "cards": deck_record["cards"]}


@router.patch("/{deck_id}/review")
async def review_card(
    deck_id: str,
    body: ReviewCardRequest,
    user: dict = Depends(get_current_user),
) -> dict:
    """Record a confidence rating for a flashcard (Leitner spaced repetition)."""
    from datetime import timedelta

    user_id: str = user["uid"]
    deck = firestore_service.get_top_level_user_doc("flashcards", user_id, deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck {deck_id} not found.",
        )

    cards = deck.get("cards", [])
    card = next((c for c in cards if c.get("id") == body.card_id), None)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card {body.card_id} not found.",
        )

    now = datetime.now(tz=timezone.utc)
    card["last_reviewed"] = now.isoformat()

    # Leitner system: confidence >= 4 → advance box; else reset to box 1
    current_box = card.get("box", 1)
    if body.confidence >= 4:
        card["box"] = min(current_box + 1, 5)
    else:
        card["box"] = 1

    days_until_review = LEITNER_REVIEW_DAYS.get(card["box"], 1)
    next_review = (now + timedelta(days=days_until_review)).isoformat()
    card["next_review"] = next_review

    firestore_service.update_top_level_user_doc(
        "flashcards", user_id, deck_id, {"cards": cards}
    )

    return {"next_review": next_review, "box": card["box"]}
