from django.contrib import admin
from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course', 'order_index', 'deck_id', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['course', 'order_index']

