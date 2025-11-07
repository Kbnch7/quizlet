from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.category import Category


async def list_categories(session: AsyncSession) -> List[Category]:
    result = await session.execute(select(Category).order_by(Category.name.asc()))
    return result.scalars().all()


async def create_category(session: AsyncSession, *, name: str, slug: str) -> Category:
    cat = Category(name=name, slug=slug)
    session.add(cat)
    await session.flush()
    await session.refresh(cat)
    return cat


async def update_category(session: AsyncSession, *, category_id: int, name: Optional[str], slug: Optional[str]) -> Optional[Category]:
    cat = await session.get(Category, category_id)
    if not cat:
        return None
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


