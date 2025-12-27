import asyncio
import os

import dotenv
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from src.entities import *

dotenv.load_dotenv()
DB_URL = os.getenv("DB_URL")

engine = create_async_engine(DB_URL)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.drop_all(
                sync_conn, checkfirst=True)
        )
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        default_categories = [
            {"name": "Математика", "slug": "mathematics"},
            {"name": "История", "slug": "history"},
            {"name": "Программирование", "slug": "programming"},
            {"name": "Физика", "slug": "physics"},
            {"name": "Химия", "slug": "chemistry"},
            {"name": "Биология", "slug": "biology"},
            {"name": "Литература", "slug": "literature"},
            {"name": "География", "slug": "geography"},
            {"name": "Другое", "slug": "other"},
        ]

        for cat_data in default_categories:
            category = Category(name=cat_data["name"], slug=cat_data["slug"])
            session.add(category)

        await session.commit()
        print("Success")


if __name__ == "__main__":
    asyncio.run(init_db())
