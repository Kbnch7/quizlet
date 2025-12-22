import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth import UserContext
from src.entities import Category, Deck

from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestGetDecks:
    """Тесты для GET /deck/"""

    async def test_get_decks_empty_unauthorized(self, client: AsyncClient):
        """Тест получения пустого списка колод"""
        response = await client.get("/deck/")
        assert response.status_code == 200

    async def test_get_decks_empty(self, client: AsyncClient, mock_user: UserContext):
        """Тест получения пустого списка колод"""
        headers = get_auth_headers(mock_user)
        response = await client.get("/deck/", headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_decks_with_data(
        self, client: AsyncClient, test_decks: list[Deck], mock_user: UserContext
    ):
        """Тест получения списка колод"""
        headers = get_auth_headers(mock_user)
        response = await client.get("/deck/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in deck for deck in data)
        assert all("title" in deck for deck in data)

    async def test_get_decks_with_data_unauthorized(
        self, client: AsyncClient, test_decks: list[Deck]
    ):
        """Тест получения списка колод без авторизации"""
        response = await client.get("/deck/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in deck for deck in data)
        assert all("title" in deck for deck in data)

    async def test_get_decks_filter_by_author(
        self, client: AsyncClient, test_decks: list[Deck], mock_user: UserContext
    ):
        """Тест фильтрации колод по автору"""
        headers = get_auth_headers(mock_user)
        response = await client.get(f"/deck/?author={mock_user.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(deck["owner_id"] == mock_user.id for deck in data)

    async def test_get_decks_filter_by_non_existing_author(
        self, client: AsyncClient, test_decks: list[Deck], mock_user: UserContext
    ):
        """Тест фильтрации колод по автору"""
        headers = get_auth_headers(mock_user)
        response = await client.get(f"/deck/?author={1000}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    async def test_get_decks_filter_by_category(
        self,
        client: AsyncClient,
        test_decks: list[Deck],
        test_categories: list[Category],
        mock_user: UserContext,
    ):
        """Тест фильтрации колод по категории"""
        headers = get_auth_headers(mock_user)
        response = await client.get(
            f"/deck/?category={test_categories[0].slug}", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_decks_with_pagination(
        self, client: AsyncClient, test_decks: list[Deck], mock_user: UserContext
    ):
        """Тест пагинации колод"""
        headers = get_auth_headers(mock_user)
        response = await client.get("/deck/?limit=2", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert "X-Next-Cursor" in response.headers

    async def test_get_decks_with_cursor(
        self, client: AsyncClient, test_decks: list[Deck], mock_user: UserContext
    ):
        """Тест пагинации с курсором"""
        headers = get_auth_headers(mock_user)
        # Получаем первую страницу
        response = await client.get("/deck/?limit=2", headers=headers)
        assert response.status_code == 200
        first_page = response.json()
        assert len(first_page) == 2
        cursor = response.headers.get("X-Next-Cursor")

        # Получаем вторую страницу
        if cursor:
            response = await client.get(
                f"/deck/?limit=2&cursor={cursor}", headers=headers
            )
            assert response.status_code == 200
            second_page = response.json()
            assert len(second_page) >= 1
            # Проверяем, что нет дубликатов
            first_ids = {deck["id"] for deck in first_page}
            second_ids = {deck["id"] for deck in second_page}
            assert first_ids.isdisjoint(second_ids)


@pytest.mark.asyncio
class TestCreateDeck:
    """Тесты для POST /deck/"""

    async def test_create_deck_unauthorized(self, client: AsyncClient):
        """Тест создания колоды без авторизации"""
        payload = {"title": "New Deck", "description": "Description"}
        response = await client.post("/deck/", json=payload)
        assert response.status_code == 401

    async def test_create_deck_success(
        self,
        client: AsyncClient,
        mock_user: UserContext,
        test_categories: list[Category],
    ):
        """Тест успешного создания колоды"""
        headers = get_auth_headers(mock_user)
        payload = {
            "title": "New Deck",
            "description": "Description",
            "categories": [test_categories[0].slug],
            "tags": ["tag1", "tag2"],
        }
        response = await client.post("/deck/", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Deck"
        assert data["description"] == "Description"
        assert data["owner_id"] == mock_user.id
        assert len(data.get("categories", [])) == 1
        assert len(data.get("tags", [])) == 2

    async def test_create_deck_with_unknown_categories(
        self, client: AsyncClient, mock_user: UserContext
    ):
        """Тест создания колоды с несуществующими категориями"""
        headers = get_auth_headers(mock_user)
        payload = {"title": "New Deck", "categories": ["unknown-category"]}
        response = await client.post("/deck/", json=payload, headers=headers)
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Unknown categories" in data["error"]
        assert "unknown-category" in data["slugs"]

    async def test_create_deck_as_manager_for_other_user(
        self,
        client: AsyncClient,
        mock_manager: UserContext,
        test_categories: list[Category],
    ):
        """Тест создания колоды менеджером для другого пользователя"""
        headers = get_auth_headers(mock_manager)
        payload = {
            "title": "Manager's Deck",
            "owner_id": 999,
            "categories": [test_categories[0].slug],
        }
        response = await client.post("/deck/", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["owner_id"] == 999

    async def test_create_deck_as_user_with_owner_id_forbidden(
        self, client: AsyncClient, mock_user: UserContext
    ):
        """Тест создания колоды обычным пользователем с указанием owner_id"""
        headers = get_auth_headers(mock_user)
        payload = {"title": "Deck", "owner_id": 999}
        response = await client.post("/deck/", json=payload, headers=headers)
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]


@pytest.mark.asyncio
class TestGetDeck:
    """Тесты для GET /deck/{deck_id}/"""

    async def test_get_deck_not_found(
        self, client: AsyncClient, mock_user: UserContext
    ):
        """Тест получения несуществующей колоды"""
        headers = get_auth_headers(mock_user)
        response = await client.get("/deck/999/", headers=headers)
        assert response.status_code == 404
        assert "Deck not found" in response.json()["detail"]

    async def test_get_deck_unauthorized(self, client: AsyncClient, test_deck: Deck):
        """Тест получения колоды без авторизации"""
        response = await client.get(f"/deck/{test_deck.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_deck.id
        assert data["title"] == test_deck.title
        assert data["description"] == test_deck.description
        assert "categories" in data
        assert "tags" in data
        assert "cards" in data

    async def test_get_deck_success(
        self, client: AsyncClient, test_deck: Deck, mock_user: UserContext
    ):
        """Тест успешного получения колоды"""
        headers = get_auth_headers(mock_user)
        response = await client.get(f"/deck/{test_deck.id}/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_deck.id
        assert data["title"] == test_deck.title
        assert data["description"] == test_deck.description
        assert "categories" in data
        assert "tags" in data
        assert "cards" in data


@pytest.mark.asyncio
class TestUpdateDeck:
    """Тесты для PATCH /deck/{deck_id}/"""

    async def test_update_deck_not_found(
        self, client: AsyncClient, mock_user: UserContext
    ):
        """Тест обновления несуществующей колоды"""
        headers = get_auth_headers(mock_user)
        payload = {"title": "Updated Title"}
        response = await client.patch("/deck/999/", json=payload, headers=headers)
        assert response.status_code == 404
        assert "Deck not found" in response.json()["detail"]

    async def test_update_deck_unauthorized(self, client: AsyncClient, test_deck: Deck):
        """Тест обновления колоды без авторизации"""
        payload = {"title": "Updated Title"}
        response = await client.patch(f"/deck/{test_deck.id}/", json=payload)
        assert response.status_code == 401
        assert (
            "Not authenticated" in response.json()["detail"]
            or "Unauthenticated" in response.json()["detail"]
        )

    async def test_update_deck_forbidden(
        self, client: AsyncClient, test_deck: Deck, mock_other_user: UserContext
    ):
        """Тест обновления чужой колоды"""
        headers = get_auth_headers(mock_other_user)
        payload = {"title": "Updated Title"}
        response = await client.patch(
            f"/deck/{test_deck.id}/", json=payload, headers=headers
        )
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

    async def test_update_deck_success(
        self,
        client: AsyncClient,
        test_deck: Deck,
        mock_user: UserContext,
        test_categories: list[Category],
        db_session: AsyncSession,
    ):
        """Тест успешного обновления колоды"""
        headers = get_auth_headers(mock_user)
        payload = {
            "title": "Updated Title",
            "description": "Updated Description",
            "categories": [test_categories[1].slug],
        }
        response = await client.patch(
            f"/deck/{test_deck.id}/", json=payload, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated Description"
        # Проверяем, что категории обновились
        category_slugs = [cat["slug"] for cat in data.get("categories", [])]
        assert test_categories[1].slug in category_slugs

    async def test_update_deck_partial(
        self, client: AsyncClient, test_deck: Deck, mock_user: UserContext
    ):
        """Тест частичного обновления колоды"""
        headers = get_auth_headers(mock_user)
        payload = {"title": "Only Title Updated"}
        response = await client.patch(
            f"/deck/{test_deck.id}/", json=payload, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Only Title Updated"
        # Описание должно остаться прежним
        assert data["description"] == test_deck.description

    async def test_update_deck_with_unknown_categories(
        self, client: AsyncClient, test_deck: Deck, mock_user: UserContext
    ):
        """Тест обновления колоды с несуществующими категориями"""
        headers = get_auth_headers(mock_user)
        payload = {"categories": ["unknown-category"]}
        response = await client.patch(
            f"/deck/{test_deck.id}/", json=payload, headers=headers
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Unknown categories" in data["error"]

    async def test_update_deck_as_manager(
        self, client: AsyncClient, test_deck: Deck, mock_manager: UserContext
    ):
        """Тест обновления колоды менеджером"""
        headers = get_auth_headers(mock_manager)
        payload = {"title": "Manager Updated"}
        response = await client.patch(
            f"/deck/{test_deck.id}/", json=payload, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Manager Updated"


@pytest.mark.asyncio
class TestDeleteDeck:
    """Тесты для DELETE /deck/{deck_id}/"""

    async def test_delete_deck_not_found(
        self, client: AsyncClient, mock_user: UserContext
    ):
        """Тест удаления несуществующей колоды"""
        headers = get_auth_headers(mock_user)
        response = await client.delete("/deck/999/", headers=headers)
        assert response.status_code == 404
        assert "Deck not found" in response.json()["detail"]

    async def test_delete_deck_unauthorized(self, client: AsyncClient, test_deck: Deck):
        """Тест удаления колоды без авторизации"""
        response = await client.delete(f"/deck/{test_deck.id}/")
        assert response.status_code == 401
        assert (
            "Not authenticated" in response.json()["detail"]
            or "Unauthenticated" in response.json()["detail"]
        )

    async def test_delete_deck_forbidden(
        self, client: AsyncClient, test_deck: Deck, mock_other_user: UserContext
    ):
        """Тест удаления чужой колоды"""
        headers = get_auth_headers(mock_other_user)
        response = await client.delete(f"/deck/{test_deck.id}/", headers=headers)
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

    async def test_delete_deck_success(
        self, client: AsyncClient, db_session: AsyncSession, mock_user: UserContext
    ):
        """Тест успешного удаления колоды"""
        # Создаем колоду для удаления
        deck = Deck(
            title="To Delete", description="Will be deleted", owner_id=mock_user.id
        )
        db_session.add(deck)
        await db_session.commit()
        await db_session.refresh(deck)

        headers = get_auth_headers(mock_user)
        response = await client.delete(f"/deck/{deck.id}/", headers=headers)
        assert response.status_code == 204

        # Проверяем, что колода удалена
        headers = get_auth_headers(mock_user)
        response = await client.get(f"/deck/{deck.id}/", headers=headers)
        assert response.status_code == 404

    async def test_delete_deck_as_manager(
        self, client: AsyncClient, test_deck: Deck, mock_manager: UserContext
    ):
        """Тест удаления колоды менеджером"""
        headers = get_auth_headers(mock_manager)
        response = await client.delete(f"/deck/{test_deck.id}/", headers=headers)
        assert response.status_code == 204


@pytest.mark.asyncio
class TestDeckStats:
    """Тесты для GET /deck/{deck_id}/stats/"""

    async def test_deck_stats_not_found(
        self, client: AsyncClient, mock_user: UserContext
    ):
        """Тест получения статистики несуществующей колоды"""
        headers = get_auth_headers(mock_user)
        response = await client.get("/deck/999/stats/", headers=headers)
        assert response.status_code == 404
        assert "Deck not found" in response.json()["detail"]

    async def test_deck_stats_unauthorized(self, client: AsyncClient, test_deck: Deck):
        """Тест получения статистики без авторизации"""
        response = await client.get(f"/deck/{test_deck.id}/stats/")
        assert response.status_code == 401
        assert (
            "Not authenticated" in response.json()["detail"]
            or "Unauthenticated" in response.json()["detail"]
        )

    async def test_deck_stats_forbidden(
        self, client: AsyncClient, test_deck: Deck, mock_other_user: UserContext
    ):
        """Тест получения статистики чужой колоды"""
        headers = get_auth_headers(mock_other_user)
        response = await client.get(f"/deck/{test_deck.id}/stats/", headers=headers)
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

    async def test_deck_stats_success(
        self, client: AsyncClient, test_deck: Deck, mock_user: UserContext
    ):
        """Тест успешного получения статистики"""
        headers = get_auth_headers(mock_user)
        response = await client.get(f"/deck/{test_deck.id}/stats/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["deck_id"] == test_deck.id
        assert "total_tests" in data
        assert "avg_score" in data
        assert "correct_rate" in data
        assert "avg_time_seconds" in data
        assert "card_stats" in data

    async def test_deck_stats_as_manager(
        self, client: AsyncClient, test_deck: Deck, mock_manager: UserContext
    ):
        """Тест получения статистики менеджером"""
        headers = get_auth_headers(mock_manager)
        response = await client.get(f"/deck/{test_deck.id}/stats/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["deck_id"] == test_deck.id
