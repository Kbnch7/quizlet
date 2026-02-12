from rest_framework import serializers
from .models import Enrollment, DeckProgress
from apps.courses.models import CourseDeck
from typing import Optional, Dict, Any
from drf_spectacular.utils import extend_schema_field
from common.clients.decks_client import decks_client


class DeckWithProgressSerializer(serializers.ModelSerializer):
    """Колодa курса с данными о прогрессе студента."""
    deck_info = serializers.SerializerMethodField()
    is_completed = serializers.BooleanField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True, allow_null=True)
    last_accessed_at = serializers.DateTimeField(read_only=True, allow_null=True)

    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_deck_info(self, obj: CourseDeck) -> Optional[Dict[str, Any]]:
        if not obj.deck_id:
            return None

        request = self.context.get('request')
        if not request:
            return None

        token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        return decks_client.get_deck_sync(obj.deck_id, token=token)

    class Meta:
        model = CourseDeck
        fields = [
            'id',
            'course',
            'deck_id',
            'order_index',
            'deck_info',
            'is_completed',
            'completed_at',
            'last_accessed_at',
        ]
        read_only_fields = ['id', 'course']


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
    decks = serializers.SerializerMethodField()
    
    class Meta(EnrollmentBaseSerializer.Meta):
        fields = EnrollmentBaseSerializer.Meta.fields + ['decks']
        read_only_fields = ['id', 'course', 'student_id', 'enrolled_at', 'completed_at', 'progress_percent']
    
    def get_decks(self, obj):
        course_decks = obj.course.course_decks.all().order_by('order_index', 'id')
        deck_progresses = {
            dp.course_deck_id: dp
            for dp in obj.deck_progresses.select_related('course_deck').all()
        }
        
        result = []
        for course_deck in course_decks:
            deck_data = DeckWithProgressSerializer(course_deck, context=self.context).data
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
        
        return result
