from prometheus_client import Counter, Histogram

from .common import registry

http_requests_total = Counter(
    "teaching_http_requests_total",
    "Total number of HTTP requests in teaching service",
    ["method", "endpoint", "status_code"],
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "teaching_http_request_duration_seconds",
    "HTTP request duration in seconds in teaching service",
    ["method", "endpoint"],
    registry=registry,
)

api_calls_total = Counter(
    "teaching_api_calls_total",
    "Total number of API calls by type in teaching service",
    ["api_type"],
    registry=registry,
)

http_errors_4xx_total = Counter(
    "teaching_http_errors_4xx_total",
    "Total number of 4xx HTTP errors in teaching service",
    ["endpoint", "status_code"],
    registry=registry,
)

http_errors_5xx_total = Counter(
    "teaching_http_errors_5xx_total",
    "Total number of 5xx HTTP errors in teaching service",
    ["endpoint", "status_code"],
    registry=registry,
)

