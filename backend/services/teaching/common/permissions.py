from rest_framework import permissions
from common.auth import UserContext


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user: UserContext = request.user
        return user.is_manager
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        user: UserContext = request.user
        return user.is_manager


class IsCourseTeacherOrManager(permissions.BasePermission):
    """Проверка прав для Course и Lesson (через course.teacher_id)"""
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        user: UserContext = request.user
        if user.is_manager:
            return True
        if hasattr(obj, 'teacher_id'):
            return obj.teacher_id == user.id
        elif hasattr(obj, 'course'):
            return obj.course.teacher_id == user.id
        
        return False


class IsEnrollmentStudentOrManager(permissions.BasePermission):
    """Проверка прав для Enrollment (student_id)"""
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        user: UserContext = request.user
        if user.is_manager:
            return True
        return obj.student_id == user.id

