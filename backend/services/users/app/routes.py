from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from .database_client import get_db
from .crud import UserCRUD
from .schemas import user_schemas, errors_schemas
from .utils.exceptions import UserAlreadyExistsException, UserNotFoundException

router = APIRouter(tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get(
    "/users/email/{user_email}",
    status_code=status.HTTP_200_OK,
    response_model=user_schemas.UserBaseInfo,
    responses={
        404: {
            "model": errors_schemas.CustomError,
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": "USER_NOT_FOUND",
                        "statusCode": "404_NOT_FOUND"
                    }
                }
            },
        },
    })
async def get_user_by_email(user_email: str, db: AsyncSession = Depends(get_db)):
    user = await UserCRUD.get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return user

@router.get(
    "/users/id/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=user_schemas.UserBaseInfo,
    responses={
        404: {
            "model": errors_schemas.CustomError,
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": "USER_NOT_FOUND",
                        "statusCode": "404_NOT_FOUND"
                    }
                }
            },
        },
    })
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserCRUD.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return user

@router.patch(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=user_schemas.UserBaseInfo,
    responses={
        404: {
            "model": errors_schemas.CustomError,
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": "USER_NOT_FOUND",
                        "statusCode": "404_NOT_FOUND"
                    }
                }
            },
        },
        409: {
            "model": errors_schemas.CustomError,
            "description": "User already exists",
            "content": {
                "application/json": {
                    "example": {
                        "code": "USER_ALREADY_EXISTS",
                        "statusCode": "409_CONFLICT"
                    }
                }
            },
        }
    })
async def update_user(user_id: int, payload: user_schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    try:
        user = await UserCRUD.update_user(db, user_id, payload)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")
    except UserAlreadyExistsException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="USER_ALREADY_EXISTS")
    return user

@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            "model": errors_schemas.CustomError,
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": "USER_NOT_FOUND",
                        "statusCode": "404_NOT_FOUND"
                    }
                }
            },
        },

    })
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await UserCRUD.delete_user(db, user_id)
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")

@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=user_schemas.UserBaseInfo,
    responses={
        409: {
            "model": errors_schemas.CustomError,
            "description": "User already exists",
            "content": {
                "application/json": {
                    "example": {
                        "code": "USER_ALREADY_EXISTS",
                        "statusCode": "409_CONFLICT"
                    }
                }
            },
        },
    }
)
async def create_user(payload: user_schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await UserCRUD.create_user(db, payload)
    except UserAlreadyExistsException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="USER_ALREADY_EXISTS")
    return user

@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    response_model=List[user_schemas.UserBaseInfo],
    responses={
        404: {
            "model": errors_schemas.CustomError,
            "description": "Users not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": "USERS_NOT_FOUND",
                        "statusCode": "404_NOT_FOUND"
                    }
                }
            },
        },
    })
async def list_users(db: AsyncSession = Depends(get_db)):
    users = await UserCRUD.get_users(db)
    if not users:
        raise HTTPException(status_code=404, detail="USERS_NOT_FOUND")
    return users

@router.post(
    "/verify_user",
    status_code=status.HTTP_200_OK,
    response_model=user_schemas.UserBaseInfo,
    responses={
        404: {
            "model": errors_schemas.CustomError,
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": "USER_NOT_FOUND",
                        "statusCode": "404_NOT_FOUND"
                    }
                }
            },
        },
    })
async def verify_user(payload: user_schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    user = await UserCRUD.get_user_by_email_and_password(db, payload)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return user

@router.get("/")
async def home():
    return {"message": "hello"}