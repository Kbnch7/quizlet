from drf_spectacular.extensions import OpenApiAuthenticationExtension
from common.auth import MockJWTAuthentication


class MockJWTAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = MockJWTAuthentication
    name = 'BearerAuth'
    
    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }

