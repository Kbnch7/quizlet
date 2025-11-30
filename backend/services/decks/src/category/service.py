from typing import List, Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities import Category
from src.exceptions import CategoryAlreadyExistsError


async def list_categories(session: AsyncSession) -> List[Category]:
    result = await session.execute(
        select(Category).order_by(Category.name.asc())
    )
    return result.scalars().all()


async def create_category(
    session: AsyncSession, *, name: str, slug: str
) -> Category:
    result = await session.execute(
        select(Category).where(
            (Category.name == name) | (Category.slug == slug)
        )
    )
    existing = result.scalars().first()
    if existing:
        if existing.name == name:
            raise CategoryAlreadyExistsError(field="name", value=name)
        if existing.slug == slug:
            raise CategoryAlreadyExistsError(field="slug", value=slug)

    cat = Category(name=name, slug=slug)
    session.add(cat)
    await session.flush()
    await session.refresh(cat)
    return cat


async def update_category(
    session: AsyncSession,
    *,
    category_id: int,
    name: Optional[str],
    slug: Optional[str]
) -> Optional[Category]:
    cat = await session.get(Category, category_id)
    if not cat:
        return None

    if name is not None or slug is not None:
        conditions = []
        if name is not None:
            conditions.append(Category.name == name)
        if slug is not None:
            conditions.append(Category.slug == slug)

        if conditions:
            result = await session.execute(
                select(Category).where(
                    or_(*conditions) & (Category.id != category_id)
                )
            )
            existing = result.scalars().first()
            if existing:
                if name is not None and existing.name == name:
                    raise CategoryAlreadyExistsError(field="name", value=name)
                if slug is not None and existing.slug == slug:
                    raise CategoryAlreadyExistsError(field="slug", value=slug)

    if name is not None:
        cat.name = name
    if slug is not None:
        cat.slug = slug
    await session.flush()
    await session.refresh(cat)
    return cat


async def delete_category(session: AsyncSession, *, category_id: int) -> bool:
    cat = await session.get(Category, category_id)
    if not cat:
        return False
    await session.delete(cat)
    return True
