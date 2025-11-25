from django.db import models
from apps.courses.models import Course
from apps.lessons.models import Lesson


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
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0.0
        completed_lessons = self.lesson_progresses.filter(is_completed=True).count()
        return (completed_lessons / total_lessons) * 100.0
    
    def is_completed(self):
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return False
        completed_lessons = self.lesson_progresses.filter(is_completed=True).count()
        return completed_lessons == total_lessons


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progresses')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['enrollment', 'lesson']]
        indexes = [
            models.Index(fields=['enrollment', 'is_completed']),
        ]
    
    def __str__(self):
        return f"{self.enrollment} - {self.lesson.title}"

