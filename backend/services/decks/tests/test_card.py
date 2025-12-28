import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth import UserContext
from src.entities import Card, Deck

from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestCreateCard:
    """Тесты для POST /deck/{deck_id}/cards"""

    async def test_create_card_unauthorized(self, client: AsyncClient, test_deck: Deck):
        """Тест создания карточки без авторизации"""
        payload = {"front_text": "Front", "back_text": "Back"}
        response = await client.post(f"/deck/{test_deck.id}/cards", json=payload)
        assert response.status_code == 401
        assert (
            "Not authenticated" in response.json()["detail"]
            or "Unauthenticated" in response.json()["detail"]
        )

    async def test_create_card_deck_not_found(
        self, client: AsyncClient, mock_user: UserContext
    ):
        """Тест создания карточки для несуществующей колоды"""
        headers = get_auth_headers(mock_user)
        payload = {"front_text": "Front", "back_text": "Back"}
        response = await client.post("/deck/999/cards", json=payload, headers=headers)
        assert response.status_code == 404
        assert "Deck not found" in response.json()["detail"]

    async def test_create_card_forbidden(
        self, client: AsyncClient, test_deck: Deck, mock_other_user: UserContext
    ):
        """Тест создания карточки для чужой колоды"""
        headers = get_auth_headers(mock_other_user)
        payload = {"front_text": "Front", "back_text": "Back"}
        response = await client.post(
            f"/deck/{test_deck.id}/cards", json=payload, headers=headers
        )
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

    async def test_create_card_success(
        self, client: AsyncClient, test_deck: Deck, mock_user: UserContext
    ):
        """Тест успешного создания карточки"""
        headers = get_auth_headers(mock_user)
        payload = {"front_text": "Question",
                   "back_text": "Answer", "order_index": 0}
        response = await client.post(
            f"/deck/{test_deck.id}/cards", json=payload, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["front_text"] == "Question"
        assert data["back_text"] == "Answer"
        assert data["deck_id"] == test_deck.id
        assert data["order_index"] == 0

    async def test_create_card_with_images(
        self, client: AsyncClient, test_deck: Deck, mock_user: UserContext
    ):
        """Тест создания карточки с изображениями"""
        headers = get_auth_headers(mock_user)
        payload = {
            "front_text": "Question",
            "back_text": "Answer",
            "front_image_url": "temp/1/uploads/image1.jpg",
            "back_image_url": "temp/1/uploads/image2.jpg",
        }
        response = await client.post(
            f"/deck/{test_deck.id}/cards", json=payload, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["front_text"] == "Question"
        assert data["back_text"] == "Answer"
        # Проверяем, что URL изображений присутствуют (могут быть presigned)
        assert "front_image_url" in data or data.get(
            "front_image_url") is not None
        assert "back_image_url" in data or data.get(
            "back_image_url") is not None


@pytest.mark.asyncio
class TestUpdateCard:
    """Тесты для PATCH /deck/{deck_id}/cards/{card_id}"""

    async def test_update_card_unauthorized(
        self, client: AsyncClient, test_deck: Deck, test_card: Card
    ):
        """Тест обновления карточки без авторизации"""
        payload = {"front_text": "Updated Front"}
        response = await client.patch(
            f"/deck/{test_deck.id}/cards/{test_card.id}", json=payload
        )
        assert response.status_code == 401
        assert (
            "Not authenticated" in response.json()["detail"]
            or "Unauthenticated" in response.json()["detail"]
        )

    async def test_update_card_not_found(
        self, client: AsyncClient, test_deck: Deck, mock_user: UserContext
    ):
        """Тест обновления несуществующей карточки"""
        headers = get_auth_headers(mock_user)
        payload = {"front_text": "Updated Front"}
        response = await client.patch(
            f"/deck/{test_deck.id}/cards/999", json=payload, headers=headers
        )
        assert response.status_code == 404
        assert "Card not found" in response.json()["detail"]

    async def test_update_card_wrong_deck(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_card: Card,
        mock_user: UserContext,
    ):
        """Тест обновления карточки с неправильным deck_id"""
        headers = get_auth_headers(mock_user)
        payload = {"front_text": "Updated Front"}
        response = await client.patch(
            f"/deck/999/cards/{test_card.id}", json=payload, headers=headers
        )
        assert response.status_code == 404
        assert "Card not found" in response.json()["detail"]

    async def test_update_card_forbidden(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_card: Card,
        mock_other_user: UserContext,
    ):
        """Тест обновления карточки в чужой колоде"""
        headers = get_auth_headers(mock_other_user)
        payload = {"front_text": "Updated Front"}
        response = await client.patch(
            f"/deck/{test_deck.id}/cards/{test_card.id}", json=payload, headers=headers
        )
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

    async def test_update_card_success(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_card: Card,
        mock_user: UserContext,
    ):
        """Тест успешного обновления карточки"""
        headers = get_auth_headers(mock_user)
        payload = {
            "front_text": "Updated Front",
            "back_text": "Updated Back",
            "order_index": 5,
        }
        response = await client.patch(
            f"/deck/{test_deck.id}/cards/{test_card.id}", json=payload, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["front_text"] == "Updated Front"
        assert data["back_text"] == "Updated Back"
        assert data["order_index"] == 5

    async def test_update_card_partial(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_card: Card,
        mock_user: UserContext,
    ):
        """Тест частичного обновления карточки"""
        headers = get_auth_headers(mock_user)
        payload = {"front_text": "Only Front Updated"}
        response = await client.patch(
            f"/deck/{test_deck.id}/cards/{test_card.id}", json=payload, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["front_text"] == "Only Front Updated"
        # Остальные поля должны остаться прежними
        assert data["back_text"] == test_card.back_text


@pytest.mark.asyncio
class TestDeleteCard:
    """Тесты для DELETE /deck/{deck_id}/cards/{card_id}"""

    async def test_delete_card_unauthorized(
        self, client: AsyncClient, test_deck: Deck, test_card: Card
    ):
        """Тест удаления карточки без авторизации"""
        response = await client.delete(f"/deck/{test_deck.id}/cards/{test_card.id}")
        assert response.status_code == 401
        assert (
            "Not authenticated" in response.json()["detail"]
            or "Unauthenticated" in response.json()["detail"]
        )

    async def test_delete_card_not_found(
        self, client: AsyncClient, test_deck: Deck, mock_user: UserContext
    ):
        """Тест удаления несуществующей карточки"""
        headers = get_auth_headers(mock_user)
        response = await client.delete(
            f"/deck/{test_deck.id}/cards/999", headers=headers
        )
        assert response.status_code == 404
        assert "Card not found" in response.json()["detail"]

    async def test_delete_card_wrong_deck(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_card: Card,
        mock_user: UserContext,
    ):
        """Тест удаления карточки с неправильным deck_id"""
        headers = get_auth_headers(mock_user)
        response = await client.delete(
            f"/deck/999/cards/{test_card.id}", headers=headers
        )
        assert response.status_code == 404
        assert "Card not found" in response.json()["detail"]

    async def test_delete_card_forbidden(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_card: Card,
        mock_other_user: UserContext,
    ):
        """Тест удаления карточки из чужой колоды"""
        headers = get_auth_headers(mock_other_user)
        response = await client.delete(
            f"/deck/{test_deck.id}/cards/{test_card.id}", headers=headers
        )
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

    async def test_delete_card_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_deck: Deck,
        mock_user: UserContext,
    ):
        """Тест успешного удаления карточки"""
        card = Card(
            deck_id=test_deck.id,
            front_text="To Delete",
            back_text="Will be deleted",
            order_index=0,
        )
        db_session.add(card)
        await db_session.commit()
        await db_session.refresh(card)

        headers = get_auth_headers(mock_user)
        response = await client.delete(
            f"/deck/{test_deck.id}/cards/{card.id}", headers=headers
        )
        assert response.status_code == 204

    async def test_delete_card_as_manager(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_card: Card,
        mock_manager: UserContext,
    ):
        """Тест удаления карточки менеджером"""
        headers = get_auth_headers(mock_manager)
        response = await client.delete(
            f"/deck/{test_deck.id}/cards/{test_card.id}", headers=headers
        )
        assert response.status_code == 204


@pytest.mark.asyncio
class TestBulkCards:
    """Тесты для PATCH /decks/{deck_id}/cards"""

    async def test_bulk_cards_unauthorized(self, client: AsyncClient, test_deck: Deck):
        """Тест bulk операций без авторизации"""
        payload = [{"front_text": "Q1", "back_text": "A1"}]
        response = await client.patch(f"/deck/decks/{test_deck.id}/cards", json=payload)
        assert response.status_code == 401
        assert (
            "Not authenticated" in response.json()["detail"]
            or "Unauthenticated" in response.json()["detail"]
        )

    async def test_bulk_cards_deck_not_found(
        self, client: AsyncClient, mock_user: UserContext
    ):
        """Тест bulk операций для несуществующей колоды"""
        headers = get_auth_headers(mock_user)
        payload = [{"front_text": "Q1", "back_text": "A1"}]
        response = await client.patch(
            "/deck/decks/999/cards", json=payload, headers=headers
        )
        assert response.status_code == 404
        assert "Deck not found" in response.json()["detail"]

    async def test_bulk_cards_forbidden(
        self, client: AsyncClient, test_deck: Deck, mock_other_user: UserContext
    ):
        """Тест bulk операций для чужой колоды"""
        headers = get_auth_headers(mock_other_user)
        payload = [{"front_text": "Q1", "back_text": "A1"}]
        response = await client.patch(
            f"/deck/decks/{test_deck.id}/cards", json=payload, headers=headers
        )
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

    async def test_bulk_cards_create(
        self, client: AsyncClient, test_deck: Deck, mock_user: UserContext
    ):
        """Тест bulk создания карточек"""
        headers = get_auth_headers(mock_user)
        payload = [
            {"front_text": "Q1", "back_text": "A1", "order_index": 0},
            {"front_text": "Q2", "back_text": "A2", "order_index": 1},
        ]
        response = await client.patch(
            f"/deck/decks/{test_deck.id}/cards", json=payload, headers=headers
        )
        assert response.status_code == 204

    async def test_bulk_cards_update(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext,
    ):
        """Тест bulk обновления карточек"""
        headers = get_auth_headers(mock_user)
        payload = [
            {"id": test_cards[0].id, "front_text": "Updated Q1"},
            {"id": test_cards[1].id, "back_text": "Updated A2"},
        ]
        response = await client.patch(
            f"/deck/decks/{test_deck.id}/cards", json=payload, headers=headers
        )
        assert response.status_code == 204

    async def test_bulk_cards_delete(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext,
    ):
        """Тест bulk удаления карточек"""
        headers = get_auth_headers(mock_user)
        payload = [
            {"id": test_cards[0].id, "to_delete": True},
            {"id": test_cards[1].id, "to_delete": True},
        ]
        response = await client.patch(
            f"/deck/decks/{test_deck.id}/cards", json=payload, headers=headers
        )
        assert response.status_code == 204

    async def test_bulk_cards_mixed(
        self,
        client: AsyncClient,
        test_deck: Deck,
        test_cards: list[Card],
        mock_user: UserContext,
    ):
        """Тест смешанных bulk операций"""
        headers = get_auth_headers(mock_user)
        payload = [
            {"front_text": "New Q", "back_text": "New A"},  # создать
            {"id": test_cards[0].id, "front_text": "Updated Q"},  # обновить
            {"id": test_cards[1].id, "to_delete": True},  # удалить
        ]
        response = await client.patch(
            f"/deck/decks/{test_deck.id}/cards", json=payload, headers=headers
        )
        assert response.status_code == 204

    async def test_bulk_cards_error_missing_id_for_delete(
        self, client: AsyncClient, test_deck: Deck, mock_user: UserContext
    ):
        """Тест ошибки при удалении без id"""
        headers = get_auth_headers(mock_user)
        payload = [{"to_delete": True}]  # нет id
        response = await client.patch(
            f"/deck/decks/{test_deck.id}/cards", json=payload, headers=headers
        )
        assert response.status_code == 400
        data = response.json()
        assert "errors" in data["detail"]

    async def test_bulk_cards_error_missing_text_for_create(
        self, client: AsyncClient, test_deck: Deck, mock_user: UserContext
    ):
        """Тест ошибки при создании без обязательных полей"""
        headers = get_auth_headers(mock_user)
        payload = [{"front_text": "Only front"}]  # нет back_text
        response = await client.patch(
            f"/deck/decks/{test_deck.id}/cards", json=payload, headers=headers
        )
        assert response.status_code == 400
        data = response.json()
        assert "errors" in data["detail"]


@pytest.mark.asyncio
class TestPresignUpload:
    """Тесты для POST /uploads/presign"""

    async def test_presign_upload_unauthorized(self, client: AsyncClient):
        """Тест получения presigned URL без авторизации"""
        payload = {"filename": "image.jpg"}
        response = await client.post("/deck/uploads/presign", json=payload)
        assert response.status_code == 401

    async def test_presign_upload_success(
        self, client: AsyncClient, mock_user: UserContext
    ):
        """Тест успешного получения presigned URL"""
        headers = get_auth_headers(mock_user)
        payload = {"filename": "image.jpg"}
        response = await client.post(
            "/deck/uploads/presign", json=payload, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "put_url" in data
        assert "get_url" in data
        assert "object_key" in data
        assert data["object_key"].startswith("temp/")
        assert str(mock_user.id) in data["object_key"]

    async def test_presign_upload_different_extensions(
        self, client: AsyncClient, mock_user: UserContext
    ):
        """Тест получения presigned URL для разных расширений"""
        headers = get_auth_headers(mock_user)
        extensions = ["jpg", "png", "gif", "webp"]
        for ext in extensions:
            payload = {"filename": f"image.{ext}"}
            response = await client.post(
                "/deck/uploads/presign", json=payload, headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["object_key"].endswith(f".{ext}")
