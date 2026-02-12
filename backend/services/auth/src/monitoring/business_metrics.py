from prometheus_client import Counter

from .common import registry

auth_users_registered_total = Counter(
    "auth_users_registered_total",
    "Total number of successfully registered users",
    registry=registry,
)

auth_logins_success_total = Counter(
    "auth_logins_success_total",
    "Total number of successful logins",
    registry=registry,
)

auth_logins_failed_total = Counter(
    "auth_logins_failed_total",
    "Total number of failed logins",
    registry=registry,
)

auth_tokens_refreshed_total = Counter(
    "auth_tokens_refreshed_total",
    "Total number of successfully refreshed access tokens",
    registry=registry,
)

auth_tokens_revoked_total = Counter(
    "auth_tokens_revoked_total",
    "Total number of revoked tokens (logout)",
    registry=registry,
)

