from prometheus_client import Counter, Histogram

from .common import registry

auth_http_requests_total = Counter(
    "auth_http_requests_total",
    "Total number of HTTP requests in auth service",
    ["method", "endpoint", "status_code"],
    registry=registry,
)

auth_http_request_duration_seconds = Histogram(
    "auth_http_request_duration_seconds",
    "HTTP request duration in seconds in auth service",
    ["method", "endpoint"],
    registry=registry,
)

auth_http_errors_4xx_total = Counter(
    "auth_http_errors_4xx_total",
    "Total number of 4xx HTTP errors in auth service",
    ["endpoint", "status_code"],
    registry=registry,
)

auth_http_errors_5xx_total = Counter(
    "auth_http_errors_5xx_total",
    "Total number of 5xx HTTP errors in auth service",
    ["endpoint", "status_code"],
    registry=registry,
)

