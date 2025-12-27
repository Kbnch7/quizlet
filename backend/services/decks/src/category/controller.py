from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import UserContext, get_current_user
from src.database.core import get_async_db_session

from .models import SCategoryCreate, SCategoryResponse, SCategoryUpdate
from .service import (
    create_category,
    delete_category,
    list_categories,
    update_category,
)

router = APIRouter(prefix="/api/categories", tags=["category"])


@router.get("/", response_model=List[SCategoryResponse])
async def get_categories(
    session: AsyncSession = Depends(get_async_db_session),
):
    categories = await list_categories(session)
    return categories


@router.post("/", response_model=SCategoryResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_category(
    payload: SCategoryCreate,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    if not user.is_manager:
        raise HTTPException(status_code=403, detail="Forbidden")
    cat = await create_category(session, name=payload.name, slug=payload.slug)
    await session.commit()
    return cat


@router.patch("/{category_id}", response_model=SCategoryResponse)
async def admin_update_category(
    category_id: int,
    payload: SCategoryUpdate,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    if not user.is_manager:
        raise HTTPException(status_code=403, detail="Forbidden")
    cat = await update_category(
        session, category_id=category_id, name=payload.name, slug=payload.slug
    )
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await session.commit()
    return cat


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_async_db_session),
    user: Optional[UserContext] = Depends(get_current_user),
):
    if not user.is_manager:
        raise HTTPException(status_code=403, detail="Forbidden")
    ok = await delete_category(session, category_id=category_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Category not found")
    await session.commit()
    return None
