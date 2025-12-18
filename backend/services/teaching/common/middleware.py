from common.auth import AnonymousUserContext


class UserContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, 'user') or not hasattr(request.user, 'is_manager'):
            request.user = AnonymousUserContext()
        
        response = self.get_response(request)
        return response

