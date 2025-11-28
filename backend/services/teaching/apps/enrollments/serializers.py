from rest_framework import serializers
from .models import Enrollment
from apps.lessons.serializers import LessonListSerializer


class LessonWithProgressSerializer(LessonListSerializer):
    is_completed = serializers.BooleanField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True, allow_null=True)
    last_accessed_at = serializers.DateTimeField(read_only=True, allow_null=True)
    
    class Meta(LessonListSerializer.Meta):
        fields = LessonListSerializer.Meta.fields + ['is_completed', 'completed_at', 'last_accessed_at']


class EnrollmentBaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор с общими полями и методами"""
    progress_percent = serializers.SerializerMethodField()
    
    def get_progress_percent(self, obj):
        return obj.get_progress_percent()
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'student_id', 'enrolled_at', 'completed_at', 'progress_percent']


class EnrollmentListSerializer(EnrollmentBaseSerializer):
    """Сериализатор для списка enrollment (GET /api/enrollments/)"""
    class Meta(EnrollmentBaseSerializer.Meta):
        read_only_fields = ['id', 'course', 'student_id', 'enrolled_at', 'completed_at', 'progress_percent']


class EnrollmentCreateSerializer(EnrollmentBaseSerializer):
    """Сериализатор для создания enrollment (POST /api/enrollments/)"""
    class Meta(EnrollmentBaseSerializer.Meta):
        read_only_fields = ['id', 'enrolled_at', 'completed_at', 'progress_percent']
        extra_kwargs = {
            'student_id': {'required': False, 'allow_null': True}
        }
    
    def to_internal_value(self, data):
        if 'student_id' not in data:
            data = data.copy()
            data['student_id'] = None
        return super().to_internal_value(data)


class EnrollmentUpdateSerializer(EnrollmentBaseSerializer):
    """Сериализатор для обновления enrollment (PATCH/PUT /api/enrollments/{id}/) - все поля read-only"""
    course = serializers.PrimaryKeyRelatedField(read_only=True)
    student_id = serializers.IntegerField(read_only=True)
    
    class Meta(EnrollmentBaseSerializer.Meta):
        read_only_fields = ['id', 'course', 'student_id', 'enrolled_at', 'completed_at', 'progress_percent']


class EnrollmentDetailSerializer(EnrollmentBaseSerializer):
    """Сериализатор для детального просмотра enrollment (GET /api/enrollments/{id}/)"""
    lessons = serializers.SerializerMethodField()
    
    class Meta(EnrollmentBaseSerializer.Meta):
        fields = EnrollmentBaseSerializer.Meta.fields + ['lessons']
        read_only_fields = ['id', 'course', 'student_id', 'enrolled_at', 'completed_at', 'progress_percent']
    
    def get_lessons(self, obj):
        lessons = obj.course.lessons.all().order_by('order_index', 'id')
        lesson_progresses = {
            lp.lesson_id: lp 
            for lp in obj.lesson_progresses.select_related('lesson').all()
        }
        
        result = []
        for lesson in lessons:
            lesson_data = LessonListSerializer(lesson, context=self.context).data
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
        
        return result
