import time
from typing import Callable

from django.http import HttpRequest, HttpResponse

from .api_metrics import (
    api_calls_total,
    http_errors_4xx_total,
    http_errors_5xx_total,
    http_request_duration_seconds,
    http_requests_total,
)


class MetricsMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        method = request.method

        resolver_match = getattr(request, "resolver_match", None)
        if resolver_match is not None and getattr(resolver_match, "route", None):
            endpoint = "/" + str(resolver_match.route).lstrip("/")
        else:
            endpoint = "/unknown"
        status_code = str(response.status_code)

        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)

        api_type = "other"
        if endpoint.startswith("/api/"):
            parts = endpoint.split("/")
            api_type = parts[2] if len(parts) > 2 and parts[2] else "unknown"

        api_calls_total.labels(api_type=api_type).inc()

        status = response.status_code
        if 400 <= status < 500:
            http_errors_4xx_total.labels(
                endpoint=endpoint,
                status_code=status_code,
            ).inc()
        elif status >= 500:
            http_errors_5xx_total.labels(
                endpoint=endpoint,
                status_code=status_code,
            ).inc()

        return response

