import os
from dataclasses import dataclass
from typing import Optional

from fastapi import Header, HTTPException, status

GATEWAY_SECRET = os.getenv("GATEWAY_SECRET")


@dataclass
class UserContext:
    id: int
    is_manager: bool


async def get_current_user(
    x_gateway_auth: str = Header(...),
    x_user_id: Optional[int] = Header(None),
    x_user_ismanager: Optional[bool] = Header(None),
) -> Optional[UserContext]:
    if x_gateway_auth != GATEWAY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid gateway"
        )

    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    if x_user_ismanager is None:
        x_user_ismanager = False
    return UserContext(id=x_user_id, is_manager=x_user_ismanager)


def is_authorized_for_resource(
    resource_owner_id: int, user: Optional[UserContext]
) -> bool:
    """Проверка доступа: менеджер — всегда, иначе — владелец ресурса."""
    if user is None:
        return False
    if user.is_manager:
        return True
    return resource_owner_id == user.id
