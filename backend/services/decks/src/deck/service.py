import logging
import os
from typing import List, Optional

from event_contracts.base import EventEnvelope
from event_contracts.content.v1 import DeckCreated as EventDeckCreatedV1
from event_contracts.kafka_producer import KafkaProducer
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.entities import Category, Deck, Tag, deck_categories, deck_tags
from src.exceptions import CategoryNotFoundError

logger = logging.getLogger(__name__)
producer = KafkaProducer(os.getenv("KAFKA_BROKER_URL"))


async def _get_or_error_categories(
    session: AsyncSession, slugs: List[str]
) -> List[Category]:
    if not slugs:
        return []
    result = await session.execute(select(Category).where(Category.slug.in_(slugs)))
    existing = {c.slug: c for c in result.scalars().all()}
    missing = [slug for slug in slugs if slug not in existing]
    if missing:
        raise CategoryNotFoundError(missing_slugs=missing)
    return [existing[s] for s in slugs]


async def _get_or_create_tags(
    session: AsyncSession, names_or_slugs: List[str]
) -> List[Tag]:
    if not names_or_slugs:
        return []
    result = await session.execute(
        select(Tag).where(
            (Tag.slug.in_(names_or_slugs)) | (Tag.name.in_(names_or_slugs))
        )
    )
    existing_by_key = {t.slug: t for t in result.scalars().all()}
    tags: List[Tag] = []
    for key in names_or_slugs:
        tag = existing_by_key.get(key)
        if tag is None:
            tag = Tag(name=key, slug=key)
            session.add(tag)
        tags.append(tag)
    return tags


async def list_decks(
    session: AsyncSession,
    *,
    author: Optional[int] = None,
    category_slug: Optional[str] = None,
    tag_slug: Optional[str] = None,
    cursor: Optional[int] = None,
    limit: int = 20,
) -> tuple[List[Deck], Optional[int]]:
    query = select(Deck)
    if author is not None:
        query = query.where(Deck.owner_id == author)
    if cursor is not None:
        query = query.where(Deck.id > cursor)
    if category_slug:
        query = query.join(Deck.categories).where(Category.slug == category_slug)
    if tag_slug:
        query = query.join(Deck.tags).where(Tag.slug == tag_slug)
    query = query.order_by(Deck.id.asc()).limit(limit)
    result = await session.execute(query)
    items = result.scalars().unique().all()
    next_cursor = items[-1].id if len(items) == limit else None
    return items, next_cursor


async def create_deck(
    session: AsyncSession,
    *,
    owner_id: int,
    title: str,
    description: Optional[str],
    categories: Optional[List[str]],
    tags: Optional[List[str]],
) -> Deck:
    cats = await _get_or_error_categories(session, categories or [])
    tgs = await _get_or_create_tags(session, tags or [])
    deck = Deck(owner_id=owner_id, title=title, description=description)
    session.add(deck)
    await session.flush()

    if cats:
        values = [{"deck_id": deck.id, "category_id": c.id} for c in cats]
        await session.execute(insert(deck_categories), values)
    if tgs:
        values = [{"deck_id": deck.id, "tag_id": t.id} for t in tgs]
        await session.execute(insert(deck_tags), values)
    await session.flush()

    result = await session.execute(
        select(Deck)
        .where(Deck.id == deck.id)
        .options(
            selectinload(Deck.cards),
            selectinload(Deck.categories),
            selectinload(Deck.tags),
        )
    )

    payload = EventDeckCreatedV1(
        deck_id=deck.id, author_id=deck.owner_id, created_at=deck.created_at
    )
    event = EventEnvelope(
        event_type="deck_created",
        event_version=1,
        producer="decks-service",
        occured_at=deck.created_at,
        payload=payload.model_dump(),
    )
    try:
        producer.send(
            topic="content.events",
            key=str(deck.id),
            value=event.to_json(),
        )
    except Exception as e:
        logger.exception(
            f"Failed to send deck_created event: {e}",
            extra={
                "deck_id": deck.id,
                "user_id": deck.owner_id,
            },
        )
    return result.scalars().first()


async def get_deck(session: AsyncSession, deck_id: int) -> Optional[Deck]:
    result = await session.execute(
        select(Deck)
        .where(Deck.id == deck_id)
        .options(
            selectinload(Deck.cards),
            selectinload(Deck.categories),
            selectinload(Deck.tags),
        )
    )
    return result.scalars().first()


async def update_deck(
    session: AsyncSession,
    deck: Deck,
    *,
    title: Optional[str],
    description: Optional[str],
    categories: Optional[List[str]],
    tags: Optional[List[str]],
) -> Deck:
    if title is not None:
        deck.title = title
    if description is not None:
        deck.description = description
    if categories is not None:
        cats = await _get_or_error_categories(session, categories)
        await session.flush()

        # Удаляем старые связи с категориями
        await session.execute(
            delete(deck_categories).where(deck_categories.c.deck_id == deck.id)
        )

        if cats:
            values = [{"deck_id": deck.id, "category_id": c.id} for c in cats]
            await session.execute(insert(deck_categories), values)

    if tags is not None:
        tgs = await _get_or_create_tags(session, tags)
        await session.flush()
        await session.execute(delete(deck_tags).where(deck_tags.c.deck_id == deck.id))
        if tgs:
            values = [{"deck_id": deck.id, "tag_id": t.id} for t in tgs]
            await session.execute(insert(deck_tags), values)

    await session.flush()

    deck_id = deck.id
    session.expunge(deck)

    result = await session.execute(
        select(Deck)
        .where(Deck.id == deck_id)
        .options(
            selectinload(Deck.cards),
            selectinload(Deck.categories),
            selectinload(Deck.tags),
        )
    )
    return result.scalars().first()


async def delete_deck(session: AsyncSession, deck_id: int) -> None:
    await session.execute(delete(Deck).where(Deck.id == deck_id))
