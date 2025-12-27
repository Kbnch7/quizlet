import dataclasses
from datetime import datetime, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt
from src.config import Settings

settings = Settings()


@dataclasses.dataclass
class UserContext:
    id: int
    is_manager: int


def extract_bearer_token(auth: str) -> str | None:
    if not auth:
        return
    sp = auth.strip().split(" ")

    if len(sp) != 2 or sp[0].lower() != "bearer":
        return

    token = sp[1]
    return token


async def get_user_by_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid"
        )

    expire = payload.get("exp")
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid",
        )

    user_is_manager = payload.get("isman")
    if not user_is_manager:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid",
        )

    return UserContext(user_id, user_is_manager)
