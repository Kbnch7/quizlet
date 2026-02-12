import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities import Deck, Card, TestResult, CardResult
from src.auth import UserContext
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestCreateTestResult:
    """Тесты для POST /deck/{deck_id}/results"""
    
    async def test_create_result_unauthorized(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест создания результата теста без авторизации"""
        payload = {
            "user_id": mock_user.id,
            "total_time_seconds": 120,
            "correct_rate": 0.75,
            "card_results": [
                {"card_id": test_cards[0].id, "correct": True, "answer_time_seconds": 30}
            ]
        }
        response = await client.post(f"/deck/{test_deck.id}/results", json=payload)
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    async def test_create_result_no_user_id_in_payload(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест создания результата без user_id в payload (должна быть валидация)"""
        headers = get_auth_headers(mock_user)
        payload = {
            "total_time_seconds": 120,
            "correct_rate": 0.75,
            "card_results": [
                {"card_id": test_cards[0].id, "correct": True, "answer_time_seconds": 30}
            ]
        }
        response = await client.post(f"/deck/{test_deck.id}/results", json=payload, headers=headers)
        # Должна быть ошибка валидации, так как user_id обязателен
        assert response.status_code == 422
    
    async def test_create_result_deck_not_found(
        self, 
        client: AsyncClient, 
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест создания результата для несуществующей колоды"""
        headers = get_auth_headers(mock_user)
        payload = {
            "user_id": mock_user.id,
            "total_time_seconds": 120,
            "correct_rate": 0.75,
            "card_results": [
                {"card_id": test_cards[0].id, "correct": True, "answer_time_seconds": 30}
            ]
        }
        response = await client.post("/deck/999/results", json=payload, headers=headers)
        assert response.status_code == 404
        assert "Deck not found" in response.json()["detail"]
    
    async def test_create_result_forbidden_other_user(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext,
        mock_other_user: UserContext
    ):
        """Тест создания результата для другого пользователя (не менеджер)"""
        headers = get_auth_headers(mock_user)
        payload = {
            "user_id": mock_other_user.id,  # Пытаемся создать результат для другого пользователя
            "total_time_seconds": 120,
            "correct_rate": 0.75,
            "card_results": [
                {"card_id": test_cards[0].id, "correct": True, "answer_time_seconds": 30}
            ]
        }
        response = await client.post(f"/deck/{test_deck.id}/results", json=payload, headers=headers)
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]
    
    async def test_create_result_invalid_card_ids(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        mock_user: UserContext
    ):
        """Тест создания результата с несуществующими card_id"""
        headers = get_auth_headers(mock_user)
        payload = {
            "user_id": mock_user.id,
            "total_time_seconds": 120,
            "correct_rate": 0.75,
            "card_results": [
                {"card_id": 999, "correct": True, "answer_time_seconds": 30}  # Несуществующая карточка
            ]
        }
        response = await client.post(f"/deck/{test_deck.id}/results", json=payload, headers=headers)
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"]
        assert "invalid_card_ids" in data["detail"]
    
    async def test_create_result_wrong_deck_cards(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        db_session: AsyncSession,
        mock_user: UserContext
    ):
        """Тест создания результата с карточками из другой колоды"""
        # Создаем другую колоду с карточкой
        other_deck = Deck(
            title="Other Deck",
            description="Other",
            owner_id=mock_user.id
        )
        db_session.add(other_deck)
        await db_session.flush()
        
        other_card = Card(
            deck_id=other_deck.id,
            front_text="Other Front",
            back_text="Other Back",
            order_index=0
        )
        db_session.add(other_card)
        await db_session.commit()
        await db_session.refresh(other_card)
        
        headers = get_auth_headers(mock_user)
        payload = {
            "user_id": mock_user.id,
            "total_time_seconds": 120,
            "correct_rate": 0.75,
            "card_results": [
                {"card_id": other_card.id, "correct": True, "answer_time_seconds": 30}
            ]
        }
        response = await client.post(f"/deck/{test_deck.id}/results", json=payload, headers=headers)
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"]
        assert "invalid_card_ids" in data["detail"]
    
    async def test_create_result_success(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext
    ):
        """Тест успешного создания результата теста"""
        headers = get_auth_headers(mock_user)
        payload = {
            "user_id": mock_user.id,
            "total_time_seconds": 120,
            "correct_rate": 0.75,
            "card_results": [
                {
                    "card_id": test_cards[0].id,
                    "correct": True,
                    "answer_time_seconds": 30,
                    "user_answer": "Answer 1"
                },
                {
                    "card_id": test_cards[1].id,
                    "correct": False,
                    "answer_time_seconds": 40,
                    "user_answer": "Answer 2"
                }
            ]
        }
        response = await client.post(f"/deck/{test_deck.id}/results", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["deck_id"] == test_deck.id
        assert data["user_id"] == mock_user.id
        assert data["total_time_seconds"] == 120
        assert data["correct_rate"] == 0.75
        assert len(data["card_results"]) == 2
        assert data["card_results"][0]["card_id"] == test_cards[0].id
        assert data["card_results"][0]["correct"] is True
        assert data["card_results"][1]["card_id"] == test_cards[1].id
        assert data["card_results"][1]["correct"] is False
    
    async def test_create_result_as_manager_for_other_user(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        test_cards: list[Card],
        mock_manager: UserContext,
        mock_user: UserContext
    ):
        """Тест создания результата менеджером для другого пользователя"""
        headers = get_auth_headers(mock_manager)
        payload = {
            "user_id": mock_user.id,  # Менеджер может создавать результаты для других
            "total_time_seconds": 120,
            "correct_rate": 0.75,
            "card_results": [
                {"card_id": test_cards[0].id, "correct": True, "answer_time_seconds": 30}
            ]
        }
        response = await client.post(f"/deck/{test_deck.id}/results", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == mock_user.id
    
    async def test_create_result_empty_card_results(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        mock_user: UserContext
    ):
        """Тест создания результата с пустым списком card_results"""
        headers = get_auth_headers(mock_user)
        payload = {
            "user_id": mock_user.id,
            "total_time_seconds": 120,
            "correct_rate": 0.75,
            "card_results": []
        }
        response = await client.post(f"/deck/{test_deck.id}/results", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["deck_id"] == test_deck.id
        assert data["user_id"] == mock_user.id
        assert len(data["card_results"]) == 0


@pytest.mark.asyncio
class TestListTestResults:
    """Тесты для GET /deck/{deck_id}/results"""
    
    async def test_list_results_unauthorized(
        self, 
        client: AsyncClient, 
        test_deck: Deck
    ):
        """Тест получения списка результатов без авторизации"""
        response = await client.get(f"/deck/{test_deck.id}/results")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    async def test_list_results_deck_not_found(
        self, 
        client: AsyncClient, 
        mock_user: UserContext
    ):
        """Тест получения результатов для несуществующей колоды"""
        headers = get_auth_headers(mock_user)
        response = await client.get("/deck/999/results", headers=headers)
        assert response.status_code == 404
        assert "Deck not found" in response.json()["detail"]
    
    async def test_list_results_empty(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        mock_user: UserContext
    ):
        """Тест получения пустого списка результатов"""
        headers = get_auth_headers(mock_user)
        response = await client.get(f"/deck/{test_deck.id}/results", headers=headers)
        assert response.status_code == 200
        assert response.json() == []
    
    async def test_list_results_success(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        test_result_with_cards: TestResult,
        mock_user: UserContext
    ):
        """Тест успешного получения списка результатов"""
        headers = get_auth_headers(mock_user)
        response = await client.get(f"/deck/{test_deck.id}/results", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all("id" in result for result in data)
        assert all("deck_id" in result for result in data)
        assert all("user_id" in result for result in data)
        assert all("card_results" in result for result in data)
    
    async def test_list_results_filter_by_user_id_owner(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        test_result_with_cards: TestResult,
        mock_user: UserContext,
        db_session: AsyncSession,
        test_cards: list[Card]
    ):
        """Тест фильтрации результатов по user_id (владелец колоды)"""
        # Создаем результат для другого пользователя
        other_result = TestResult(
            deck_id=test_deck.id,
            user_id=999,
            total_time_seconds=60,
            correct_rate=0.5,
        )
        db_session.add(other_result)
        await db_session.flush()
        
        card_result = CardResult(
            test_result_id=other_result.id,
            user_id=999,
            card_id=test_cards[0].id,
            correct=True,
            answer_time_seconds=20,
        )
        db_session.add(card_result)
        await db_session.commit()
        
        headers = get_auth_headers(mock_user)
        # Владелец может фильтровать по любому user_id
        response = await client.get(
            f"/deck/{test_deck.id}/results?user_id={mock_user.id}", 
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(result["user_id"] == mock_user.id for result in data)
    
    async def test_list_results_filter_by_user_id_non_owner(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        test_result_with_cards: TestResult,
        mock_other_user: UserContext,
        db_session: AsyncSession,
        test_cards: list[Card]
    ):
        """Тест фильтрации результатов по user_id (не владелец колоды)"""
        # Создаем результат для другого пользователя
        other_result = TestResult(
            deck_id=test_deck.id,
            user_id=999,
            total_time_seconds=60,
            correct_rate=0.5,
        )
        db_session.add(other_result)
        await db_session.flush()
        
        card_result = CardResult(
            test_result_id=other_result.id,
            user_id=999,
            card_id=test_cards[0].id,
            correct=True,
            answer_time_seconds=20,
        )
        db_session.add(card_result)
        await db_session.commit()
        
        headers = get_auth_headers(mock_other_user)
        # Не владелец видит только свои результаты
        response = await client.get(f"/deck/{test_deck.id}/results", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Не владелец не должен видеть результаты других пользователей
        # Но может видеть свои, если они есть
        assert all(result["user_id"] == mock_other_user.id for result in data)
    
    async def test_list_results_with_pagination(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        test_result_with_cards: TestResult,
        mock_user: UserContext,
        db_session: AsyncSession,
        test_cards: list[Card]
    ):
        """Тест пагинации результатов"""
        # Создаем еще несколько результатов
        for i in range(3):
            result = TestResult(
                deck_id=test_deck.id,
                user_id=mock_user.id,
                total_time_seconds=60 + i * 10,
                correct_rate=0.5 + i * 0.1,
            )
            db_session.add(result)
            await db_session.flush()
            
            card_result = CardResult(
                test_result_id=result.id,
                user_id=mock_user.id,
                card_id=test_cards[0].id,
                correct=True,
                answer_time_seconds=20,
            )
            db_session.add(card_result)
        
        await db_session.commit()
        
        headers = get_auth_headers(mock_user)
        response = await client.get(
            f"/deck/{test_deck.id}/results?limit=2", 
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert "X-Next-Cursor" in response.headers
    
    async def test_list_results_with_cursor(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        test_result_with_cards: TestResult,
        mock_user: UserContext,
        db_session: AsyncSession,
        test_cards: list[Card]
    ):
        """Тест пагинации с курсором"""
        # Создаем еще несколько результатов
        for i in range(3):
            result = TestResult(
                deck_id=test_deck.id,
                user_id=mock_user.id,
                total_time_seconds=60 + i * 10,
                correct_rate=0.5 + i * 0.1,
            )
            db_session.add(result)
            await db_session.flush()
            
            card_result = CardResult(
                test_result_id=result.id,
                user_id=mock_user.id,
                card_id=test_cards[0].id,
                correct=True,
                answer_time_seconds=20,
            )
            db_session.add(card_result)
        
        await db_session.commit()
        
        headers = get_auth_headers(mock_user)
        # Получаем первую страницу
        response = await client.get(
            f"/deck/{test_deck.id}/results?limit=2", 
            headers=headers
        )
        assert response.status_code == 200
        first_page = response.json()
        assert len(first_page) == 2
        cursor = response.headers.get("X-Next-Cursor")
        
        # Получаем вторую страницу
        if cursor:
            response = await client.get(
                f"/deck/{test_deck.id}/results?limit=2&cursor={cursor}", 
                headers=headers
            )
            assert response.status_code == 200
            second_page = response.json()
            assert len(second_page) >= 1
            # Проверяем, что нет дубликатов
            first_ids = {result["id"] for result in first_page}
            second_ids = {result["id"] for result in second_page}
            assert first_ids.isdisjoint(second_ids)
    
    async def test_list_results_limit_validation(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        mock_user: UserContext
    ):
        """Тест валидации параметра limit"""
        headers = get_auth_headers(mock_user)
        # limit должен быть >= 1
        response = await client.get(
            f"/deck/{test_deck.id}/results?limit=0", 
            headers=headers
        )
        assert response.status_code == 422
        
        # limit должен быть <= 100
        response = await client.get(
            f"/deck/{test_deck.id}/results?limit=101", 
            headers=headers
        )
        assert response.status_code == 422
    
    async def test_list_results_manager_can_see_all(
        self, 
        client: AsyncClient, 
        test_deck: Deck,
        test_result_with_cards: TestResult,
        mock_user: UserContext,
        mock_manager: UserContext,
        db_session: AsyncSession,
        test_cards: list[Card]
    ):
        """Тест, что менеджер может видеть все результаты"""
        # Создаем результат для другого пользователя
        other_result = TestResult(
            deck_id=test_deck.id,
            user_id=999,
            total_time_seconds=60,
            correct_rate=0.5,
        )
        db_session.add(other_result)
        await db_session.flush()
        
        card_result = CardResult(
            test_result_id=other_result.id,
            user_id=999,
            card_id=test_cards[0].id,
            correct=True,
            answer_time_seconds=20,
        )
        db_session.add(card_result)
        await db_session.commit()
        
        headers = get_auth_headers(mock_manager)
        # Менеджер должен видеть все результаты
        response = await client.get(f"/deck/{test_deck.id}/results", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Менеджер видит результаты всех пользователей
        user_ids = {result["user_id"] for result in data}
        assert mock_user.id in user_ids or 999 in user_ids



