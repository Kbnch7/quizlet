import time
from typing import Callable

from fastapi import Request, Response

from .api_metrics import (
    auth_http_errors_4xx_total,
    auth_http_errors_5xx_total,
    auth_http_request_duration_seconds,
    auth_http_requests_total,
)


class MetricsMiddleware:
    def __init__(self, app: Callable):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        method = request.method

        route = request.scope.get("route")
        if route is not None and hasattr(route, "path"):
            endpoint = route.path
        else:
            endpoint = "/unknown"
        status_code = str(response.status_code)

        auth_http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
        ).inc()

        auth_http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)

        status = response.status_code
        if 400 <= status < 500:
            auth_http_errors_4xx_total.labels(
                endpoint=endpoint,
                status_code=status_code,
            ).inc()
        elif status >= 500:
            auth_http_errors_5xx_total.labels(
                endpoint=endpoint,
                status_code=status_code,
            ).inc()

        return response

