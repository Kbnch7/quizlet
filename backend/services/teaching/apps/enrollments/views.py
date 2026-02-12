import logging
import os

from common.auth import UserContext
from common.pagination import EnrolledAtCursorPagination
from common.permissions import IsEnrollmentStudentOrManager
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from event_contracts.base import EventEnvelope
from event_contracts.course.v1 import (
    CourseEnrolled as EventCourseEnrolledV1,
)
from event_contracts.course.v1 import (
    CourseProgressUpdated as CourseProgressUpdatedV1,
)
from event_contracts.kafka_producer import KafkaProducer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.courses.models import CourseDeck

from .models import DeckProgress, Enrollment
from .serializers import (
    DeckWithProgressSerializer,
    EnrollmentCreateSerializer,
    EnrollmentDetailSerializer,
    EnrollmentListSerializer,
    EnrollmentUpdateSerializer,
)

logger = logging.getLogger(__name__)
producer = KafkaProducer(os.getenv("KAFKA_BROKER_URL"))


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = EnrolledAtCursorPagination

    def get_serializer_class(self):
        if self.action == "list":
            return EnrollmentListSerializer
        elif self.action == "create":
            return EnrollmentCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return EnrollmentUpdateSerializer
        elif self.action == "retrieve":
            return EnrollmentDetailSerializer
        return EnrollmentListSerializer

    def get_queryset(self):
        user: UserContext = self.request.user
        queryset = Enrollment.objects.all()
        student_id = self.request.query_params.get("student_id")
        course_id = self.request.query_params.get("course_id")

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        if not user.is_manager:
            queryset = queryset.filter(
                Q(student_id=user.id) | Q(course__teacher_id=user.id)
            )

        return queryset.order_by("-enrolled_at")

    def perform_create(self, serializer):
        user: UserContext = self.request.user
        course = serializer.validated_data.get("course")

        if not course.is_published:
            raise ValidationError({"course": ["Cannot enroll in unpublished course"]})

        student_id = serializer.validated_data.get("student_id")

        if student_id is None:
            student_id = user.id
        else:
            if not user.is_manager:
                raise PermissionDenied("Only managers can set student_id")

        try:
            enrollment = serializer.save(student_id=student_id)
        except IntegrityError as e:
            if (
                "unique constraint" in str(e).lower()
                or "duplicate key" in str(e).lower()
            ):
                raise ValidationError(
                    {
                        "non_field_errors": [
                            "Enrollment for this course and student already exists."
                        ]
                    }
                )
            raise

        def publish_event():
            payload = EventCourseEnrolledV1(
                enrollment_id=enrollment.id,
                course_id=course.id,
                user_id=enrollment.student_id,
                enrolled_at=enrollment.enrolled_at,
            )
            event = EventEnvelope(
                event_type="course_enrolled",
                event_version=1,
                producer="teaching-service",
                occured_at=enrollment.enrolled_at,
                payload=payload.model_dump(),
            )
            try:
                producer.send(
                    topic="course.events",
                    key=str(enrollment.id),
                    value=event.to_json(),
                )
            except Exception as e:
                logger.exception(
                    f"Failed to send enrollment_created event: {e}",
                    extra={
                        "enrollment_id": enrollment.id,
                        "course_id": course.id,
                        "user_id": enrollment.student_id,
                    },
                )

        transaction.on_commit(publish_event)

    def update(self, request, *args, **kwargs):
        return Response(
            {"error": "Update is not allowed for enrollment"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"error": "Update is not allowed for enrollment"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=True, methods=["get"])
    def decks(self, request, pk=None):
        enrollment = self.get_object()
        course_decks = enrollment.course.course_decks.order_by("order_index", "id")
        deck_progresses = {
            dp.course_deck_id: dp
            for dp in enrollment.deck_progresses.select_related("course_deck").all()
        }

        result = []
        for course_deck in course_decks:
            deck_data = DeckWithProgressSerializer(
                course_deck, context={"request": request}
            ).data
            progress = deck_progresses.get(course_deck.id)

            if progress:
                deck_data["is_completed"] = progress.is_completed
                deck_data["completed_at"] = progress.completed_at
                deck_data["last_accessed_at"] = progress.last_accessed_at
            else:
                deck_data["is_completed"] = False
                deck_data["completed_at"] = None
                deck_data["last_accessed_at"] = None

            result.append(deck_data)

        return Response(result)

    @action(detail=True, methods=["get"], url_path="decks/(?P<deck_rel_id>\\d+)")
    def deck_detail(self, request, pk=None, deck_rel_id=None):
        """
        deck_rel_id — это ID CourseDeck (связка курс-колода), а не ID самой колоды.
        """
        enrollment = self.get_object()
        course_deck = get_object_or_404(
            CourseDeck, id=deck_rel_id, course=enrollment.course
        )

        progress, _ = DeckProgress.objects.get_or_create(
            enrollment=enrollment,
            course_deck=course_deck,
            defaults={"is_completed": False},
        )

        deck_data = DeckWithProgressSerializer(
            course_deck, context={"request": request}
        ).data
        deck_data["is_completed"] = progress.is_completed
        deck_data["completed_at"] = progress.completed_at
        deck_data["last_accessed_at"] = progress.last_accessed_at

        return Response(deck_data)

    @action(
        detail=True, methods=["post"], url_path="decks/(?P<deck_rel_id>\\d+)/complete"
    )
    def deck_complete(self, request, pk=None, deck_rel_id=None):
        enrollment: Enrollment = self.get_object()
        course_deck: CourseDeck = get_object_or_404(
            CourseDeck, id=deck_rel_id, course=enrollment.course
        )

        progress, _ = DeckProgress.objects.get_or_create(
            enrollment=enrollment,
            course_deck=course_deck,
            defaults={"is_completed": False},
        )

        progress.is_completed = True
        if not progress.completed_at:
            progress.completed_at = timezone.now()
        progress.last_accessed_at = timezone.now()
        progress.save()

        payload = CourseProgressUpdatedV1(
            course_id=course_deck.course.id,
            user_id=enrollment.student_id,
            deck_id=course_deck.deck_id,
            progress_percent=float(enrollment.get_progress_percent()),
            updated_at=progress.last_accessed_at,
        )
        event = EventEnvelope(
            event_type="course_progress_updated",
            event_version=1,
            producer="teaching-service",
            occured_at=enrollment.enrolled_at,
            payload=payload.model_dump(),
        )
        try:
            producer.send(
                topic="course.events",
                key=str(enrollment.id),
                value=event.to_json(),
            )
        except Exception as e:
            logger.exception(
                f"Failed to send course_progress_updated event: {e}",
                extra={
                    "enrollment_id": enrollment.id,
                    "course_id": enrollment.course.id,
                    "user_id": enrollment.student_id,
                },
            )

        deck_data = DeckWithProgressSerializer(
            course_deck, context={"request": request}
        ).data
        deck_data["is_completed"] = progress.is_completed
        deck_data["completed_at"] = progress.completed_at
        deck_data["last_accessed_at"] = progress.last_accessed_at

        return Response(deck_data)

    def get_permissions(self):
        if self.action in ["destroy", "decks", "deck_detail", "deck_complete"]:
            return [IsEnrollmentStudentOrManager()]
        return [IsAuthenticated()]
