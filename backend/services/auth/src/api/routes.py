import logging
import os
from time import time

import httpx
from dotenv import load_dotenv
from event_contracts.base import EventEnvelope
from event_contracts.kafka_producer import KafkaProducer
from event_contracts.user.v1 import UserRegistered as EventUserRegisteredV1
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from ..core.exceptions import (
    TokenExpiredException,
    TokenRevokedException,
    TokenValidationException,
)
from ..core.jwt import (
    create_access_token,
    create_refresh_token,
    get_access_token,
    verify_token,
)
from ..infra.redis_client import get_redis
from ..schemas import errors_schemas, token_schemas, users_schemas

load_dotenv()


logger = logging.getLogger(__name__)
producer = KafkaProducer(os.getenv("KAFKA_BROKER_URL"))

router = APIRouter(tags=["Auth"])


async def get_users_client() -> httpx.AsyncClient:
    async with httpx.AsyncClient(
        base_url=f"{os.getenv('USERS_SERVICE_URL')}/api", timeout=30.0
    ) as client:
        yield client


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=token_schemas.AccessToken,
    responses={
        409: {
            "model": errors_schemas.CustomError,
            "description": "Users already exists",
            "content": {
                "application/json": {
                    "example": {
                        "code": "USER_ALREADY_EXISTS",
                        "statusCode": "409_CONFLICT",
                    }
                }
            },
        },
        422: {
            "model": errors_schemas.CustomError,
            "description": "Invalid user data",
            "content": {
                "application/json": {
                    "example": {
                        "code": "HTTP_ERROR",
                        "statusCode": "422_UNPROCESSABLE_ENTITY",
                    }
                }
            },
        },
        500: {
            "model": errors_schemas.CustomError,
            "description": "Server error",
            "content": {
                "application/json": {
                    "example": {
                        "code": "SERVER_ERROR",
                        "statusCode": "HTTP_500_INTERNAL_SERVER_ERROR",
                    }
                }
            },
        },
    },
)
async def register(
    payload: users_schemas.UserRegister,
    response: Response,
    users_client: httpx.AsyncClient = Depends(get_users_client),
):
    try:
        users_response = await users_client.post("/users", json=payload.model_dump())
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="USER_SERVICE_UNAVAILABLE")
    if users_response.status_code == 409:
        raise HTTPException(status_code=409, detail="USER_ALREADY_EXISTS")
    elif users_response.status_code == 422:
        try:
            error = users_response.json()
        except Exception:
            error = users_response.text
        raise HTTPException(status_code=422, detail=error)
    elif users_response.is_error:
        raise HTTPException(
            status_code=500, detail=f"User service error: {users_response.text}"
        )

    data = users_response.json()
    access_token = create_access_token(data["id"], is_manager=data["is_manager"])
    refresh_token = create_refresh_token(data["id"], is_manager=data["is_manager"])
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    payload = EventUserRegisteredV1(
        user_id=data.get("id"),
        email=data.get("email"),
        registered_at=data.get("created_at"),
    )
    event = EventEnvelope(
        event_type="user_registered",
        event_version=1,
        occured_at=data.get("created_at"),
        producer="auth-service",
        payload=payload.model_dump(),
    )
    try:
        producer.send(
            topic="user.events",
            key=str(data.get("id")),
            value=event.to_json(),
        )
    except Exception as e:
        logger.exception(
            f"Failed to send user_registered event: {e}",
            extra={
                "user_id": data.get("id"),
            },
        )
    return token_schemas.AccessToken(access=access_token)


@router.post(
    "/login",
    status_code=status.HTTP_201_CREATED,
    response_model=token_schemas.AccessToken,
    responses={
        404: {
            "model": errors_schemas.CustomError,
            "description": "USER_NOT_FOUND",
            "content": {
                "application/json": {
                    "example": {"code": "USER_NOT_FOUND", "statusCode": "404_NOT_FOUND"}
                }
            },
        },
        500: {
            "model": errors_schemas.CustomError,
            "description": "USER_SERVER_ERROR",
            "content": {
                "application/json": {
                    "example": {
                        "code": "USER_SERVER_ERROR",
                        "statusCode": "500_INTERNAL_SERVER_ERROR",
                    }
                }
            },
        },
    },
)
async def login(
    payload: users_schemas.UserLogin,
    response: Response,
    users_client: httpx.AsyncClient = Depends(get_users_client),
):
    try:
        users_response = await users_client.post(
            "/verify_user", json=payload.model_dump()
        )
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="USER_SERVICE_UNAVAILABLE")
    if users_response.status_code == 404:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    elif users_response.status_code == 422:
        try:
            error = users_response.json()
        except Exception:
            error = users_response.text
        raise HTTPException(status_code=422, detail=error)
    elif users_response.is_error:
        raise HTTPException(
            status_code=500, detail=f"User service error: {users_response.text}"
        )
    data = users_response.json()
    access_token = create_access_token(data["id"], is_manager=data["is_manager"])
    refresh_token = create_refresh_token(data["id"], is_manager=data["is_manager"])
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return token_schemas.AccessToken(access=access_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": errors_schemas.CustomError,
            "description": "INVALID_TOKEN",
            "content": {
                "application/json": {
                    "example": {
                        "invalid_token": {
                            "code": "INVALID_TOKEN",
                            "statusCode": "401_UNAUTHORIZED",
                        },
                        "token_expired": {
                            "code": "TOKEN_EXPIRED",
                            "statusCode": "401_UNAUTHORIZED",
                        },
                        "token_revoked": {
                            "code": "TOKEN_REVOKED",
                            "statusCode": "401_UNAUTHORIZED",
                        },
                    }
                }
            },
        },
        200: {
            "description": "SUCCESS",
            "content": {"application/json": {"example": {"statusCode": "LOGGED_OUT"}}},
        },
    },
)
async def logout(
    response: Response,
    access_token: str = Depends(get_access_token),
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
):
    tokens = {}
    for token, token_type in ((access_token, "access"), (refresh_token, "refresh")):
        try:
            tokens[token_type] = await verify_token(token, token_type=token_type)
        except TokenRevokedException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN_REVOKED"
            )
        except TokenExpiredException:
            pass
        except TokenValidationException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_TOKEN"
            )
    r = await get_redis()
    now = int(time())
    for kind in tokens:
        jti = tokens[kind]["jti"]
        exp = int(tokens[kind]["exp"])
        ttl = exp - now
        if ttl > 0:
            await r.setex(f"bl:{kind}:{jti}", ttl, tokens[kind].get("sub", ""))

    response.delete_cookie("refresh_token")

    return {"detail": "LOGGED_OUT"}


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=token_schemas.AccessToken,
    responses={
        401: {
            "model": errors_schemas.CustomError,
            "description": "INVALID_TOKEN",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_token": {
                            "code": "INVALID_TOKEN",
                            "statusCode": "401_UNAUTHORIZED",
                        },
                        "token_expired": {
                            "code": "TOKEN_EXPIRED",
                            "statusCode": "401_UNAUTHORIZED",
                        },
                        "token_revoked": {
                            "code": "TOKEN_REVOKED",
                            "statusCode": "401_UNAUTHORIZED",
                        },
                    }
                }
            },
        },
        200: {
            "description": "SUCCESS",
            "content": {"application/json": {"example": {"statusCode": "REFRESHED"}}},
        },
    },
)
async def refresh(
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="NO_REFRESH_TOKEN"
        )
    try:
        refresh = await verify_token(refresh_token, token_type="refresh")
    except TokenRevokedException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN_REVOKED"
        )
    except TokenExpiredException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN_EXPIRED"
        )
    except TokenValidationException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_TOKEN"
        )

    access_token = create_access_token(refresh["sub"], refresh["isman"])

    return token_schemas.AccessToken(access=access_token)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=users_schemas.UserBaseInfo,
    responses={
        401: {
            "model": errors_schemas.CustomError,
            "description": "INVALID_TOKEN",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_token": {
                            "code": "INVALID_TOKEN",
                            "statusCode": "401_UNAUTHORIZED",
                        },
                        "token_expired": {
                            "code": "TOKEN_EXPIRED",
                            "statusCode": "401_UNAUTHORIZED",
                        },
                        "token_revoked": {
                            "code": "TOKEN_REVOKED",
                            "statusCode": "401_UNAUTHORIZED",
                        },
                    }
                }
            },
        },
    },
)
async def me(
    access_token: str = Depends(get_access_token),
    users_client: httpx.AsyncClient = Depends(get_users_client),
):
    try:
        access = await verify_token(access_token, token_type="access")
    except TokenRevokedException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN_REVOKED"
        )
    except TokenExpiredException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN_EXPIRED"
        )
    except TokenValidationException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_TOKEN"
        )

    user_id = access["sub"]

    try:
        response = await users_client.get(f"/users/id/{user_id}")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="USER_SERVICE_UNAVAILABLE")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    elif response.status_code == 422:
        try:
            error = response.json()
        except Exception:
            error = response.text
        raise HTTPException(status_code=422, detail=error)
    elif response.is_error:
        raise HTTPException(
            status_code=500, detail=f"User service error: {response.text}"
        )

    return response.json()


@router.get("/")
async def home():
    return {"message": "hello"}
