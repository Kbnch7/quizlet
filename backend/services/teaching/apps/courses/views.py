from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from common.auth import UserContext
from common.permissions import IsCourseTeacherOrManager
from .models import Course
from .serializers import (
    CourseListSerializer,
    CourseCreateSerializer,
    CourseUpdateSerializer,
    CourseDetailSerializer
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        elif self.action == 'create':
            return CourseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CourseUpdateSerializer
        elif self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer
    
    def get_queryset(self):
        user: UserContext = self.request.user
        queryset = Course.objects.all()
        
        teacher_id = self.request.query_params.get('teacher_id')
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        
        is_published = self.request.query_params.get('is_published')
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published.lower() == 'true')
        
        if not user.is_manager:
            queryset = queryset.filter(
                Q(is_published=True) | Q(teacher_id=user.id)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        user: UserContext = self.request.user
        teacher_id = serializer.validated_data.get('teacher_id')
        
        if teacher_id is None:
            teacher_id = user.id
        else:
            if not user.is_manager:
                raise PermissionDenied("Only managers can set teacher_id")
        
        serializer.save(teacher_id=teacher_id)
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy', 'publish', 'unpublish']:
            return [IsCourseTeacherOrManager()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        course = self.get_object()
        course.is_published = True
        course.save()
        return Response({'status': 'published'})
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        course = self.get_object()
        course.is_published = False
        course.save()
        return Response({'status': 'unpublished'})

