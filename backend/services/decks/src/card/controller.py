import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

import src.card.service as service
from src.database.core import get_async_db_session
from .models import SCardCreate, SCardUpdate, SCardResponse, SCardBulkItem, SPresignUploadRequest, SPresignUploadResponse
from src.auth import get_current_user, UserContext, is_authorized_for_resource
from src.entities.deck import Deck
from sqlalchemy import select
from src.utils.storage import get_storage_client, BUCKET_CARDS
from uuid import uuid4


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "miniouser")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "miniopassword")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_BUCKET_CARDS = os.getenv("MINIO_BUCKET_CARDS", "cards")


router = APIRouter(prefix="/deck", tags=["card"])


def _signer_client():
    return get_storage_client()


def _presign_card_images(card):
    """Заменить front_image_url и back_image_url в карточке (Card) на presigned_url"""
    bucket = BUCKET_CARDS
    signer = _signer_client()
    if card.front_image_url and not card.front_image_url.startswith("temp/"):
        card.front_image_url = signer.presigned_get_url(bucket, card.front_image_url)
    if card.back_image_url and not card.back_image_url.startswith("temp/"):
        card.back_image_url = signer.presigned_get_url(bucket, card.back_image_url)


@router.post("/{deck_id}/cards", response_model=SCardResponse)
async def create_card(
    deck_id: int,
    payload: SCardCreate,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    deck = (await session.execute(select(Deck).where(Deck.id == deck_id))).scalars().first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if not is_authorized_for_resource(deck.owner_id, user):
        raise HTTPException(status_code=403, detail="Forbidden")
    card = await service.create_card(session, deck_id=deck_id, **payload.model_dump())
    await session.commit()
    _presign_card_images(card)
    return card


@router.patch("/{deck_id}/cards/{card_id}", response_model=SCardResponse)
async def update_card(
    deck_id: int,
    card_id: int,
    payload: SCardUpdate,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    card = await service.get_card(session, card_id)
    if not card or card.deck_id != deck_id:
        raise HTTPException(status_code=404, detail="Card not found")
    deck = await session.get(Deck, deck_id)
    if deck and not is_authorized_for_resource(deck.owner_id, user):
        raise HTTPException(status_code=403, detail="Forbidden")
    card = await service.update_card(session, card, **payload.model_dump())
    await session.commit()
    _presign_card_images(card)
    return card


@router.delete("/{deck_id}/cards/{card_id}", status_code=204)
async def delete_card(
    deck_id: int,
    card_id: int,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    card = await service.get_card(session, card_id)
    if not card or card.deck_id != deck_id:
        raise HTTPException(status_code=404, detail="Card not found")
    deck = await session.get()
    if deck and not is_authorized_for_resource(deck.owner_id, user):
        raise HTTPException(status_code=403, detail="Forbidden")
    await service.delete_card(session, card_id)
    await session.commit()
    return None


@router.patch("/decks/{deck_id}/cards", status_code=204)
async def bulk_cards(
    deck_id: int,
    items: List[SCardBulkItem] = Body(
        ..., 
        description=(
            "Bulk-операции над карточками. Правила:\n"
            "- Если объект содержит id и поля — обновить существующую карточку.\n"
            "- Если у объекта нет id — создать новую карточку.\n"
            "- Если есть to_delete: true и указан id — удалить карточку."
        ),
        openapi_examples={
            "create": {
                "summary": "Создание",
                "value": [
                    {
                        "front_text": "Q1",
                        "back_text": "A1",
                        "fron_image_url": "temp/{user_id}/uploads/{uuid}.{ext}",
                        "order_index": 0}
                ],
            },
            "update": {
                "summary": "Обновление",
                "value": [
                    {"id": 12, "front_text": "New Q", "order_index": 2}
                ],
            },
            "delete": {
                "summary": "Удаление",
                "value": [
                    {"id": 13, "to_delete": True}
                ],
            },
            "mixed": {
                "summary": "Смешанный набор",
                "value": [
                    {"front_text": "Q2", "back_text": "A2"},
                    {"id": 5, "back_text": "A1 updated"},
                    {"id": 8, "to_delete": True}
                ],
            },
        },
    ),
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    deck = await session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if not is_authorized_for_resource(deck.owner_id, user):
        raise HTTPException(status_code=403, detail="Forbidden")
    errors = await service.bulk_upsert_delete_cards(session, deck_id, items)
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    await session.commit()
    return None


@router.post("/uploads/presign", response_model=SPresignUploadResponse)
async def presign_card_image(
    payload: SPresignUploadRequest,
    user: Optional[UserContext] = Depends(get_current_user),
):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    client = _signer_client()
    client.ensure_bucket(MINIO_BUCKET_CARDS)

    # temp key: temp/{user_id}/uploads/{uuid}.{ext}
    _, _, ext = payload.filename.rpartition(".")
    ext_part = f".{ext}" if ext else ""
    object_key = f"temp/{user.id}/uploads/{uuid4().hex}{ext_part}"
    put_url = client.presigned_put_url(MINIO_BUCKET_CARDS, object_key)
    get_url = client.presigned_get_url(MINIO_BUCKET_CARDS, object_key)
    return SPresignUploadResponse(put_url=put_url, get_url=get_url, object_key=object_key)


