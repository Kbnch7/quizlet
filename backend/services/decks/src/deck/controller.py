from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

import src.deck.service as deck_service
from src.database.core import get_async_db_session
from .models import (
    SDeckCreate,
    SDeckUpdate,
    SDeckResponse,
    SDeckDetailedResponse,
)
from src.auth import get_current_user, UserContext, is_authorized_for_resource
from src.deck_stats.service import get_deck_stats
from src.utils.storage import BUCKET_CARDS, get_storage_client

router = APIRouter(prefix="/deck", tags=["deck"])


def _signer_client():
    return get_storage_client()


def _presign_deck_cards(deck):
    """Заменить front_image_url и back_image_url в карточке (Card) на presigned_url"""
    bucket = BUCKET_CARDS
    signer = _signer_client()
    if getattr(deck, "cards", None):
        for card in deck.cards:
            if card.front_image_url and not card.front_image_url.startswith(
                "temp/"
            ):
                card.front_image_url = signer.presigned_get_url(
                    bucket, card.front_image_url
                )
            if card.back_image_url and not card.back_image_url.startswith(
                "temp/"
            ):
                card.back_image_url = signer.presigned_get_url(
                    bucket, card.back_image_url
                )


@router.get("/", response_model=List[SDeckResponse])
async def get_decks(
    response: Response,
    author: Optional[int] = Query(default=None),
    category: Optional[str] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    my_teachers: Optional[bool] = Query(
        default=None
    ),  # stubbed, not used TODO: my_teachers
    cursor: Optional[int] = Query(default=None),
    limit: int = Query(default=20, le=100),
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    decks, next_cursor = await deck_service.list_decks(
        session,
        author=author,
        category_slug=category,
        tag_slug=tag,
        cursor=cursor,
        limit=limit,
    )
    if next_cursor and response is not None:
        response.headers["X-Next-Cursor"] = str(next_cursor)
    return decks


@router.post("/", response_model=SDeckDetailedResponse)
async def create_deck(
    payload: SDeckCreate,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    if payload.owner_id is not None:
        if not user.is_manager:
            raise HTTPException(status_code=403, detail="Forbidden")
        owner_id = payload.owner_id
    else:
        owner_id = user.id
    deck = await deck_service.create_deck(
        session,
        owner_id=owner_id,
        title=payload.title,
        description=payload.description,
        categories=payload.categories,
        tags=payload.tags,
    )
    await session.commit()
    _presign_deck_cards(deck)
    return deck


@router.get("/{deck_id}/", response_model=SDeckDetailedResponse)
async def get_deck(
    deck_id: int,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    deck = await deck_service.get_deck(session, deck_id)
    if deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    _presign_deck_cards(deck)
    return deck


@router.patch("/{deck_id}/", response_model=SDeckDetailedResponse)
async def update_deck(
    deck_id: int,
    payload: SDeckUpdate,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    deck = await deck_service.get_deck(session, deck_id)
    if deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    if not is_authorized_for_resource(deck.owner_id, user):
        raise HTTPException(status_code=403, detail="Forbidden")
    deck = await deck_service.update_deck(
        session,
        deck,
        title=payload.title,
        description=payload.description,
        categories=payload.categories,
        tags=payload.tags,
    )
    await session.commit()
    _presign_deck_cards(deck)
    return deck


@router.delete("/{deck_id}/", status_code=204)
async def delete_deck(
    deck_id: int,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    deck = await deck_service.get_deck(session, deck_id)
    if deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    if not is_authorized_for_resource(deck.owner_id, user):
        raise HTTPException(status_code=403, detail="Forbidden")
    await deck_service.delete_deck(session, deck_id)
    await session.commit()
    return None


@router.get("/{deck_id}/stats/")
async def deck_stats(
    deck_id: int,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    deck = await deck_service.get_deck(session, deck_id)
    if deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    if not is_authorized_for_resource(deck.owner_id, user):
        raise HTTPException(status_code=403, detail="Forbidden")
    stats = await get_deck_stats(session, deck_id)
    return {
        "deck_id": stats.deck_id,
        "total_tests": stats.total_tests,
        "avg_score": stats.avg_score,
        "correct_rate": stats.correct_rate,
        "avg_time_seconds": stats.avg_time_seconds,
        "card_stats": stats.card_stats,
    }
