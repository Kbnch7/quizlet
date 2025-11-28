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
from .models import Enrollment, LessonProgress
from .serializers import (
    EnrollmentListSerializer,
    EnrollmentCreateSerializer,
    EnrollmentUpdateSerializer,
    EnrollmentDetailSerializer,
    LessonWithProgressSerializer
)
from apps.lessons.models import Lesson


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
    def lessons(self, request, pk=None):
        enrollment = self.get_object()
        lessons = enrollment.course.lessons.all().order_by('order_index', 'id')
        lesson_progresses = {
            lp.lesson_id: lp 
            for lp in enrollment.lesson_progresses.select_related('lesson').all()
        }
        
        result = []
        for lesson in lessons:
            lesson_data = LessonWithProgressSerializer(lesson, context={'request': request}).data
            progress = lesson_progresses.get(lesson.id)
            
            if progress:
                lesson_data['is_completed'] = progress.is_completed
                lesson_data['completed_at'] = progress.completed_at
                lesson_data['last_accessed_at'] = progress.last_accessed_at
            else:
                lesson_data['is_completed'] = False
                lesson_data['completed_at'] = None
                lesson_data['last_accessed_at'] = None
            
            result.append(lesson_data)
        
        return Response(result)
    
    @action(detail=True, methods=['get'], url_path='lessons/(?P<lesson_id>[^/.]+)')
    def lesson_detail(self, request, pk=None, lesson_id=None):
        enrollment = self.get_object()
        lesson = get_object_or_404(Lesson, id=lesson_id, course=enrollment.course)
        
        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={'is_completed': False}
        )
        
        lesson_data = LessonWithProgressSerializer(lesson, context={'request': request}).data
        lesson_data['is_completed'] = progress.is_completed
        lesson_data['completed_at'] = progress.completed_at
        lesson_data['last_accessed_at'] = progress.last_accessed_at
        
        return Response(lesson_data)
    
    @action(detail=True, methods=['post'], url_path='lessons/(?P<lesson_id>[^/.]+)/complete')
    def lesson_complete(self, request, pk=None, lesson_id=None):
        enrollment = self.get_object()
        lesson = get_object_or_404(Lesson, id=lesson_id, course=enrollment.course)
        
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={'is_completed': False}
        )
        
        progress.is_completed = True
        if not progress.completed_at:
            progress.completed_at = timezone.now()
        progress.last_accessed_at = timezone.now()
        progress.save()
        
        lesson_data = LessonWithProgressSerializer(lesson, context={'request': request}).data
        lesson_data['is_completed'] = progress.is_completed
        lesson_data['completed_at'] = progress.completed_at
        lesson_data['last_accessed_at'] = progress.last_accessed_at
        
        return Response(lesson_data)
    
    def get_permissions(self):
        if self.action in ['destroy', 'lessons', 'lesson_detail', 'lesson_complete']:
            return [IsEnrollmentStudentOrManager()]
        return [IsAuthenticated()]

