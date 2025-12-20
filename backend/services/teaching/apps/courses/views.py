from common.auth import UserContext
from common.clients.decks_client import decks_client
from common.permissions import IsCourseTeacherOrManager
from django.db import transaction
from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Course, CourseDeck
from .serializers import (
    CourseCreateSerializer,
    CourseDeckCreateUpdateSerializer,
    CourseDeckReorderItemSerializer,
    CourseDeckSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseUpdateSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        elif self.action == "create":
            return CourseCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return CourseUpdateSerializer
        elif self.action == "retrieve":
            return CourseDetailSerializer
        return CourseListSerializer

    def get_queryset(self):
        user: UserContext = self.request.user
        queryset = Course.objects.all()

        teacher_id = self.request.query_params.get("teacher_id")
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)

        is_published = self.request.query_params.get("is_published")
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published.lower() == "true")

        if not user.is_manager:
            queryset = queryset.filter(Q(is_published=True) | Q(teacher_id=user.id))

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        user: UserContext = self.request.user
        teacher_id = serializer.validated_data.get("teacher_id")

        if teacher_id is None:
            teacher_id = user.id
        else:
            if not user.is_manager:
                raise PermissionDenied("Only managers can set teacher_id")

        serializer.save(teacher_id=teacher_id)

    def get_permissions(self):
        deck_actions = [
            "decks",
            "deck_detail",
            "decks_reorder",
            "decks_batch",
        ]
        if self.action in ["create"]:
            return [IsAuthenticated()]
        elif (
            self.action
            in ["update", "partial_update", "destroy", "publish", "unpublish"]
            + deck_actions
        ):
            return [IsCourseTeacherOrManager()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        course = self.get_object()
        course.is_published = True
        course.save()
        return Response({"status": "published"})

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        course = self.get_object()
        course.is_published = False
        course.save()
        return Response({"status": "unpublished"})

    def _check_deck_permissions(
        self, deck_id: int, course: Course, user: UserContext
    ) -> None:
        deck = decks_client.get_deck_sync(
            deck_id,
            token=self.request.META.get("HTTP_AUTHORIZATION", "").replace(
                "Bearer ", ""
            ),
        )
        if not deck:
            raise ValidationError({"deck_id": "Deck not found"})
        if user.is_manager:
            return
        if deck.get("owner_id") != course.teacher_id:
            raise PermissionDenied("You can only use decks owned by the course teacher")

    def _get_next_order_index(self, course: Course) -> int:
        last = course.course_decks.order_by("-order_index", "-id").first()
        return (last.order_index + 1) if last else 0

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="X-User-Id",
                type=int,
                location=OpenApiParameter.HEADER,
                required=True,
                description="User ID injected by gateway",
            ),
            OpenApiParameter(
                name="X-User-Ismanager",
                type=str,
                location=OpenApiParameter.HEADER,
                required=False,
                description="Is user a manager",
            ),
        ]
    )
    @extend_schema(
        methods=["get"],
        responses=CourseDeckSerializer(many=True),
        description="Список колод, привязанных к курсу.",
    )
    @extend_schema(
        methods=["post"],
        request=CourseDeckCreateUpdateSerializer,
        responses=CourseDeckSerializer,
        description="Создать привязку колоды к курсу.",
    )
    @action(detail=True, methods=["get", "post"], url_path="decks")
    def decks(self, request, pk=None):
        course: Course = self.get_object()
        user: UserContext = request.user

        if request.method.lower() == "get":
            queryset = course.course_decks.order_by("order_index", "id")
            serializer = CourseDeckSerializer(
                queryset, many=True, context={"request": request}
            )
            return Response(serializer.data)

        serializer = CourseDeckCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deck_id = serializer.validated_data["deck_id"]
        if course.course_decks.filter(deck_id=deck_id).exists() is True:
            raise ValidationError({"detail": "Deck with this id already exists"})

        order_index = serializer.validated_data.get("order_index")
        if order_index is None:
            order_index = self._get_next_order_index(course)

        self._check_deck_permissions(deck_id, course, user)

        coursedeck = CourseDeck.objects.create(
            course=course,
            deck_id=deck_id,
            order_index=order_index,
        )
        return Response(
            CourseDeckSerializer(coursedeck, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=CourseDeckReorderItemSerializer(many=True),
        responses=CourseDeckSerializer(many=True),
        description="Батч-переупорядочивание колод в курсе.",
    )
    @action(detail=True, methods=["post"], url_path="decks/reorder")
    def decks_reorder(self, request, pk=None):
        course = self.get_object()
        items = request.data
        if not isinstance(items, list):
            raise ValidationError(
                {"detail": "Expected a list of objects with id and order_index"}
            )

        ids = []
        for item in items:
            if not isinstance(item, dict):
                raise ValidationError({"detail": "Each item must be an object"})
            if "id" not in item or "order_index" not in item:
                raise ValidationError(
                    {"detail": "Each item must have id and order_index"}
                )
            ids.append(item["id"])
            if not isinstance(item["order_index"], int):
                raise ValidationError({"detail": "order_index must be int"})

        course_decks = {cd.id: cd for cd in course.course_decks.filter(id__in=ids)}
        if len(course_decks) != len(set(ids)):
            raise ValidationError(
                {"detail": "Some course_deck ids do not belong to this course"}
            )

        with transaction.atomic():
            for item in items:
                cd = course_decks[item["id"]]
                cd.order_index = item["order_index"]
                cd.save(update_fields=["order_index"])

        ordered = course.course_decks.order_by("order_index", "id")
        return Response(
            CourseDeckSerializer(ordered, many=True, context={"request": request}).data
        )

    @extend_schema(
        request=CourseDeckCreateUpdateSerializer(many=True),
        responses=CourseDeckSerializer(many=True),
        description="Батч-добавление колод в курс.",
    )
    @action(detail=True, methods=["post"], url_path="decks/batch")
    def decks_batch(self, request, pk=None):
        course = self.get_object()
        user: UserContext = request.user
        items = request.data

        if not isinstance(items, list):
            raise ValidationError({"detail": "Expected a list of objects with deck_id"})

        if not items:
            raise ValidationError({"detail": "List cannot be empty"})

        # Валидация входных данных
        deck_ids = []
        for item in items:
            if not isinstance(item, dict):
                raise ValidationError({"detail": "Each item must be an object"})
            if "deck_id" not in item:
                raise ValidationError({"detail": "Each item must have deck_id"})
            deck_id = item["deck_id"]
            if not isinstance(deck_id, int):
                raise ValidationError({"detail": "deck_id must be int"})
            deck_ids.append(deck_id)

        # Проверка на дубликаты во входных данных
        if len(deck_ids) != len(set(deck_ids)):
            raise ValidationError({"detail": "Duplicate deck_ids in request"})

        # Проверка, что колоды еще не привязаны к курсу
        existing_deck_ids = set(
            course.course_decks.filter(deck_id__in=deck_ids).values_list(
                "deck_id", flat=True
            )
        )
        if existing_deck_ids:
            raise ValidationError(
                {
                    "detail": f"Decks with ids {list(existing_deck_ids)} are already attached to this course"
                }
            )

        # Проверка прав на все колоды
        for deck_id in deck_ids:
            self._check_deck_permissions(deck_id, course, user)

        # Получаем начальный order_index
        start_order_index = self._get_next_order_index(course)

        # Создаем все CourseDeck записи
        created_decks = []
        with transaction.atomic():
            for idx, deck_id in enumerate(deck_ids):
                order_index = start_order_index + idx
                coursedeck = CourseDeck.objects.create(
                    course=course,
                    deck_id=deck_id,
                    order_index=order_index,
                )
                created_decks.append(coursedeck)

        serializer = CourseDeckSerializer(
            created_decks, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        methods=["get"],
        responses=CourseDeckSerializer,
        description="Получить информацию о привязке конкретной колоды в курсе.",
    )
    @extend_schema(
        methods=["patch"],
        request=CourseDeckCreateUpdateSerializer,
        responses=CourseDeckSerializer,
        description="Обновить привязку колоды в курсе.",
    )
    @extend_schema(
        methods=["delete"],
        responses=None,
        description="Удалить привязку колоды из курса.",
    )
    @action(
        detail=True,
        methods=["get", "patch", "delete"],
        url_path="decks/(?P<deck_rel_id>\\d+)",
    )
    def deck_detail(self, request, pk=None, deck_rel_id=None):
        course = self.get_object()
        user: UserContext = request.user
        try:
            coursedeck = course.course_decks.get(id=deck_rel_id)
        except CourseDeck.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.method.lower() == "get":
            return Response(
                CourseDeckSerializer(coursedeck, context={"request": request}).data
            )

        if request.method.lower() == "delete":
            coursedeck.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # PATCH
        serializer = CourseDeckCreateUpdateSerializer(
            coursedeck, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        new_deck_id = serializer.validated_data.get("deck_id")
        if new_deck_id and new_deck_id != coursedeck.deck_id:
            self._check_deck_permissions(new_deck_id, course, user)
            coursedeck.deck_id = new_deck_id

        for attr in ["order_index"]:
            if attr in serializer.validated_data:
                setattr(coursedeck, attr, serializer.validated_data[attr])
        coursedeck.save()

        return Response(
            CourseDeckSerializer(coursedeck, context={"request": request}).data
        )
