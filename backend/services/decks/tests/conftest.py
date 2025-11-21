import pytest
import os
from typing import AsyncGenerator, Optional
from unittest.mock import Mock, patch

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security import HTTPBearer
from fastapi import HTTPException, status

# Получение базы
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
original_getenv = os.getenv
def mock_getenv(key, default=None):
    if key == "DATABASE_URL":
        return "sqlite+aiosqlite:///:memory:"
    return original_getenv(key, default)

# Временно заменяем os.getenv
os.getenv = mock_getenv

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy import insert
from sqlalchemy.pool import StaticPool

from src.main import app

# Восстанавливаем оригинальный os.getenv
os.getenv = original_getenv

from src.entities import Base, Category, Deck, Card, TestResult, CardResult, deck_categories
from src.auth import UserContext
from src.database.core import get_async_db_session
from src.auth import get_current_user, _mock_fetch_user_info_from_auth_service


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Создает тестовую сессию БД для каждого теста"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Создает тестовый HTTP клиент с переопределенной сессией БД"""
    
    async def override_get_db():
        yield db_session
    
    # Переопределяем get_async_db_session
    app.dependency_overrides[get_async_db_session] = override_get_db
    
    # Переопределяем get_current_user для поддержки тестовой авторизации

    optional_auth_scheme = HTTPBearer(auto_error=False)  # Изменено: auto_error=False
    async def override_get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_auth_scheme)  # Изменено: Optional
    ) -> UserContext | None:
        # Если credentials не передан (нет заголовка), выбрасываем 401
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = credentials.credentials
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if token.endswith("-manager"):
            return UserContext(id=2, is_manager=True)
        if token.startswith("test-token-"):
            try:
                user_id = int(token.split("-")[-1])
                return UserContext(id=user_id, is_manager=False)
            except (ValueError, IndexError):
                pass
        return _mock_fetch_user_info_from_auth_service(token)
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Мокируем storage клиент, чтобы не было проблем с MinIO
    mock_storage_client = Mock()
    mock_storage_client.presigned_get_url = Mock(return_value="http://mock-presigned-get-url")
    mock_storage_client.presigned_put_url = Mock(return_value="http://mock-presigned-put-url")
    mock_storage_client.ensure_bucket = Mock(return_value=None)
    mock_storage_client.copy_object = Mock(return_value=None)
    mock_storage_client.remove_object = Mock(return_value=None)
    
    # Мокируем для всех модулей, которые используют storage
    with patch("src.deck.controller.get_storage_client", return_value=mock_storage_client), \
         patch("src.card.controller.get_storage_client", return_value=mock_storage_client), \
         patch("src.card.service.get_storage_client", return_value=mock_storage_client):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user() -> UserContext:
    """Обычный пользователь"""
    return UserContext(id=1, is_manager=False)


@pytest.fixture
def mock_manager() -> UserContext:
    """Менеджер"""
    return UserContext(id=2, is_manager=True)


@pytest.fixture
def mock_other_user() -> UserContext:
    """Другой пользователь"""
    return UserContext(id=3, is_manager=False)


@pytest.fixture
async def test_category(db_session: AsyncSession) -> Category:
    """Создает тестовую категорию"""
    category = Category(name="Математика", slug="mathematics")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture
async def test_categories(db_session: AsyncSession) -> list[Category]:
    """Создает несколько тестовых категорий"""
    categories = [
        Category(name="История", slug="history"),
        Category(name="Программирование", slug="programming"),
    ]
    for cat in categories:
        db_session.add(cat)
    await db_session.commit()
    for cat in categories:
        await db_session.refresh(cat)
    return categories


@pytest.fixture
async def test_deck(db_session: AsyncSession, test_category: Category, mock_user: UserContext) -> Deck:
    """Создает тестовую колоду"""
    deck = Deck(
        title="Test Deck",
        description="Test Description",
        owner_id=mock_user.id,
    )
    db_session.add(deck)
    await db_session.flush()
    
    # Добавляем категорию
    await db_session.execute(
        insert(deck_categories).values(deck_id=deck.id, category_id=test_category.id)
    )
    
    await db_session.commit()
    await db_session.refresh(deck)
    return deck


@pytest.fixture
async def test_decks(db_session: AsyncSession, test_categories: list[Category], mock_user: UserContext) -> list[Deck]:
    """Создает несколько тестовых колод"""
    decks = [
        Deck(title="Deck 1", description="Description 1", owner_id=mock_user.id),
        Deck(title="Deck 2", description="Description 2", owner_id=mock_user.id),
        Deck(title="Deck 3", description="Description 3", owner_id=2),  # Другой владелец
    ]
    for deck in decks:
        db_session.add(deck)
    await db_session.flush()
    
    # Добавляем категории к первой колоде
    if decks and test_categories:
        await db_session.execute(
            insert(deck_categories).values(deck_id=decks[0].id, category_id=test_categories[0].id)
        )
    
    await db_session.commit()
    for deck in decks:
        await db_session.refresh(deck)
    return decks


def get_auth_headers(user: UserContext) -> dict[str, str]:
    """Генерирует заголовки авторизации для пользователя"""
    if user.is_manager:
        token = "test-token-manager"
    else:
        token = f"test-token-{user.id}"
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_card(db_session: AsyncSession, test_deck: Deck) -> Card:
    """Создает тестовую карточку"""
    card = Card(
        deck_id=test_deck.id,
        front_text="Front text",
        back_text="Back text",
        order_index=0,
    )
    db_session.add(card)
    await db_session.flush()
    # Обновляем cards_amount в колоде
    test_deck.cards_amount += 1
    await db_session.commit()
    await db_session.refresh(card)
    await db_session.refresh(test_deck)
    return card


@pytest.fixture
async def test_cards(db_session: AsyncSession, test_deck: Deck) -> list[Card]:
    """Создает несколько тестовых карточек"""
    cards = [
        Card(deck_id=test_deck.id, front_text="Front 1", back_text="Back 1", order_index=0),
        Card(deck_id=test_deck.id, front_text="Front 2", back_text="Back 2", order_index=1),
        Card(deck_id=test_deck.id, front_text="Front 3", back_text="Back 3", order_index=2),
    ]
    for card in cards:
        db_session.add(card)
    await db_session.flush()
    # Обновляем cards_amount в колоде
    test_deck.cards_amount = len(cards)
    await db_session.commit()
    for card in cards:
        await db_session.refresh(card)
    await db_session.refresh(test_deck)
    return cards


@pytest.fixture
async def test_result_with_cards(
    db_session: AsyncSession, 
    test_deck: Deck, 
    test_cards: list[Card],
    mock_user: UserContext
) -> TestResult:
    """Создает тестовый результат теста с результатами карточек"""
    test_result = TestResult(
        deck_id=test_deck.id,
        user_id=mock_user.id,
        total_time_seconds=120,
        correct_rate=0.75,
    )
    db_session.add(test_result)
    await db_session.flush()
    
    card_results = [
        CardResult(
            test_result_id=test_result.id,
            user_id=mock_user.id,
            card_id=test_cards[0].id,
            correct=True,
            answer_time_seconds=30,
            user_answer="Answer 1"
        ),
        CardResult(
            test_result_id=test_result.id,
            user_id=mock_user.id,
            card_id=test_cards[1].id,
            correct=False,
            answer_time_seconds=40,
            user_answer="Answer 2"
        ),
        CardResult(
            test_result_id=test_result.id,
            user_id=mock_user.id,
            card_id=test_cards[2].id,
            correct=True,
            answer_time_seconds=50,
        ),
    ]
    for cr in card_results:
        db_session.add(cr)
    
    await db_session.commit()
    await db_session.refresh(test_result)
    return test_result
