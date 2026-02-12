# Teaching Service

Django REST Framework сервис для управления курсами, уроками и записями студентов.

## Запуск

1. Скопируйте `.env.example` в `.env` и при необходимости измените переменные:
```bash
cp .env.example .env
```

2. Запустите сервисы через Docker Compose:
```bash
docker-compose up -d
```

3. Сервис будет доступен по адресу: http://localhost:8001

## API Endpoints

### Courses (`/api/courses/`)
- `GET /api/courses/` - список курсов
- `POST /api/courses/` - создать курс
- `GET /api/courses/{id}/` - детали курса
- `PUT /api/courses/{id}/` - обновить курс
- `PATCH /api/courses/{id}/` - частично обновить курс
- `DELETE /api/courses/{id}/` - удалить курс
- `POST /api/courses/{id}/publish/` - опубликовать курс
- `POST /api/courses/{id}/unpublish/` - снять с публикации

### Lessons (`/api/lessons/`)
- `GET /api/lessons/` - список уроков
- `POST /api/lessons/` - создать урок
- `GET /api/lessons/{id}/` - детали урока (с deck_info)
- `PUT /api/lessons/{id}/` - обновить урок
- `PATCH /api/lessons/{id}/` - частично обновить урок
- `DELETE /api/lessons/{id}/` - удалить урок

### Enrollments (`/api/enrollments/`)
- `GET /api/enrollments/` - список записей на курсы
- `POST /api/enrollments/` - записаться на курс
- `GET /api/enrollments/{id}/` - детали записи (с уроками и прогрессом)
- `DELETE /api/enrollments/{id}/` - отписаться от курса
- `GET /api/enrollments/{id}/lessons/` - список уроков с прогрессом
- `GET /api/enrollments/{id}/lessons/{lesson_id}/` - детали урока с прогрессом
- `POST /api/enrollments/{id}/lessons/{lesson_id}/complete/` - отметить урок завершенным

## Аутентификация

Все эндпоинты требуют аутентификации через Bearer токен:
```
Authorization: Bearer <token>
```

Для тестирования используйте токены:
- Обычный пользователь: `Bearer 1`, `Bearer 2`, и т.д.
- Менеджер: `Bearer 1-manager`, `Bearer 2-manager`, и т.д.

## Переменные окружения

См. `.env.example` для списка переменных окружения.

