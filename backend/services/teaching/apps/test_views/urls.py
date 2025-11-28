from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('my-courses/', views.my_courses, name='my_courses'),
]

