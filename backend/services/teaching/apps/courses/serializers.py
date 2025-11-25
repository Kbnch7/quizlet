from rest_framework import serializers
from .models import Course
from apps.lessons.serializers import LessonListSerializer


class CourseBaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор с общими полями"""
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher_id', 'is_published', 'created_at', 'updated_at']


class CourseListSerializer(CourseBaseSerializer):
    """Сериализатор для списка курсов (GET /api/courses/)"""
    class Meta(CourseBaseSerializer.Meta):
        read_only_fields = ['id', 'title', 'description', 'teacher_id', 'is_published', 'created_at', 'updated_at']


class CourseCreateSerializer(CourseBaseSerializer):
    """Сериализатор для создания курса (POST /api/courses/)"""
    teacher_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta(CourseBaseSerializer.Meta):
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'is_published': {'required': False}
        }


class CourseUpdateSerializer(CourseBaseSerializer):
    """Сериализатор для обновления курса (PATCH/PUT /api/courses/{id}/)"""
    teacher_id = serializers.IntegerField(read_only=True)
    
    class Meta(CourseBaseSerializer.Meta):
        read_only_fields = ['id', 'teacher_id', 'created_at', 'updated_at']


class CourseDetailSerializer(CourseBaseSerializer):
    """Сериализатор для детального просмотра курса (GET /api/courses/{id}/)"""
    lessons = LessonListSerializer(many=True, read_only=True)
    
    class Meta(CourseBaseSerializer.Meta):
        fields = CourseBaseSerializer.Meta.fields + ['lessons']
        read_only_fields = ['id', 'title', 'description', 'teacher_id', 'is_published', 'created_at', 'updated_at']
