import uuid
from datetime import datetime, timedelta

from fastapi import Header
from jose import ExpiredSignatureError, JWTError, jwt

from ..infra.redis_client import get_redis
from .config import jwt_settings
from .exceptions import (
    TokenExpiredException,
    TokenRevokedException,
    TokenValidationException,
)


def create_token(data: dict, expires_delta: timedelta) -> str:
    expiring_datetime = expires_delta + datetime.utcnow()
    payload = data.copy()
    payload["exp"] = expiring_datetime
    payload["iat"] = datetime.utcnow()
    payload["jti"] = str(uuid.uuid4())
    return jwt.encode(
        payload, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM
    )


def create_access_token(user_id: int, is_manager: bool) -> str:
    payload = {"sub": str(user_id), "type": "access",
               "isman": str(int(is_manager))}
    return create_token(
        payload, timedelta(minutes=int(
            jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    )


def create_refresh_token(user_id: int, is_manager: bool) -> str:
    payload = {"sub": str(user_id), "type": "refresh",
               "isman": str(int(is_manager))}
    return create_token(
        payload, timedelta(days=int(jwt_settings.REFRESH_TOKEN_EXPIRE_DAYS))
    )


def decode_token(token: str) -> dict:
    return jwt.decode(
        token, jwt_settings.SECRET_KEY, algorithms=[jwt_settings.ALGORITHM]
    )


async def verify_token(token: str, token_type: str) -> dict:
    if not token:
        raise TokenValidationException()
    r = await get_redis()
    try:
        payload = decode_token(token)
        if payload.get("type", "") != token_type:
            raise TokenValidationException()
        if "sub" not in payload or "jti" not in payload or "exp" not in payload:
            raise TokenValidationException()
        if await r.exists(f"bl:{token_type}:{payload['jti']}"):
            raise TokenRevokedException()
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise TokenValidationException()


async def get_access_token(authorization: str = Header(..., alias="Authorization")):
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise TokenValidationException()
    return token
