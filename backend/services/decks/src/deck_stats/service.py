from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities import DeckStats, CardResult


async def update_deck_stats(
    session: AsyncSession,
    deck_id: int,
    new_correct_rate: float,
    new_total_time_seconds: int,
    card_results: List[CardResult],
) -> DeckStats:
    stats = await session.get(DeckStats, deck_id)

    if stats is None:
        card_stats: Dict[int, Dict[str, Any]] = {}
        for cr in card_results:
            card_stats[cr.card_id] = {
                "total": 1,
                "correct": 1 if cr.correct else 0,
                "avg_time_seconds": cr.answer_time_seconds,
                "correct_rate": 1.0 if cr.correct else 0.0,
            }

        stats = DeckStats(
            deck_id=deck_id,
            total_tests=1,
            avg_score=new_correct_rate,
            correct_rate=1.0 if new_correct_rate >= 0.5 else 0.0,
            avg_time_seconds=new_total_time_seconds,
            card_stats=card_stats if card_stats else None,
        )
        session.add(stats)
    else:
        # обновление статистик для карточек
        old_total = stats.total_tests
        new_total = old_total + 1

        stats.total_tests = new_total
        stats.avg_score = (
            stats.avg_score * old_total + new_correct_rate
        ) / new_total

        old_successful = stats.correct_rate * old_total
        new_successful = old_successful + (
            1.0 if new_correct_rate >= 0.5 else 0.0
        )
        stats.correct_rate = new_successful / new_total

        stats.avg_time_seconds = int(
            (stats.avg_time_seconds * old_total + new_total_time_seconds)
            / new_total
        )

        if stats.card_stats is None:
            stats.card_stats = {}

        for cr in card_results:
            card_id = cr.card_id
            if card_id not in stats.card_stats:
                stats.card_stats[card_id] = {
                    "total": 0,
                    "correct": 0,
                    "avg_time_seconds": 0,
                }

            card_stat = stats.card_stats[card_id]
            old_card_total = card_stat["total"]
            new_card_total = old_card_total + 1

            card_stat["total"] = new_card_total
            if cr.correct:
                card_stat["correct"] += 1

            card_stat["avg_time_seconds"] = int(
                (
                    card_stat["avg_time_seconds"] * old_card_total
                    + cr.answer_time_seconds
                )
                / new_card_total
            )

            card_stat["correct_rate"] = card_stat["correct"] / new_card_total

    await session.flush()
    return stats


async def get_deck_stats(session: AsyncSession, deck_id: int) -> DeckStats:
    stats = await session.get(DeckStats, deck_id)
    if stats is None:
        stats = DeckStats(
            deck_id=deck_id,
            total_tests=0,
            avg_score=0.0,
            correct_rate=0.0,
            avg_time_seconds=0,
            card_stats=None,
        )
        session.add(stats)
        await session.flush()
    return stats
