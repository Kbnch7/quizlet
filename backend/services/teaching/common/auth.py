from rest_framework import authentication
from dataclasses import dataclass


@dataclass
class UserContext:
    id: int
    is_manager: bool
    
    @property
    def is_authenticated(self):
        return True


@dataclass
class AnonymousUserContext:
    id: int = 0
    is_manager: bool = False
    
    @property
    def is_authenticated(self):
        return False


def get_user_context(request) -> UserContext | AnonymousUserContext:
    user = getattr(request, 'user', None)
    if user and isinstance(user, (UserContext, AnonymousUserContext)):
        return user
    return AnonymousUserContext()


class MockJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ', 1)[1]
        
        if token.endswith('-manager'):
            user = UserContext(id=2, is_manager=True)
        else:
            try:
                user_id = int(token.split('-')[-1]) if '-' in token else 1
            except ValueError:
                user_id = 1
            user = UserContext(id=user_id, is_manager=False)
        
        return (user, None)
    
    def authenticate_header(self, request):
        return 'Bearer'

