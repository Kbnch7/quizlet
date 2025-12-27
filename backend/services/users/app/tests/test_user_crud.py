# tests/test_user_crud.py
import pytest
from sqlalchemy import select

# подстрой пути под твой пакет
from ..crud import UserCRUD
from ..schemas import user_schemas
from ..utils.exceptions import UserAlreadyExistsException
from ..utils.security import verify_password
from . import models

pytestmark = pytest.mark.asyncio


async def test_create_user_ok(session, user_payload_factory):
    payload = user_schemas.UserCreate(**user_payload_factory(1))
    user = await UserCRUD.create_user(session, payload)
    assert user.id is not None
    assert user.email == payload.email
    assert user.password_hash != payload.password
    assert verify_password(payload.password, user.password_hash)


async def test_create_user_conflict_email(session, user_payload_factory):
    # первый — ок
    payload1 = user_schemas.UserCreate(**user_payload_factory(2))
    await UserCRUD.create_user(session, payload1)

    # второй с тем же email — 409
    payload2 = user_schemas.UserCreate(
        **user_payload_factory(3, email=payload1.email))
    with pytest.raises(UserAlreadyExistsException) as exc:
        await UserCRUD.create_user(session, payload2)


async def test_get_user_by_id_only_active(session, user_payload_factory):
    # создаём
    payload = user_schemas.UserCreate(**user_payload_factory(4))
    user = await UserCRUD.create_user(session, payload)

    # находим активного
    found = await UserCRUD.get_user_by_id(session, user.id)
    assert found is not None
    assert found.id == user.id

    # делаем soft-delete
    await UserCRUD.delete_user(session, user.id)

    # больше не находим (фильтр is_active==True)
    found2 = await UserCRUD.get_user_by_id(session, user.id)
    assert found2 is None


async def test_list_users_filters_only_active(session, user_payload_factory):
    u1 = await UserCRUD.create_user(
        session, user_schemas.UserCreate(**user_payload_factory(5))
    )
    u2 = await UserCRUD.create_user(
        session, user_schemas.UserCreate(**user_payload_factory(6))
    )
    # soft-delete второго
    await UserCRUD.delete_user(session, u2.id)

    items = await UserCRUD.get_users(session)
    ids = {u.id for u in items}
    assert u1.id in ids
    assert u2.id not in ids  # удалённый не должен вернуться


async def test_update_user_partial_fields(session, user_payload_factory):
    # создаём
    payload = user_schemas.UserCreate(**user_payload_factory(7))
    user = await UserCRUD.create_user(session, payload)

    # частичное обновление: имя и почта
    patch = user_schemas.UserUpdate(name="Alice", email="alice@example.com")
    updated = await UserCRUD.update_user(session, user.id, patch)

    assert updated.name == "Alice"
    assert updated.email == "alice@example.com"
    # пароль не меняли — должен верифицироваться старый
    # assert verify_password("strongpass7!", updated.password_hash)


async def test_update_user_password_hashing(session, user_payload_factory):
    payload = user_schemas.UserCreate(**user_payload_factory(8))
    user = await UserCRUD.create_user(session, payload)

    patch = user_schemas.UserUpdate(password="NewStrongPass!8")
    updated = await UserCRUD.update_user(session, user.id, patch)

    assert verify_password("NewStrongPass!8", updated.password_hash)
    # старый уже не должен подходить
    assert not verify_password(payload.password, updated.password_hash)


async def test_update_user_conflict_email(session, user_payload_factory):
    # два пользователя
    u1 = await UserCRUD.create_user(
        session, user_schemas.UserCreate(**user_payload_factory(9))
    )
    u2 = await UserCRUD.create_user(
        session, user_schemas.UserCreate(**user_payload_factory(10))
    )

    # пытаемся изменить email второго на email первого → 409
    with pytest.raises(UserAlreadyExistsException) as exc:
        await UserCRUD.update_user(
            session, u2.id, user_schemas.UserUpdate(email=u1.email)
        )


async def test_delete_user_soft(session, user_payload_factory):
    user = await UserCRUD.create_user(
        session, user_schemas.UserCreate(**user_payload_factory(11))
    )
    await UserCRUD.delete_user(session, user.id)

    # запись осталась в БД, но is_active = False
    res = await session.execute(select(models.User).where(models.User.id == user.id))
    db_user = res.scalar_one()
    assert db_user.is_active is False
