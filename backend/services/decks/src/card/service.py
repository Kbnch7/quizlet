import logging
import os
from typing import Dict, List, Optional

from event_contracts.base import EventEnvelope
from event_contracts.content.v1 import CardCreated as EventCardCreatedV1
from event_contracts.kafka_producer import KafkaProducer
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.card.models import SCardBulkItem
from src.entities import Card, CardResult, Deck, UserCardStats
from src.utils.minio import extract_object_key_from_url
from src.utils.storage import BUCKET_CARDS, get_storage_client

logger = logging.getLogger(__name__)
producer = KafkaProducer(os.getenv("KAFKA_BROKER_URL"))


async def create_card(
    session: AsyncSession,
    *,
    deck_id: int,
    front_text: str,
    back_text: str,
    front_image_url: Optional[str],
    back_image_url: Optional[str],
    order_index: Optional[int],
) -> Card:
    card = Card(
        deck_id=deck_id,
        front_text=front_text,
        back_text=back_text,
        front_image_url=front_image_url,
        back_image_url=back_image_url,
        order_index=order_index or 0,
    )
    session.add(card)
    await session.flush()
    deck = await session.get(Deck, deck_id)
    if deck:
        deck.cards_amount += 1
    await session.flush()

    stats_query = await session.execute(
        select(UserCardStats.user_id)
        .join(Card, Card.id == UserCardStats.card_id)
        .where(Card.deck_id == deck_id)
    )
    user_ids = {row[0] for row in stats_query.all()}
    for user_id in user_ids:
        stats = UserCardStats(
            user_id=user_id,
            card_id=card.id,
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
    await session.refresh(card)

    payload = EventCardCreatedV1(
        card_id=card.id, deck_id=card.deck_id, created_at=card.created_at
    )
    event = EventEnvelope(
        event_type="card_created",
        event_version=1,
        occured_at=card.created_at,
        producer="decks-service",
        payload=payload.model_dump(),
    )
    try:
        producer.send(
            topic="content.events",
            key=str(card.id),
            value=event.to_json(),
        )
    except Exception as e:
        logger.exception(
            f"Failed to send card_created event: {e}",
            extra={
                "card_id": card.id,
                "deck_id": deck.id,
                "user_id": deck.owner_id,
            },
        )

    return card


async def get_card(session: AsyncSession, card_id: int) -> Optional[Card]:
    result = await session.execute(select(Card).where(Card.id == card_id))
    return result.scalars().first()


async def update_card(
    session: AsyncSession,
    card: Card,
    *,
    front_text: Optional[str],
    back_text: Optional[str],
    front_image_url: Optional[str],
    back_image_url: Optional[str],
    order_index: Optional[int],
) -> Card:
    if front_text is not None:
        card.front_text = front_text
    if back_text is not None:
        card.back_text = back_text
    if front_image_url is not None:
        card.front_image_url = front_image_url
    if back_image_url is not None:
        card.back_image_url = back_image_url
    if order_index is not None:
        card.order_index = order_index

    # Перемещение фотографий из temp в основную структуру

    storage = get_storage_client()

    if front_image_url:
        src_key = extract_object_key_from_url(front_image_url, BUCKET_CARDS)
        if src_key.startswith("temp/"):
            _, _, ext = src_key.rpartition(".")
            ext_part = f".{ext}" if ext else ""
            dst_key = f"decks/{card.deck_id}/card/{card.id}/images/front{ext_part}"
            storage.copy_object(BUCKET_CARDS, src_key, dst_key)
            storage.remove_object(BUCKET_CARDS, src_key)
            card.front_image_url = dst_key
    if back_image_url:
        src_key = extract_object_key_from_url(back_image_url, BUCKET_CARDS)
        if src_key.startswith("temp/"):
            _, _, ext = src_key.rpartition(".")
            ext_part = f".{ext}" if ext else ""
            dst_key = f"decks/{card.deck_id}/card/{card.id}/images/back{ext_part}"
            storage.copy_object(BUCKET_CARDS, src_key, dst_key)
            storage.remove_object(BUCKET_CARDS, src_key)
            card.back_image_url = dst_key

    stats_query = await session.execute(
        select(UserCardStats).where(UserCardStats.card_id == card.id)
    )
    stats = stats_query.scalars().all()
    for stat in stats:
        stat.streak = 0
        stat.is_learned = False
        stat.difficulty_score = 0.5

    await session.flush()
    await session.refresh(card)
    return card


async def delete_card(session: AsyncSession, card_id: int) -> None:
    card = await get_card(session, card_id)
    if card:
        deck = await session.get(Deck, card.deck_id)
        if deck:
            deck.cards_amount = max(0, deck.cards_amount - 1)
    await session.execute(delete(CardResult).where(CardResult.card_id == card_id))
    await session.execute(delete(UserCardStats).where(UserCardStats.card_id == card_id))
    await session.execute(delete(Card).where(Card.id == card_id))


async def bulk_upsert_delete_cards(
    session: AsyncSession,
    deck_id: int,
    items: List[SCardBulkItem],
) -> None:
    """Множественные операции над карточками"""
    errors: List[Dict[str, str]] = []
    ids_to_touch = [it.id for it in items if it.id]
    id_to_card: Dict[int, Card] = {}
    if ids_to_touch:
        result = await session.execute(select(Card).where(Card.id.in_(ids_to_touch)))
        fetched = result.scalars().all()
        id_to_card = {c.id: c for c in fetched}

    for idx, item in enumerate(items):
        if item.to_delete:
            if not item.id:
                errors.append({"index": str(idx), "error": "to_delete requires id"})
                continue
            card = id_to_card.get(item.id)
            if not card:
                errors.append({"index": str(idx), "error": f"card {item.id} not found"})
            elif card.deck_id != deck_id:
                errors.append(
                    {
                        "index": str(idx),
                        "error": (f"card {item.id} does not belong to deck {deck_id}"),
                    }
                )
        elif item.id:
            # update
            card = id_to_card.get(item.id)
            if not card:
                errors.append({"index": str(idx), "error": f"card {item.id} not found"})
            elif card.deck_id != deck_id:
                errors.append(
                    {
                        "index": str(idx),
                        "error": (f"card {item.id} does not belong to deck {deck_id}"),
                    }
                )
        else:
            # create
            if not item.front_text or not item.back_text:
                errors.append(
                    {
                        "index": str(idx),
                        "error": ("front_text and back_text are required for creation"),
                    }
                )

    if errors:
        return errors

    storage = get_storage_client()

    for item in items:
        if item.to_delete:
            if item.id:
                await delete_card(session, item.id)
            continue
        if item.id:
            card = id_to_card.get(item.id)
            if not card:
                continue
            updated = await update_card(
                session,
                card,
                front_text=item.front_text,
                back_text=item.back_text,
                front_image_url=item.front_image_url,
                back_image_url=item.back_image_url,
                order_index=item.order_index,
            )
            # переместить картинку из temp
            if item.front_image_url:
                src_key = extract_object_key_from_url(
                    item.front_image_url, BUCKET_CARDS
                )
                if src_key.startswith("temp/"):
                    _, _, ext = src_key.rpartition(".")
                    ext_part = f".{ext}" if ext else ""
                    dst_key = (
                        f"decks/{deck_id}/card/{updated.id}/images/front{ext_part}"
                    )
                    storage.copy_object(BUCKET_CARDS, src_key, dst_key)
                    storage.remove_object(BUCKET_CARDS, src_key)
                    updated.front_image_url = dst_key
            if item.back_image_url:
                src_key = extract_object_key_from_url(item.back_image_url, BUCKET_CARDS)
                if src_key.startswith("temp/"):
                    _, _, ext = src_key.rpartition(".")
                    ext_part = f".{ext}" if ext else ""
                    dst_key = f"decks/{deck_id}/card/"
                    f"{updated.id}/images/back{ext_part}"
                    storage.copy_object(BUCKET_CARDS, src_key, dst_key)
                    storage.remove_object(BUCKET_CARDS, src_key)
                    updated.back_image_url = dst_key
        else:
            created = await create_card(
                session,
                deck_id=deck_id,
                front_text=item.front_text or "",
                back_text=item.back_text or "",
                front_image_url=item.front_image_url,
                back_image_url=item.back_image_url,
                order_index=item.order_index,
            )
            # переместить картинку из temp
            if item.front_image_url:
                src_key = extract_object_key_from_url(
                    item.front_image_url, BUCKET_CARDS
                )
                if src_key.startswith("temp/"):
                    _, _, ext = src_key.rpartition(".")
                    ext_part = f".{ext}" if ext else ""
                    dst_key = (
                        f"decks/{deck_id}/card/{created.id}/images/front{ext_part}"
                    )
                    storage.copy_object(BUCKET_CARDS, src_key, dst_key)
                    storage.remove_object(BUCKET_CARDS, src_key)
                    created.front_image_url = dst_key
            if item.back_image_url:
                src_key = extract_object_key_from_url(item.back_image_url, BUCKET_CARDS)
                if src_key.startswith("temp/"):
                    _, _, ext = src_key.rpartition(".")
                    ext_part = f".{ext}" if ext else ""
                    dst_key = f"decks/{deck_id}/card/"
                    f"{created.id}/images/back{ext_part}"
                    storage.copy_object(BUCKET_CARDS, src_key, dst_key)
                    storage.remove_object(BUCKET_CARDS, src_key)
                    created.back_image_url = dst_key
            await session.flush()
