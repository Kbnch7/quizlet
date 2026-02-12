from event_contracts.learning.v1 import (
    LearningSessionFinished as LearningSessionFinishedV1,
)
from event_contracts.learning.v1 import (
    LearningSessionStarted as LearningSessionStartedV1,
)


def map_learning_session_started(
    produced_at: str, event_id: int, event: LearningSessionStartedV1
) -> tuple:
    return (
        event.started_at,
        produced_at,
        event_id,
        event.user_id,
        event.deck_id,
        event.session_id,
    )


def map_learning_session_finished(
    produced_at: str, event_id: int, event: LearningSessionFinishedV1
) -> tuple:
    return (
        event.finished_at,
        produced_at,
        event_id,
        event.user_id,
        event.deck_id,
        event.session_id,
        event.learned_cards,
        event.total_cards_seen,
        event.duration_sec,
        event.completed,
    )
