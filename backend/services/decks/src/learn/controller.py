from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import UserContext, get_current_user
from src.database.core import get_async_db_session
from src.entities import Deck
from src.learn.models import (
    SLearnAnswer,
    SLearnBatchResponse,
    SLearnProgressResponse,
    SLearnSessionCreateResponse,
    SLearnSessionResponse,
)
from src.learn.service import (
    finish_session,
    get_next_card,
    get_session,
    record_answer,
    start_session,
    update_session_progress,
)

router = APIRouter(prefix="/api/learn", tags=["learn"])


def _session_to_response(learn_session) -> SLearnSessionResponse:
    return SLearnSessionResponse(
        id=learn_session.id,
        deck_id=learn_session.deck_id,
        status=learn_session.status,
        total_cards=learn_session.total_cards,
        learned_cards=learn_session.learned_cards,
        started_at=learn_session.started_at.isoformat(),
        ended_at=(
            learn_session.ended_at.isoformat() if learn_session.ended_at else None
        ),
    )


def _progress_response(learn_session) -> SLearnProgressResponse:
    total = max(learn_session.total_cards, 1)
    progress = learn_session.learned_cards / total
    return SLearnProgressResponse(
        session_id=learn_session.id,
        learned_cards=learn_session.learned_cards,
        total_cards=total,
        progress=progress,
        is_completed=learn_session.status == "completed",
    )


@router.post("/deck/{deck_id}/sessions", response_model=SLearnSessionCreateResponse)
async def create_learn_session(
    deck_id: int,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    deck = await session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if deck.cards_amount == 0:
        raise HTTPException(status_code=400, detail="Deck has no cards")

    learn_session = await start_session(session, deck_id, user.id)
    progress = learn_session.learned_cards / max(learn_session.total_cards, 1)
    await session.commit()
    return SLearnSessionCreateResponse(
        session=_session_to_response(learn_session),
        progress=progress,
    )


@router.get("/sessions/{session_id}", response_model=SLearnSessionResponse)
async def get_learn_session(
    session_id: int,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    learn_session = await get_session(session, session_id, user.id)
    if not learn_session:
        raise HTTPException(status_code=404, detail="Learn session not found")
    return _session_to_response(learn_session)


@router.get("/sessions/{session_id}/next", response_model=SLearnBatchResponse)
async def get_next_card_endpoint(
    session_id: int,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    learn_session = await get_session(session, session_id, user.id)
    if not learn_session:
        raise HTTPException(status_code=404, detail="Learn session not found")
    if learn_session.status != "active":
        raise HTTPException(
            status_code=400, detail="Learn session is not active")

    card_id = await get_next_card(session, learn_session, user.id)
    await update_session_progress(session, learn_session, user.id)
    await session.commit()
    total = max(learn_session.total_cards, 1)
    progress = learn_session.learned_cards / total
    return SLearnBatchResponse(
        session_id=learn_session.id,
        card_id=card_id,
        learned_cards=learn_session.learned_cards,
        total_cards=total,
        progress=progress,
    )


@router.post(
    "/sessions/{session_id}/cards/{card_id}/answer",
    response_model=SLearnProgressResponse,
)
async def submit_answer(
    session_id: int,
    card_id: int,
    payload: SLearnAnswer,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    learn_session = await get_session(session, session_id, user.id)
    if not learn_session:
        raise HTTPException(status_code=404, detail="Learn session not found")
    if learn_session.status != "active":
        raise HTTPException(
            status_code=400, detail="Learn session is not active")

    await record_answer(
        session,
        learn_session,
        user.id,
        card_id,
        payload.correct,
        payload.answer_time_seconds,
    )
    await update_session_progress(session, learn_session, user.id)
    await session.commit()
    return _progress_response(learn_session)


@router.get("/sessions/{session_id}/progress", response_model=SLearnProgressResponse)
async def get_session_progress(
    session_id: int,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    learn_session = await get_session(session, session_id, user.id)
    if not learn_session:
        raise HTTPException(status_code=404, detail="Learn session not found")
    await update_session_progress(session, learn_session, user.id)
    await session.commit()
    return _progress_response(learn_session)


@router.post("/sessions/{session_id}/finish", response_model=SLearnProgressResponse)
async def finish_learn_session(
    session_id: int,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    learn_session = await get_session(session, session_id, user.id)
    if not learn_session:
        raise HTTPException(status_code=404, detail="Learn session not found")

    await finish_session(session, learn_session)
    await update_session_progress(session, learn_session, user.id)
    await session.commit()
    return _progress_response(learn_session)
