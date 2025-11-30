from typing import Optional
import random
from datetime import datetime, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities import Card, Deck, UserCardStats, LearnSession

TARGET_STREAK = 3
W_FAIL = 3.0
W_SUCCESS = 1.0
W_TIME = 0.05
W_DIFFICULTY = 2.0
W_STREAK = 2.0
W_LAST_ERROR = 5.0


async def start_session(
    session: AsyncSession, deck_id: int, user_id: int
) -> LearnSession:
    """Создать или вернуть активную сессию обучения."""
    existing = await session.execute(
        select(LearnSession).where(
            and_(
                LearnSession.deck_id == deck_id,
                LearnSession.user_id == user_id,
                LearnSession.status == "active",
            )
        )
    )
    learn_session = existing.scalars().first()
    if learn_session:
        await ensure_user_card_stats(session, deck_id, user_id)
        await update_session_progress(session, learn_session, user_id)
        return learn_session

    deck = await session.get(Deck, deck_id)
    if not deck:
        raise ValueError("Deck not found")

    cards_query = await session.execute(
        select(Card.id).where(Card.deck_id == deck_id)
    )
    card_ids = cards_query.scalars().all()
    total_cards = len(card_ids)

    await ensure_user_card_stats(session, deck_id, user_id, card_ids)
    await reset_stats_if_all_learned(session, deck_id, user_id)

    learn_session = LearnSession(
        user_id=user_id,
        deck_id=deck_id,
        total_cards=total_cards,
        learned_cards=0,
    )
    session.add(learn_session)
    await session.flush()

    await update_session_progress(session, learn_session, user_id)
    return learn_session


async def ensure_user_card_stats(
    session: AsyncSession,
    deck_id: int,
    user_id: int,
    card_ids: Optional[list[int]] = None,
) -> None:
    """Создать отсутствующие записи статистики для пользователя."""
    if card_ids is None:
        cards_query = await session.execute(
            select(Card.id).where(Card.deck_id == deck_id)
        )
        card_ids = cards_query.scalars().all()
    if not card_ids:
        return

    existing_query = await session.execute(
        select(UserCardStats.card_id).where(
            (UserCardStats.user_id == user_id)
            & (UserCardStats.card_id.in_(card_ids))
        )
    )
    existing = set(existing_query.scalars().all())

    for card_id in card_ids:
        if card_id in existing:
            continue
        stats = UserCardStats(
            user_id=user_id,
            card_id=card_id,
            success_count=0,
            fail_count=0,
            total_answers=0,
            correct_rate=0.0,
            streak=0,
            difficulty_score=0.5,
            is_learned=False,
            last_result=None,
            last_answered_at=None,
        )
        session.add(stats)
    await session.flush()


async def reset_stats_if_all_learned(
    session: AsyncSession, deck_id: int, user_id: int
) -> None:
    stats_query = await session.execute(
        select(UserCardStats)
        .join(Card, Card.id == UserCardStats.card_id)
        .where((Card.deck_id == deck_id) & (UserCardStats.user_id == user_id))
    )
    stats = stats_query.scalars().all()
    if not stats:
        return
    if all(stat.is_learned for stat in stats):
        for stat in stats:
            stat.success_count = 0
            stat.fail_count = 0
            stat.total_answers = 0
            stat.correct_rate = 0.0
            stat.streak = 0
            stat.difficulty_score = 0.5
            stat.is_learned = False
            stat.last_result = None
            stat.last_answered_at = None
        await session.flush()


async def get_session(
    session: AsyncSession, session_id: int, user_id: int
) -> Optional[LearnSession]:
    result = await session.execute(
        select(LearnSession).where(
            (LearnSession.id == session_id) & (LearnSession.user_id == user_id)
        )
    )
    return result.scalars().first()


async def reset_cycle_if_needed(
    session: AsyncSession, deck_id: int, user_id: int
) -> None:
    await reset_stats_if_all_learned(session, deck_id, user_id)


def _compute_weight(stat: UserCardStats) -> float:
    weight = 0.0
    if stat.total_answers == 0:
        weight += 100.0
    if stat.last_result is False:
        weight += W_LAST_ERROR
    weight += W_FAIL * stat.fail_count
    weight -= W_SUCCESS * stat.success_count
    weight += W_STREAK * max(0, TARGET_STREAK - stat.streak)

    if stat.last_answered_at is None:
        hours_since = 100.0
    else:
        hours_since = (
            datetime.now(timezone.utc) - stat.last_answered_at
        ).total_seconds() / 3600
    weight += W_TIME * hours_since

    weight += W_DIFFICULTY * stat.difficulty_score
    if stat.is_learned:
        weight -= 50.0
    return weight


async def get_next_card(
    session: AsyncSession, learn_session: LearnSession, user_id: int
) -> Optional[int]:
    await ensure_user_card_stats(session, learn_session.deck_id, user_id)
    await reset_cycle_if_needed(session, learn_session.deck_id, user_id)

    stats_query = await session.execute(
        select(UserCardStats, Card)
        .join(Card, Card.id == UserCardStats.card_id)
        .where(
            (Card.deck_id == learn_session.deck_id)
            & (UserCardStats.user_id == user_id)
        )
    )
    rows = stats_query.all()
    if not rows:
        return None

    weighted = []
    for stat, card in rows:
        weighted.append((_compute_weight(stat), card.id))
    if not weighted:
        return None

    max_weight = max(weighted, key=lambda x: x[0])[0]
    top_cards = [
        card_id for weight, card_id in weighted if weight == max_weight
    ]
    return random.choice(top_cards) if top_cards else None


async def record_answer(
    session: AsyncSession,
    learn_session: LearnSession,
    user_id: int,
    card_id: int,
    correct: bool,
    answer_time_seconds: int,
) -> None:
    stats_query = await session.execute(
        select(UserCardStats).where(
            (UserCardStats.user_id == user_id)
            & (UserCardStats.card_id == card_id)
        )
    )
    stats = stats_query.scalars().first()
    if not stats:
        stats = UserCardStats(
            user_id=user_id,
            card_id=card_id,
        )
        session.add(stats)
        await session.flush()

    now = datetime.now(timezone.utc)

    if correct:
        stats.success_count += 1
        stats.streak += 1
        stats.last_result = True
    else:
        stats.fail_count += 1
        stats.streak = 0
        stats.last_result = False
        stats.is_learned = False

    stats.total_answers = stats.success_count + stats.fail_count
    if stats.total_answers:
        stats.correct_rate = stats.success_count / stats.total_answers
    else:
        stats.correct_rate = 0.0

    if stats.total_answers == 1:
        stats.difficulty_score = 0.3 if correct else 0.8
    else:
        stats.difficulty_score = stats.fail_count / (
            stats.success_count + stats.fail_count + 1
        )

    stats.is_learned = stats.streak >= TARGET_STREAK
    stats.last_answered_at = now

    await session.flush()
    await update_session_progress(session, learn_session, user_id)


async def update_session_progress(
    session: AsyncSession, learn_session: LearnSession, user_id: int
) -> None:
    stats_query = await session.execute(
        select(UserCardStats.is_learned)
        .join(Card, Card.id == UserCardStats.card_id)
        .where(
            (Card.deck_id == learn_session.deck_id)
            & (UserCardStats.user_id == user_id)
        )
    )
    stats = stats_query.scalars().all()
    total = len(stats)
    learned = sum(1 for value in stats if value)
    learn_session.total_cards = max(learn_session.total_cards, total)
    learn_session.learned_cards = learned
    if (
        learn_session.total_cards > 0
        and learn_session.learned_cards >= learn_session.total_cards
    ):
        learn_session.status = "completed"
        learn_session.ended_at = datetime.now(timezone.utc)
    await session.flush()


async def finish_session(
    session: AsyncSession, learn_session: LearnSession
) -> None:
    learn_session.status = "completed"
    learn_session.ended_at = datetime.now(timezone.utc)
    await session.flush()
