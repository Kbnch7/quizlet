from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.test_result import TestResult
from src.entities.test_result_card import TestResultCard


async def create_test_result(
    session: AsyncSession,
    *,
    deck_id: int,
    user_id: int,
    total_time_ms: int,
    score: float,
    card_results: List[dict],
) -> TestResult:
    tr = TestResult(deck_id=deck_id, user_id=user_id, total_time_ms=total_time_ms, score=score)
    session.add(tr)
    await session.flush()
    for cr in card_results:
        trc = TestResultCard(
            test_result_id=tr.id,
            card_id=cr["card_id"],
            correct=cr["correct"],
            answer_time_ms=cr["answer_time_ms"],
            user_answer=cr.get("user_answer"),
        )
        session.add(trc)
    await session.flush()
    await session.refresh(tr)
    return tr


async def list_test_results(session: AsyncSession, deck_id: int) -> List[TestResult]:
    result = await session.execute(
        select(TestResult)
        .where(TestResult.deck_id == deck_id)
        .options(selectinload(TestResult.card_results))
        .order_by(TestResult.id.desc())
    )
    return result.scalars().all()


