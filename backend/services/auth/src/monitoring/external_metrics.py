from prometheus_client import Counter, Histogram

from .common import registry

auth_users_service_requests_total = Counter(
    "auth_users_service_requests_total",
    "Total number of requests from auth to users service",
    ["method", "endpoint", "status"],
    registry=registry,
)

auth_users_service_request_duration_seconds = Histogram(
    "auth_users_service_request_duration_seconds",
    "Request duration from auth to users service in seconds",
    ["method", "endpoint"],
    registry=registry,
)

