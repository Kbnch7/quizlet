from rest_framework import serializers
from .models import Course, CourseDeck
from typing import Optional, Dict, Any
from drf_spectacular.utils import extend_schema_field
from common.clients.decks_client import decks_client


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


class CourseDeckSerializer(serializers.ModelSerializer):
    deck_info = serializers.SerializerMethodField()

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
        fields = ['id', 'course', 'deck_id', 'order_index', 'deck_info']
        read_only_fields = ['id', 'course']


class CourseDeckCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление привязки колоды к курсу."""
    deck_id = serializers.IntegerField(required=True)
    order_index = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = CourseDeck
        fields = ['id', 'deck_id', 'order_index']
        read_only_fields = ['id']


class CourseDeckReorderItemSerializer(serializers.Serializer):
    """Элемент для батч-переупорядочивания колод в курсе."""
    id = serializers.IntegerField()
    order_index = serializers.IntegerField()


class CourseDetailSerializer(CourseBaseSerializer):
    """Сериализатор для детального просмотра курса (GET /api/courses/{id}/)"""
    decks = CourseDeckSerializer(source='course_decks', many=True, read_only=True)
    
    class Meta(CourseBaseSerializer.Meta):
        fields = CourseBaseSerializer.Meta.fields + ['decks']
        read_only_fields = ['id', 'title', 'description', 'teacher_id', 'is_published', 'created_at', 'updated_at']
