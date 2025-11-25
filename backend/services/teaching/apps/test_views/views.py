from django.shortcuts import render, get_object_or_404
from apps.courses.models import Course
from apps.lessons.models import Lesson
from apps.enrollments.models import Enrollment
from common.clients.decks_client import decks_client


def course_list(request):
    courses = Course.objects.filter(is_published=True).order_by('-created_at')
    context = {
        'courses': courses,
    }
    return render(request, 'test_views/course_list.html', context)


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all().order_by('order_index')
    
    lessons_with_decks = []
    for lesson in lessons:
        deck_info = None
        if lesson.deck_id:
            deck_info = decks_client.get_deck_sync(lesson.deck_id)
        lessons_with_decks.append({
            'lesson': lesson,
            'deck': deck_info,
        })
    
    context = {
        'course': course,
        'lessons_with_decks': lessons_with_decks,
    }
    return render(request, 'test_views/course_detail.html', context)


def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    deck_info = None
    
    if lesson.deck_id:
        deck_info = decks_client.get_deck_sync(lesson.deck_id)
    
    context = {
        'lesson': lesson,
        'deck': deck_info,
    }
    return render(request, 'test_views/lesson_detail.html', context)


def my_courses(request):
    return render(request, 'test_views/my_courses.html', {})

