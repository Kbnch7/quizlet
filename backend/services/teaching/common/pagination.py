from rest_framework.pagination import CursorPagination


class CreatedAtCursorPagination(CursorPagination):
    ordering = '-created_at'
    page_size = 20


class EnrolledAtCursorPagination(CursorPagination):
    ordering = '-enrolled_at'
    page_size = 20


class IdCursorPagination(CursorPagination):
    ordering = '-id'
    page_size = 20

