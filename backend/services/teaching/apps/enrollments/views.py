from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from django.utils import timezone
from django.db.models import Q
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from common.auth import UserContext
from common.permissions import IsEnrollmentStudentOrManager
from common.pagination import EnrolledAtCursorPagination
from .models import Enrollment, DeckProgress
from .serializers import (
    EnrollmentListSerializer,
    EnrollmentCreateSerializer,
    EnrollmentUpdateSerializer,
    EnrollmentDetailSerializer,
    DeckWithProgressSerializer,
)
from apps.courses.models import CourseDeck


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = EnrolledAtCursorPagination
    
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EnrollmentListSerializer
        elif self.action == 'create':
            return EnrollmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EnrollmentUpdateSerializer
        elif self.action == 'retrieve':
            return EnrollmentDetailSerializer
        return EnrollmentListSerializer

    def get_queryset(self):
        user: UserContext = self.request.user
        queryset = Enrollment.objects.all()
        student_id = self.request.query_params.get('student_id')
        course_id = self.request.query_params.get('course_id')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        if not user.is_manager:
            queryset = queryset.filter(
                Q(student_id=user.id) | Q(course__teacher_id=user.id)
            )
        
        return queryset.order_by('-enrolled_at')
    
    def perform_create(self, serializer):
        user: UserContext = self.request.user
        course = serializer.validated_data.get('course')

        if not course.is_published:
            raise ValidationError({
                'course': ['Cannot enroll in unpublished course']
            })
        
        student_id = serializer.validated_data.get('student_id')
        
        if student_id is None:
            student_id = user.id
        else:
            if not user.is_manager:
                raise PermissionDenied("Only managers can set student_id")
        
        try:
            serializer.save(student_id=student_id)
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower() or 'duplicate key' in str(e).lower():
                raise ValidationError({
                    'non_field_errors': ['Enrollment for this course and student already exists.']
                })
            raise
    
    def update(self, request, *args, **kwargs):
        return Response(
            {'error': 'Update is not allowed for enrollment'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'error': 'Update is not allowed for enrollment'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    @action(detail=True, methods=['get'])
    def decks(self, request, pk=None):
        enrollment = self.get_object()
        course_decks = enrollment.course.course_decks.order_by('order_index', 'id')
        deck_progresses = {
            dp.course_deck_id: dp
            for dp in enrollment.deck_progresses.select_related('course_deck').all()
        }
        
        result = []
        for course_deck in course_decks:
            deck_data = DeckWithProgressSerializer(course_deck, context={'request': request}).data
            progress = deck_progresses.get(course_deck.id)
            
            if progress:
                deck_data['is_completed'] = progress.is_completed
                deck_data['completed_at'] = progress.completed_at
                deck_data['last_accessed_at'] = progress.last_accessed_at
            else:
                deck_data['is_completed'] = False
                deck_data['completed_at'] = None
                deck_data['last_accessed_at'] = None
            
            result.append(deck_data)
        
        return Response(result)
    
    @action(detail=True, methods=['get'], url_path='decks/(?P<deck_rel_id>\\d+)')
    def deck_detail(self, request, pk=None, deck_rel_id=None):
        """
        deck_rel_id — это ID CourseDeck (связка курс-колода), а не ID самой колоды.
        """
        enrollment = self.get_object()
        course_deck = get_object_or_404(CourseDeck, id=deck_rel_id, course=enrollment.course)
        
        progress, _ = DeckProgress.objects.get_or_create(
            enrollment=enrollment,
            course_deck=course_deck,
            defaults={'is_completed': False},
        )
        
        deck_data = DeckWithProgressSerializer(course_deck, context={'request': request}).data
        deck_data['is_completed'] = progress.is_completed
        deck_data['completed_at'] = progress.completed_at
        deck_data['last_accessed_at'] = progress.last_accessed_at
        
        return Response(deck_data)
    
    @action(detail=True, methods=['post'], url_path='decks/(?P<deck_rel_id>\\d+)/complete')
    def deck_complete(self, request, pk=None, deck_rel_id=None):
        enrollment = self.get_object()
        course_deck = get_object_or_404(CourseDeck, id=deck_rel_id, course=enrollment.course)
        
        progress, _ = DeckProgress.objects.get_or_create(
            enrollment=enrollment,
            course_deck=course_deck,
            defaults={'is_completed': False},
        )
        
        progress.is_completed = True
        if not progress.completed_at:
            progress.completed_at = timezone.now()
        progress.last_accessed_at = timezone.now()
        progress.save()
        
        deck_data = DeckWithProgressSerializer(course_deck, context={'request': request}).data
        deck_data['is_completed'] = progress.is_completed
        deck_data['completed_at'] = progress.completed_at
        deck_data['last_accessed_at'] = progress.last_accessed_at
        
        return Response(deck_data)
    
    def get_permissions(self):
        if self.action in ['destroy', 'decks', 'deck_detail', 'deck_complete']:
            return [IsEnrollmentStudentOrManager()]
        return [IsAuthenticated()]

