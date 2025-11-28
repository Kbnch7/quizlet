from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Header

from datetime import timedelta, datetime
import uuid

from .config import jwt_settings
from .exceptions import TokenExpiredException, TokenValidationException, TokenRevokedException
from ..infra.redis_client import get_redis

def create_token(data: dict, expires_delta: timedelta) -> str:
    expiring_datetime = expires_delta + datetime.utcnow()
    payload = data.copy()
    payload['exp'] = expiring_datetime
    payload['iat'] = datetime.utcnow()
    payload['jti'] = str(uuid.uuid4())
    return jwt.encode(payload, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)

def create_access_token(user_id: int) -> str:
    payload = {'sub': str(user_id), 'type': 'access'}
    return create_token(payload, timedelta(minutes=int(jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES)))

def create_refresh_token(user_id: int) -> str:
    payload = {'sub': str(user_id), 'type': 'refresh'}
    return create_token(payload, timedelta(days=int(jwt_settings.REFRESH_TOKEN_EXPIRE_DAYS)))

def decode_token(token: str) -> dict:
    return jwt.decode(token, jwt_settings.SECRET_KEY, algorithms=[jwt_settings.ALGORITHM])

async def verify_token(token: str, token_type: str) -> dict:
    if not token:
        raise TokenValidationException()
    r = await get_redis()
    try:
        payload = decode_token(token)
        if payload.get('type', '') != token_type:
            raise TokenValidationException()
        if "sub" not in payload or "jti" not in payload or "exp" not in payload:
            raise TokenValidationException()
        if await r.exists(f"bl:{token_type}:{payload['jti']}"):
            print(f"bl:{token_type}:{payload['jti']}")
            raise TokenRevokedException()
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise TokenValidationException()

async def get_access_token(authorization: str = Header(...)):
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise TokenValidationException()
    return token
