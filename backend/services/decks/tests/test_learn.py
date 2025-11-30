import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities import Deck, Card
from src.auth import UserContext
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestCreateLearnSession:
    """Тесты для POST /learn/deck/{deck_id}/sessions"""
    
    async def test_create_learn_session_success(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест успешного создания сессии обучения"""
        headers = get_auth_headers(mock_user)
        response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "session" in data
        assert "progress" in data
        assert data["session"]["deck_id"] == test_deck.id
        assert data["session"]["status"] == "active"
        assert data["session"]["total_cards"] == len(test_cards)
        assert data["session"]["learned_cards"] == 0
        assert data["progress"] == 0.0
        assert "started_at" in data["session"]
        assert data["session"]["ended_at"] is None
    
    async def test_create_learn_session_unauthorized(
        self,
        client: AsyncClient,
        test_deck: Deck
    ):
        """Тест создания сессии без авторизации"""
        response = await client.post(f"/learn/deck/{test_deck.id}/sessions")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    async def test_create_learn_session_deck_not_found(
        self,
        client: AsyncClient,
        mock_user: UserContext
    ):
        """Тест создания сессии для несуществующей колоды"""
        headers = get_auth_headers(mock_user)
        response = await client.post(
            "/learn/deck/99999/sessions",
            headers=headers
        )
        assert response.status_code == 404
        assert "Deck not found" in response.json()["detail"]
    
    async def test_create_learn_session_deck_no_cards(
        self,
        client: AsyncClient,
        test_deck: Deck,
        mock_user: UserContext,
        db_session: AsyncSession
    ):
        """Тест создания сессии для колоды без карточек"""
        # Удаляем все карточки из колоды
        await db_session.execute(
            delete(Card).where(Card.deck_id == test_deck.id)
        )
        # Обновляем cards_amount
        test_deck.cards_amount = 0
        await db_session.commit()
        await db_session.refresh(test_deck)
        
        headers = get_auth_headers(mock_user)
        response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        assert response.status_code == 400
        assert "Deck has no cards" in response.json()["detail"]
    
    async def test_create_learn_session_existing_active(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext,
        db_session: AsyncSession
    ):
        """Тест создания сессии, когда уже есть активная сессия"""
        headers = get_auth_headers(mock_user)
        
        # Создаем первую сессию
        response1 = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        assert response1.status_code == 200
        session_id1 = response1.json()["session"]["id"]
        
        # Пытаемся создать вторую сессию
        response2 = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        assert response2.status_code == 200
        session_id2 = response2.json()["session"]["id"]
        
        # Должна вернуться та же сессия
        assert session_id1 == session_id2


@pytest.mark.asyncio
class TestGetLearnSession:
    """Тесты для GET /learn/sessions/{session_id}"""
    
    async def test_get_learn_session_success(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест успешного получения сессии"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Получаем сессию
        response = await client.get(
            f"/learn/sessions/{session_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["deck_id"] == test_deck.id
        assert data["status"] == "active"
        assert data["total_cards"] == len(test_cards)
        assert "started_at" in data
    
    async def test_get_learn_session_not_found(
        self,
        client: AsyncClient,
        mock_user: UserContext
    ):
        """Тест получения несуществующей сессии"""
        headers = get_auth_headers(mock_user)
        response = await client.get(
            "/learn/sessions/99999",
            headers=headers
        )
        assert response.status_code == 404
        assert "Learn session not found" in response.json()["detail"]
    
    async def test_get_learn_session_unauthorized(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест получения сессии без авторизации"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Пытаемся получить без авторизации
        response = await client.get(f"/learn/sessions/{session_id}")
        assert response.status_code == 401
    
    async def test_get_learn_session_other_user(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест получения сессии другого пользователя"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию для первого пользователя
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Пытаемся получить сессию от имени другого пользователя
        other_user = UserContext(id=999, is_manager=False)
        other_headers = get_auth_headers(other_user)
        response = await client.get(
            f"/learn/sessions/{session_id}",
            headers=other_headers
        )
        assert response.status_code == 404
        assert "Learn session not found" in response.json()["detail"]


@pytest.mark.asyncio
class TestGetNextCard:
    """Тесты для GET /learn/sessions/{session_id}/next"""
    
    async def test_get_next_card_success(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест успешного получения следующей карточки"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Получаем следующую карточку
        response = await client.get(
            f"/learn/sessions/{session_id}/next",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "card_id" in data
        assert data["card_id"] is not None
        assert data["card_id"] in [card.id for card in test_cards]
        assert data["learned_cards"] >= 0
        assert data["total_cards"] == len(test_cards)
        assert 0.0 <= data["progress"] <= 1.0
    
    async def test_get_next_card_unauthorized(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест получения следующей карточки без авторизации"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Пытаемся получить без авторизации
        response = await client.get(f"/learn/sessions/{session_id}/next")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    async def test_get_next_card_session_not_found(
        self,
        client: AsyncClient,
        mock_user: UserContext
    ):
        """Тест получения следующей карточки для несуществующей сессии"""
        headers = get_auth_headers(mock_user)
        response = await client.get(
            "/learn/sessions/99999/next",
            headers=headers
        )
        assert response.status_code == 404
        assert "Learn session not found" in response.json()["detail"]
    
    async def test_get_next_card_session_not_active(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext,
        db_session: AsyncSession
    ):
        """Тест получения следующей карточки для завершенной сессии"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Завершаем сессию
        finish_response = await client.post(
            f"/learn/sessions/{session_id}/finish",
            headers=headers
        )
        assert finish_response.status_code == 200
        
        # Пытаемся получить следующую карточку
        response = await client.get(
            f"/learn/sessions/{session_id}/next",
            headers=headers
        )
        assert response.status_code == 400
        assert "Learn session is not active" in response.json()["detail"]


@pytest.mark.asyncio
class TestSubmitAnswer:
    """Тесты для POST /learn/sessions/{session_id}/cards/{card_id}/answer"""
    
    async def test_submit_answer_correct(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест отправки правильного ответа"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Получаем следующую карточку
        next_response = await client.get(
            f"/learn/sessions/{session_id}/next",
            headers=headers
        )
        card_id = next_response.json()["card_id"]
        
        # Отправляем правильный ответ
        payload = {
            "correct": True,
            "answer_time_seconds": 5
        }
        response = await client.post(
            f"/learn/sessions/{session_id}/cards/{card_id}/answer",
            json=payload,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["learned_cards"] >= 0
        assert data["total_cards"] == len(test_cards)
        assert 0.0 <= data["progress"] <= 1.0
        assert isinstance(data["is_completed"], bool)
    
    async def test_submit_answer_incorrect(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест отправки неправильного ответа"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Получаем следующую карточку
        next_response = await client.get(
            f"/learn/sessions/{session_id}/next",
            headers=headers
        )
        card_id = next_response.json()["card_id"]
        
        # Отправляем неправильный ответ
        payload = {
            "correct": False,
            "answer_time_seconds": 10
        }
        response = await client.post(
            f"/learn/sessions/{session_id}/cards/{card_id}/answer",
            json=payload,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["is_completed"] is False
    
    async def test_submit_answer_unauthorized(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест отправки ответа без авторизации"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Получаем следующую карточку
        next_response = await client.get(
            f"/learn/sessions/{session_id}/next",
            headers=headers
        )
        card_id = next_response.json()["card_id"]
        
        # Пытаемся отправить ответ без авторизации
        payload = {
            "correct": True,
            "answer_time_seconds": 5
        }
        response = await client.post(
            f"/learn/sessions/{session_id}/cards/{card_id}/answer",
            json=payload
        )
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    async def test_submit_answer_session_not_found(
        self,
        client: AsyncClient,
        mock_user: UserContext
    ):
        """Тест отправки ответа для несуществующей сессии"""
        headers = get_auth_headers(mock_user)
        payload = {
            "correct": True,
            "answer_time_seconds": 5
        }
        response = await client.post(
            "/learn/sessions/99999/cards/1/answer",
            json=payload,
            headers=headers
        )
        assert response.status_code == 404
        assert "Learn session not found" in response.json()["detail"]
    
    async def test_submit_answer_session_not_active(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест отправки ответа для завершенной сессии"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Получаем следующую карточку
        next_response = await client.get(
            f"/learn/sessions/{session_id}/next",
            headers=headers
        )
        card_id = next_response.json()["card_id"]
        
        # Завершаем сессию
        finish_response = await client.post(
            f"/learn/sessions/{session_id}/finish",
            headers=headers
        )
        assert finish_response.status_code == 200
        
        # Пытаемся отправить ответ
        payload = {
            "correct": True,
            "answer_time_seconds": 5
        }
        response = await client.post(
            f"/learn/sessions/{session_id}/cards/{card_id}/answer",
            json=payload,
            headers=headers
        )
        assert response.status_code == 400
        assert "Learn session is not active" in response.json()["detail"]


@pytest.mark.asyncio
class TestGetSessionProgress:
    """Тесты для GET /learn/sessions/{session_id}/progress"""
    
    async def test_get_session_progress_success(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест успешного получения прогресса сессии"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Получаем прогресс
        response = await client.get(
            f"/learn/sessions/{session_id}/progress",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["learned_cards"] >= 0
        assert data["total_cards"] == len(test_cards)
        assert 0.0 <= data["progress"] <= 1.0
        assert isinstance(data["is_completed"], bool)
    
    async def test_get_session_progress_unauthorized(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест получения прогресса без авторизации"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Пытаемся получить прогресс без авторизации
        response = await client.get(f"/learn/sessions/{session_id}/progress")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    async def test_get_session_progress_not_found(
        self,
        client: AsyncClient,
        mock_user: UserContext
    ):
        """Тест получения прогресса для несуществующей сессии"""
        headers = get_auth_headers(mock_user)
        response = await client.get(
            "/learn/sessions/99999/progress",
            headers=headers
        )
        assert response.status_code == 404
        assert "Learn session not found" in response.json()["detail"]


@pytest.mark.asyncio
class TestFinishLearnSession:
    """Тесты для POST /learn/sessions/{session_id}/finish"""
    
    async def test_finish_learn_session_success(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест успешного завершения сессии"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Завершаем сессию
        response = await client.post(
            f"/learn/sessions/{session_id}/finish",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["is_completed"] is True
        assert 0.0 <= data["progress"] <= 1.0
        
        # Проверяем, что сессия действительно завершена
        get_response = await client.get(
            f"/learn/sessions/{session_id}",
            headers=headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "completed"
        assert get_response.json()["ended_at"] is not None
    
    async def test_finish_learn_session_unauthorized(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест завершения сессии без авторизации"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Пытаемся завершить без авторизации
        response = await client.post(f"/learn/sessions/{session_id}/finish")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    async def test_finish_learn_session_not_found(
        self,
        client: AsyncClient,
        mock_user: UserContext
    ):
        """Тест завершения несуществующей сессии"""
        headers = get_auth_headers(mock_user)
        response = await client.post(
            "/learn/sessions/99999/finish",
            headers=headers
        )
        assert response.status_code == 404
        assert "Learn session not found" in response.json()["detail"]
    
    async def test_finish_learn_session_already_completed(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест повторного завершения уже завершенной сессии"""
        headers = get_auth_headers(mock_user)
        
        # Создаем сессию
        create_response = await client.post(
            f"/learn/deck/{test_deck.id}/sessions",
            headers=headers
        )
        session_id = create_response.json()["session"]["id"]
        
        # Завершаем сессию первый раз
        finish_response1 = await client.post(
            f"/learn/sessions/{session_id}/finish",
            headers=headers
        )
        assert finish_response1.status_code == 200
        
        # Пытаемся завершить еще раз
        finish_response2 = await client.post(
            f"/learn/sessions/{session_id}/finish",
            headers=headers
        )
        # Должно вернуть успех, но сессия уже завершена
        assert finish_response2.status_code == 200
        assert finish_response2.json()["is_completed"] is True

