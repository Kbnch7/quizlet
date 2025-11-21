from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities import TestResult, CardResult


async def create_test_result(
    session: AsyncSession,
    *,
    deck_id: int,
    user_id: int,
    total_time_seconds: int,
    correct_rate: float,
    card_results: List[dict],
) -> TestResult:
    tr = TestResult(
        deck_id=deck_id,
        user_id=user_id,
        total_time_seconds=total_time_seconds,
        correct_rate=correct_rate,
    )
    session.add(tr)
    await session.flush()
    for cr in card_results:
        trc = CardResult(
            test_result_id=tr.id,
            user_id=user_id,
            card_id=cr["card_id"],
            correct=cr["correct"],
            answer_time_seconds=cr["answer_time_seconds"],
            user_answer=cr.get("user_answer"),
        )
        session.add(trc)
    await session.flush()
    await session.refresh(tr)
    return tr


async def list_test_results(
    session: AsyncSession,
    deck_id: int,
    *,
    cursor: Optional[int],
    limit: int,
    user_filter: int | None = None,
) -> tuple[List[TestResult], Optional[int]]:
    conditions = [TestResult.deck_id == deck_id]
    if user_filter is not None:
        conditions.append(TestResult.user_id == user_filter)
    if cursor is not None:
        conditions.append(TestResult.id < cursor)

    query = (
        select(TestResult)
        .where(and_(*conditions))
        .options(selectinload(TestResult.card_results))
        .order_by(TestResult.id.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    items = result.scalars().all()
    next_cursor = items[-1].id if len(items) == limit else None
    return items, next_cursor
