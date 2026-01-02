from dataclasses import dataclass
from typing import Callable, Type

from event_contracts.content.v1 import CardCreated as CardCreatedV1
from event_contracts.content.v1 import ContentEventType as ContentEventTypeV1
from event_contracts.content.v1 import DeckCreated as DeckCreatedV1
from event_contracts.course.v1 import CourseCreated as CourseCreatedV1
from event_contracts.course.v1 import CourseEnrolled as CourseEnrolledV1
from event_contracts.course.v1 import CourseEventType as CourseEventTypeV1
from event_contracts.course.v1 import CourseProgressUpdated as CourseProgressUpdatedV1
from event_contracts.learning.v1 import LearningEventType as LearningEventTypeV1
from event_contracts.learning.v1 import (
    LearningSessionFinished as LearningSessionFinishedV1,
)
from event_contracts.learning.v1 import (
    LearningSessionStarted as LearningSessionStartedV1,
)
from event_contracts.user.v1 import UserEventType as UserEventTypeV1
from event_contracts.user.v1 import UserRegistered as UserRegisteredV1
from pydantic import BaseModel

from .mappers.content import map_card_created, map_deck_created
from .mappers.course import (
    map_course_created,
    map_course_enrolled,
    map_course_progress_updated,
)
from .mappers.learning import (
    map_learning_session_finished,
    map_learning_session_started,
)
from .mappers.user import map_user_registered


@dataclass(frozen=True)
class EventDescriptor:
    schema: Type[BaseModel]
    table: str
    mapper: Callable[[BaseModel], tuple]


EVENT_REGISTRY: dict[tuple[str, int], EventDescriptor] = {
    # ---------- CONTENT ----------
    (ContentEventTypeV1.DECK_CREATED, 1): EventDescriptor(
        schema=DeckCreatedV1,
        table="analytics.deck_created",
        mapper=map_deck_created,
    ),
    (ContentEventTypeV1.CARD_CREATED, 1): EventDescriptor(
        schema=CardCreatedV1,
        table="analytics.card_created",
        mapper=map_card_created,
    ),
    # ---------- LEARNING ----------
    (LearningEventTypeV1.LEARNING_SESSION_STARTED, 1): EventDescriptor(
        schema=LearningSessionStartedV1,
        table="analytics.learning_session_started",
        mapper=map_learning_session_started,
    ),
    (LearningEventTypeV1.LEARNING_SESSION_FINISHED, 1): EventDescriptor(
        schema=LearningSessionFinishedV1,
        table="analytics.learning_session_finished",
        mapper=map_learning_session_finished,
    ),
    # ---------- COURSE ----------
    (CourseEventTypeV1.COURSE_CREATED, 1): EventDescriptor(
        schema=CourseCreatedV1,
        table="analytics.course_created",
        mapper=map_course_created,
    ),
    (CourseEventTypeV1.COURSE_ENROLLED, 1): EventDescriptor(
        schema=CourseEnrolledV1,
        table="analytics.course_enrolled",
        mapper=map_course_enrolled,
    ),
    (CourseEventTypeV1.COURSE_PROGRESS_UPDATED, 1): EventDescriptor(
        schema=CourseProgressUpdatedV1,
        table="analytics.course_progress_updated",
        mapper=map_course_progress_updated,
    ),
    # ---------- USER ----------
    (UserEventTypeV1.USER_REGISTERED, 1): EventDescriptor(
        schema=UserRegisteredV1,
        table="analytics.user_registered",
        mapper=map_user_registered,
    ),
}
