# tests/conftest.py
import asyncio
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from ..database_client import Base  # импорт скорректируй под свой проект


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
    )
    return engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture()
async def session(test_engine) -> AsyncSession:
    SessionLocal = async_sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with SessionLocal() as s:
        yield s


@pytest_asyncio.fixture()
def user_payload_factory():
    def _make(i=1, **overrides):
        data = {
            "name": f"User{i}",
            "surname": f"Surname{i}",
            "email": f"user{i}@example.com",
            "password": f"strongpass{i}!",
        }
        data.update(overrides)
        return data
    return _make
