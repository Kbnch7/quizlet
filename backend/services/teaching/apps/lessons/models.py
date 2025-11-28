from django.db import models
from apps.courses.models import Course


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order_index = models.IntegerField(default=0)
    deck_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order_index', 'id']
        indexes = [
            models.Index(fields=['course', 'order_index']),
            models.Index(fields=['deck_id']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

