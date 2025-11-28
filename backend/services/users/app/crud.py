from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from .utils import exceptions
from . import models
from .schemas import user_schemas
from .utils.security import hash_password, verify_password
from .utils.exceptions import UserAlreadyExistsException, UserNotFoundException


class UserCRUD:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> models.User | None:
        result = await db.execute(
            select(models.User)
            .where(models.User.email == email and models.User.is_active == True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> models.User | None:
        result = await db.execute(
            select(models.User)
            .where(models.User.id == user_id, models.User.is_active == True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_users(db: AsyncSession) -> List[models.User]:
        result = await db.execute(
            select(models.User)
            .where(models.User.is_active == True)
        )
        return result.scalars().all()

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, payload: user_schemas.UserUpdate) -> models.User | None:
        user = await UserCRUD.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundException()

        update_data = payload.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = hash_password(update_data.pop("password"))

        for k, v in update_data.items():
            setattr(user, k, v)
        
        try:
            await db.commit()
            await db.refresh(user)
        except IntegrityError:
            await db.rollback()
            raise UserAlreadyExistsException()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")

        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> None:
        user = await UserCRUD.get_user_by_id(db, user_id)

        if not user:
            raise UserNotFoundException()

        user.is_active = False
        await db.commit()

    @staticmethod
    async def create_user(db: AsyncSession, payload: user_schemas.UserCreate) -> models.User | None:
        data = payload.model_dump()
        data['password_hash'] = hash_password(data.pop('password'))
        
        user = models.User(**data)
        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
        except IntegrityError:
            await db.rollback()
            raise UserAlreadyExistsException()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")

        return user

    @staticmethod
    async def get_user_by_email_and_password(db: AsyncSession, payload: user_schemas.UserLogin) -> models.User | None:
        data = payload.model_dump()
        data['password_hash'] = hash_password(data.pop('password'))
        result = await db.execute(
            select(models.User)
            .where(models.User.email == data['email'] and models.User.is_active == True and models.User.password_hash == data['password_hash'])
        )
        return result.scalar_one_or_none()