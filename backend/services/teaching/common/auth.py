import os
from dataclasses import dataclass

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


@dataclass
class UserContext:
    id: int
    is_manager: bool

    @property
    def is_authenticated(self):
        return True


class GatewayAuthentication(BaseAuthentication):
    GATEWAY_SECRET = os.getenv("GATEWAY_SECRET")

    def authenticate(self, request):
        gateway_auth = request.headers.get("X-Gateway-Auth")

        if gateway_auth is None or gateway_auth != self.GATEWAY_SECRET:
            raise AuthenticationFailed("Invalid Gateway")

        user_id = request.headers.get("X-User-Id")
        if not user_id:
            return None

        is_manager = request.headers.get("X-User-Ismanager")

        try:
            user_id = int(user_id)
        except ValueError:
            raise AuthenticationFailed("Invalid user id")

        try:
            is_manager = bool(int(is_manager))
        except ValueError:
            raise AuthenticationFailed("Invalid is manager header")

        user = UserContext(id=user_id, is_manager=is_manager)
        return (user, None)


class GatewayAuthScheme(OpenApiAuthenticationExtension):
    target_class = "common.auth.GatewayAuthentication"
    name = "GatewayAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "X-Gateway-Auth",
            "description": "Internal gateway authentication header",
        }
