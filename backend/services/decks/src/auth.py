from typing import Optional
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

auth_scheme = HTTPBearer(auto_error=False)


@dataclass
class UserContext:
    id: int
    is_manager: bool


def _mock_fetch_user_info_from_auth_service(
    token: str,
) -> Optional[UserContext]:
    if not token:
        return None
    if token.endswith("-manager"):
        return UserContext(id=2, is_manager=True)
    # По умолчанию — обычный пользователь с id 1
    return UserContext(id=1, is_manager=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme),
) -> Optional[UserContext]:
    """Достает пользователя из заголовка Authorization: Bearer <jwt> (заглушка)."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _mock_fetch_user_info_from_auth_service(credentials.credentials)


def is_authorized_for_resource(
    resource_owner_id: int, user: Optional[UserContext]
) -> bool:
    """Проверка доступа: менеджер — всегда, иначе — владелец ресурса."""
    if user is None:
        return False
    if user.is_manager:
        return True
    return resource_owner_id == user.id
