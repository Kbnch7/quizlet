from rest_framework import serializers
from typing import Optional, Dict, Any
from drf_spectacular.utils import extend_schema_field
from .models import Lesson


class LessonListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка уроков (GET /api/lessons/)"""
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'order_index', 'deck_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'course', 'created_at', 'updated_at']


class LessonCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания урока (POST /api/lessons/)"""
    deck_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'order_index', 'deck_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LessonUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления урока (PATCH/PUT /api/lessons/{id}/)"""
    deck_id = serializers.IntegerField(required=False, allow_null=True)
    course = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'order_index', 'deck_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'course', 'created_at', 'updated_at']


class LessonDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра урока (GET /api/lessons/{id}/)"""
    deck_id = serializers.IntegerField(read_only=True)
    deck_info = serializers.SerializerMethodField()
    
    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_deck_info(self, obj) -> Optional[Dict[str, Any]]:
        if not obj.deck_id:
            return None
        
        request = self.context.get('request')
        if not request:
            return None
        
        from common.clients.decks_client import decks_client
        token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        return decks_client.get_deck_sync(obj.deck_id, token=token)
    
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'order_index', 'deck_id', 'deck_info', 'created_at', 'updated_at']
        read_only_fields = ['id', 'course', 'deck_id', 'created_at', 'updated_at']
