from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from common.permissions import IsCourseTeacherOrManager
from common.pagination import CreatedAtCursorPagination
from common.auth import UserContext
from common.clients.decks_client import decks_client
from .models import Lesson
from .serializers import (
    LessonListSerializer,
    LessonCreateSerializer,
    LessonUpdateSerializer,
    LessonDetailSerializer
)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CreatedAtCursorPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LessonListSerializer
        elif self.action == 'create':
            return LessonCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LessonUpdateSerializer
        elif self.action == 'retrieve':
            return LessonDetailSerializer
        return LessonListSerializer
    
    def get_queryset(self):
        queryset = Lesson.objects.all()
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset.order_by('-created_at', 'id')
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsCourseTeacherOrManager()]
        return [IsAuthenticated()]
    
    def _check_deck_permissions(self, deck_id: int, course, user: UserContext) -> None:
        """Проверка прав на использование колоды в уроке"""
        if not deck_id:
            return
        
        deck = decks_client.get_deck_sync(
            deck_id,
            token=self.request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        )
        
        if not deck:
            raise ValidationError({'deck_id': 'Deck not found'})
        
        if user.is_manager:
            return
        
        if deck['owner_id'] != course.teacher_id:
            raise PermissionDenied(
                "You can only use decks owned by the course teacher"
            )
    
    def perform_create(self, serializer):
        user: UserContext = self.request.user
        course = serializer.validated_data['course']
        deck_id = serializer.validated_data.get('deck_id')
        
        if course.teacher_id != user.id and not user.is_manager:
            raise PermissionDenied("You can only create lessons for your own courses")
        
        if deck_id:
            self._check_deck_permissions(deck_id, course, user)
        
        serializer.save()
    
    def perform_update(self, serializer):
        user: UserContext = self.request.user
        lesson = self.get_object()
        course = lesson.course
        
        new_deck_id = serializer.validated_data.get('deck_id')
        if new_deck_id is not None and new_deck_id != lesson.deck_id:
            self._check_deck_permissions(new_deck_id, course, user)
        
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()

