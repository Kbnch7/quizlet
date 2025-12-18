from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    teacher_id = models.IntegerField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['teacher_id']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return self.title


class CourseDeck(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_decks')
    deck_id = models.IntegerField()
    order_index = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order_index', 'id']
        constraints = [
            models.UniqueConstraint(fields=['course', 'deck_id'], name='unique_course_deck'),
        ]
        indexes = [
            models.Index(fields=['course', 'order_index']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - deck {self.deck_id}"

