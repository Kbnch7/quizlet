from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.courses.views import CourseViewSet
from apps.lessons.views import LessonViewSet
from apps.enrollments.views import EnrollmentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]

