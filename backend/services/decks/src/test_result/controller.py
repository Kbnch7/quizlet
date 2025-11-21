from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    BackgroundTasks,
    Query,
    Response,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .models import STestResultCreate, STestResultResponse
from .service import create_test_result, list_test_results
from src.database.core import get_async_db_session, async_session_maker
from src.entities import Deck, Card, TestResult
from src.auth import get_current_user, UserContext, is_authorized_for_resource
from src.deck_stats.service import update_deck_stats

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
                    new_correct_rate=test_result.correct_rate,
                    new_total_time_seconds=test_result.total_time_seconds,
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
    deck = (
        (await session.execute(select(Deck).where(Deck.id == deck_id)))
        .scalars()
        .first()
    )
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if user.id != payload.user_id and not user.is_manager:
        raise HTTPException(status_code=403, detail="Forbidden")

    card_ids = {cr.card_id for cr in payload.card_results}
    if card_ids:
        cards_query = await session.execute(
            select(Card.id).where(
                (Card.id.in_(card_ids)) & (Card.deck_id == deck_id)
            )
        )
        valid_ids = set(cards_query.scalars().all())
        invalid = card_ids - valid_ids
        if invalid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Some card_ids do not belong to this deck",
                    "invalid_card_ids": list(invalid),
                },
            )

    tr = await create_test_result(
        session, deck_id=deck_id, **payload.model_dump()
    )
    await session.commit()
    background_tasks.add_task(_update_stats_background, tr.id, deck_id)
    await session.refresh(tr, ["card_results"])
    return tr


@router.get("/{deck_id}/results", response_model=List[STestResultResponse])
async def list_results(
    deck_id: int,
    response: Response,
    cursor: Optional[int] = Query(
        None, description="Use last seen result id for pagination"
    ),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    deck = (
        (await session.execute(select(Deck).where(Deck.id == deck_id)))
        .scalars()
        .first()
    )
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    is_owner = is_authorized_for_resource(deck.owner_id, user)

    if not is_owner:
        filter_user_id = user.id
    else:
        filter_user_id = user_id

    results, next_cursor = await list_test_results(
        session,
        deck_id,
        cursor=cursor,
        limit=limit,
        user_filter=filter_user_id,
    )
    if next_cursor and response is not None:
        response.headers["X-Next-Cursor"] = str(next_cursor)
    return results
