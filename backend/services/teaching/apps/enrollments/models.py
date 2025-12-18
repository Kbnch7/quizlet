from django.db import models
from apps.courses.models import Course, CourseDeck


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    student_id = models.IntegerField()
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = [['course', 'student_id']]
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['course', 'student_id']),
        ]
    
    def __str__(self):
        return f"Student {self.student_id} - {self.course.title}"
    
    def get_progress_percent(self):
        total_items = self.course.course_decks.count()
        if total_items == 0:
            return 0.0
        completed_items = self.deck_progresses.filter(is_completed=True).count()
        return (completed_items / total_items) * 100.0
    
    def is_completed(self):
        total_items = self.course.course_decks.count()
        if total_items == 0:
            return False
        completed_items = self.deck_progresses.filter(is_completed=True).count()
        return completed_items == total_items


class DeckProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='deck_progresses')
    course_deck = models.ForeignKey(CourseDeck, on_delete=models.CASCADE, related_name='progresses')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['enrollment', 'course_deck']]
        indexes = [
            models.Index(fields=['enrollment', 'is_completed']),
        ]
    
    def __str__(self):
        return f"{self.enrollment} - deck {self.course_deck.deck_id}"

