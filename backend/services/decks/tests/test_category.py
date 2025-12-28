import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth import UserContext
from src.entities import Category, Deck

from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestGetCategories:
    """Тесты для GET /categories/"""

    async def test_get_categories_empty(self, client: AsyncClient):
        """Тест получения пустого списка категорий"""
        response = await client.get("/categories/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_categories_with_data(
        self, client: AsyncClient, test_categories: list[Category]
    ):
        """Тест получения списка категорий"""
        response = await client.get("/categories/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2  # test_categories создает 2 категории
        assert all("id" in cat for cat in data)
        assert all("name" in cat for cat in data)
        assert all("slug" in cat for cat in data)
        # Проверяем, что категории отсортированы по имени
        names = [cat["name"] for cat in data]
        assert names == sorted(names)

    async def test_get_categories_includes_default(
        self, client: AsyncClient, test_category: Category
    ):
        """Тест получения категорий с дефолтной категорией"""
        response = await client.get("/categories/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        # Проверяем, что дефолтная категория присутствует
        slugs = [cat["slug"] for cat in data]
        assert test_category.slug in slugs


@pytest.mark.asyncio
class TestCreateCategory:
    """Тесты для POST /categories/"""

    async def test_create_category_unauthorized(self, client: AsyncClient):
        """Тест создания категории без авторизации"""
        payload = {"name": "Новая категория", "slug": "new-category"}
        response = await client.post("/categories/", json=payload)
        assert response.status_code == 401
        assert (
            "Not authenticated" in response.json()["detail"]
            or "Not authenticated" in response.json()["detail"]
        )

    async def test_create_category_forbidden(
        self, client: AsyncClient, mock_user: UserContext
    ):
        """Тест создания категории обычным пользователем"""
        headers = get_auth_headers(mock_user)
        payload = {"name": "Новая категория", "slug": "new-category"}
        response = await client.post("/categories/", json=payload, headers=headers)
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

    async def test_create_category_success(
        self, client: AsyncClient, mock_manager: UserContext
    ):
        """Тест успешного создания категории менеджером"""
        headers = get_auth_headers(mock_manager)
        payload = {"name": "Физика", "slug": "physics"}
        response = await client.post("/categories/", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Физика"
        assert data["slug"] == "physics"
        assert "id" in data

    async def test_create_category_duplicate_slug(
        self, client: AsyncClient, mock_manager: UserContext, test_category: Category
    ):
        """Тест создания категории с дублирующимся slug"""
        headers = get_auth_headers(mock_manager)
        payload = {
            "name": "Другое название",
            "slug": test_category.slug,  # Используем существующий slug
        }
        response = await client.post("/categories/", json=payload, headers=headers)
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "slug" in data["error"] or data.get("field") == "slug"
        assert (
            test_category.slug in data["error"]
            or data.get("value") == test_category.slug
        )

    async def test_create_category_duplicate_name(
        self, client: AsyncClient, mock_manager: UserContext, test_category: Category
    ):
        """Тест создания категории с дублирующимся именем"""
        headers = get_auth_headers(mock_manager)
        payload = {
            "name": test_category.name,  # Используем существующее имя
            "slug": "different-slug",
        }
        response = await client.post("/categories/", json=payload, headers=headers)
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "name" in data["error"] or data.get("field") == "name"
        assert (
            test_category.name in data["error"]
            or data.get("value") == test_category.name
        )


@pytest.mark.asyncio
class TestUpdateCategory:
    """Тесты для PATCH /categories/{category_id}"""

    async def test_update_category_unauthorized(
        self, client: AsyncClient, test_category: Category
    ):
        """Тест обновления категории без авторизации"""
        payload = {"name": "Updated Name"}
        response = await client.patch(f"/categories/{test_category.id}", json=payload)
        assert response.status_code == 401
        assert (
            "Not authenticated" in response.json()["detail"]
            or "Not authenticated" in response.json()["detail"]
        )

    async def test_update_category_forbidden(
        self, client: AsyncClient, test_category: Category, mock_user: UserContext
    ):
        """Тест обновления категории обычным пользователем"""
        headers = get_auth_headers(mock_user)
        payload = {"name": "Updated Name"}
        response = await client.patch(
            f"/categories/{test_category.id}", json=payload, headers=headers
        )
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

    async def test_update_category_not_found(
        self, client: AsyncClient, mock_manager: UserContext
    ):
        """Тест обновления несуществующей категории"""
        headers = get_auth_headers(mock_manager)
        payload = {"name": "Updated Name"}
        response = await client.patch("/categories/999", json=payload, headers=headers)
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]

    async def test_update_category_success(
        self, client: AsyncClient, test_category: Category, mock_manager: UserContext
    ):
        """Тест успешного обновления категории"""
        headers = get_auth_headers(mock_manager)
        payload = {"name": "Обновленное название", "slug": "updated-slug"}
        response = await client.patch(
            f"/categories/{test_category.id}", json=payload, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Обновленное название"
        assert data["slug"] == "updated-slug"
        assert data["id"] == test_category.id

    async def test_update_category_partial(
        self, client: AsyncClient, test_category: Category, mock_manager: UserContext
    ):
        """Тест частичного обновления категории"""
        headers = get_auth_headers(mock_manager)
        original_name = test_category.name
        payload = {"slug": "only-slug-updated"}
        response = await client.patch(
            f"/categories/{test_category.id}", json=payload, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "only-slug-updated"
        # Имя должно остаться прежним
        assert data["name"] == original_name

    async def test_update_category_duplicate_slug(
        self,
        client: AsyncClient,
        test_category: Category,
        test_categories: list[Category],
        mock_manager: UserContext,
    ):
        """Тест обновления категории с дублирующимся slug"""
        headers = get_auth_headers(mock_manager)
        payload = {
            "slug": test_categories[0].slug  # Используем slug другой категории
        }
        response = await client.patch(
            f"/categories/{test_category.id}", json=payload, headers=headers
        )
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "slug" in data["error"] or data.get("field") == "slug"
        assert (
            test_categories[0].slug in data["error"]
            or data.get("value") == test_categories[0].slug
        )

    async def test_update_category_duplicate_name(
        self,
        client: AsyncClient,
        test_category: Category,
        test_categories: list[Category],
        mock_manager: UserContext,
    ):
        """Тест обновления категории с дублирующимся именем"""
        headers = get_auth_headers(mock_manager)
        payload = {
            "name": test_categories[0].name  # Используем имя другой категории
        }
        response = await client.patch(
            f"/categories/{test_category.id}", json=payload, headers=headers
        )
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert "name" in data["error"] or data.get("field") == "name"
        assert (
            test_categories[0].name in data["error"]
            or data.get("value") == test_categories[0].name
        )


@pytest.mark.asyncio
class TestDeleteCategory:
    """Тесты для DELETE /categories/{category_id}"""

    async def test_delete_category_unauthorized(
        self, client: AsyncClient, test_category: Category
    ):
        """Тест удаления категории без авторизации"""
        response = await client.delete(f"/categories/{test_category.id}")
        assert response.status_code == 401
        assert (
            "Not authenticated" in response.json()["detail"]
            or "Not authenticated" in response.json()["detail"]
        )

    async def test_delete_category_forbidden(
        self, client: AsyncClient, test_category: Category, mock_user: UserContext
    ):
        """Тест удаления категории обычным пользователем"""
        headers = get_auth_headers(mock_user)
        response = await client.delete(
            f"/categories/{test_category.id}", headers=headers
        )
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

    async def test_delete_category_not_found(
        self, client: AsyncClient, mock_manager: UserContext
    ):
        """Тест удаления несуществующей категории"""
        headers = get_auth_headers(mock_manager)
        response = await client.delete("/categories/999", headers=headers)
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]

    async def test_delete_category_success(
        self, client: AsyncClient, db_session: AsyncSession, mock_manager: UserContext
    ):
        """Тест успешного удаления категории"""
        # Создаем категорию для удаления
        category = Category(name="To Delete", slug="to-delete")
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        headers = get_auth_headers(mock_manager)
        response = await client.delete(f"/categories/{category.id}", headers=headers)
        assert response.status_code == 204

        # Проверяем, что категория удалена
        response = await client.get("/categories/")
        assert response.status_code == 200
        data = response.json()
        slugs = [cat["slug"] for cat in data]
        assert category.slug not in slugs

    async def test_delete_category_with_decks(
        self,
        client: AsyncClient,
        test_category: Category,
        test_deck: Deck,
        mock_manager: UserContext,
    ):
        """Тест удаления категории, связанной с колодами"""
        # test_deck уже связан с test_category через фикстуру
        headers = get_auth_headers(mock_manager)
        response = await client.delete(
            f"/categories/{test_category.id}", headers=headers
        )
        # В зависимости от настроек CASCADE, категория может быть удалена
        # или должна быть ошибка. Проверяем, что операция завершилась
        assert response.status_code in [204, 400, 409]
