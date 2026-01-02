from event_contracts.course.v1 import (
    CourseCreated as CourseCreatedV1,
)
from event_contracts.course.v1 import (
    CourseEnrolled as CourseEnrolledV1,
)
from event_contracts.course.v1 import (
    CourseProgressUpdated as CourseProgressUpdatedV1,
)


def map_course_created(
    produced_at: str, event_id: int, event: CourseCreatedV1
) -> tuple:
    return (
        event.created_at,
        produced_at,
        event_id,
        event.course_id,
        event.author_id,
    )


def map_course_enrolled(
    produced_at: str, event_id: int, event: CourseEnrolledV1
) -> tuple:
    return (
        event.enrolled_at,
        produced_at,
        event_id,
        event.course_id,
        event.user_id,
    )


def map_course_progress_updated(
    produced_at: str, event_id: int, event: CourseProgressUpdatedV1
) -> tuple:
    return (
        event.updated_at,
        produced_at,
        event_id,
        event.course_id,
        event.user_id,
        event.deck_id,
        event.progress_percent,
    )
