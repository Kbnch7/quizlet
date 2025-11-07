from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .models import STestResultCreate, STestResultResponse
from .service import create_test_result, list_test_results
from src.database.core import get_async_db_session, async_session_maker
from src.entities.deck import Deck
from src.auth import get_current_user, UserContext, is_authorized_for_resource
from src.deck_stats.service import update_deck_stats
from src.entities.test_result import TestResult


router = APIRouter(prefix="/deck", tags=["test_result"])


async def _update_stats_background(test_result_id: int, deck_id: int) -> None:
    async with async_session_maker() as session:
        try:
            result = await session.execute(
                select(TestResult)
                .where(TestResult.id == test_result_id)
                .options(selectinload(TestResult.card_results))
            )
            test_result = result.scalars().first()
            
            if test_result:
                await update_deck_stats(
                    session,
                    deck_id=deck_id,
                    new_score=test_result.score,
                    new_total_time_ms=test_result.total_time_ms,
                    card_results=test_result.card_results,
                )
                await session.commit()
        except Exception:
            await session.rollback()


@router.post("/{deck_id}/results", response_model=STestResultResponse)
async def create_result(
    deck_id: int,
    payload: STestResultCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    deck = (await session.execute(select(Deck).where(Deck.id == deck_id))).scalars().first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    # if not is_authorized_for_resource(deck.owner_id, user):
    #     raise HTTPException(status_code=403, detail="Forbidden")
    tr = await create_test_result(session, deck_id=deck_id, **payload.model_dump())
    await session.commit()
    background_tasks.add_task(_update_stats_background, tr.id, deck_id)
    result = await session.execute(
        select(TestResult)
        .where(TestResult.id == tr.id)
        .options(selectinload(TestResult.card_results))
    )
    result = result.scalars().first()
    return result


@router.get("/{deck_id}/results", response_model=List[STestResultResponse])
async def list_results(
    deck_id: int,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    deck = (await session.execute(select(Deck).where(Deck.id == deck_id))).scalars().first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    print(user.id)
    if not is_authorized_for_resource(deck.owner_id, user):
        raise HTTPException(status_code=403, detail="Forbidden")
    results = await list_test_results(session, deck_id)
    return results


