from django.contrib import admin
from .models import Enrollment, DeckProgress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    def get_progress_percent(self, obj):
        return f"{obj.get_progress_percent():.1f}%"
    get_progress_percent.short_description = 'Progress'
    
    list_display = ['id', 'course', 'student_id', 'get_progress_percent', 'enrolled_at', 'completed_at']
    list_filter = ['enrolled_at', 'completed_at']
    search_fields = ['student_id']


@admin.register(DeckProgress)
class DeckProgressAdmin(admin.ModelAdmin):
    list_display = ['id', 'enrollment', 'course_deck', 'is_completed', 'last_accessed_at']
    list_filter = ['is_completed', 'last_accessed_at']

