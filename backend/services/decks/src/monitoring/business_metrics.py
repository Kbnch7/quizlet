from prometheus_client import Counter

from .common import registry

decks_created_total = Counter(
    "decks_created_total",
    "Total number of created decks",
    registry=registry,
)

decks_updated_total = Counter(
    "decks_updated_total",
    "Total number of updated decks",
    registry=registry,
)

cards_created_total = Counter(
    "cards_created_total",
    "Total number of created cards",
    registry=registry,
)

card_presign_image_requests_total = Counter(
    "card_presign_image_requests_total",
    "Total number of presigned image URL requests",
    registry=registry,
)

learn_sessions_started_total = Counter(
    "learn_sessions_started_total",
    "Total number of started learning sessions",
    registry=registry,
)

learn_sessions_completed_total = Counter(
    "learn_sessions_completed_total",
    "Total number of completed learning sessions",
    registry=registry,
)

learn_sessions_finished_total = Counter(
    "learn_sessions_finished_total",
    "Total number of finished learning sessions",
    registry=registry,
)
