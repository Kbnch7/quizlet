# Ruzlet

Приложение для изучения материалов с использованием карточек и колод.

## Архитектура

Проект построен на микросервисной архитектуре:

- **Backend**: Python микросервисы (FastAPI + Django)
- **База данных**: PostgreSQL (отдельная для каждого сервиса)
- **Кэш**: Redis
- **Очередь сообщений**: Kafka (Confluent Platform)
- **Хранилище событий**: ClickHouse
- **Объектное хранилище**: MinIO

## Бэкенд

Бэкенд расположен в директории `backend/` и состоит из следующих сервисов:

### Сервисы

| Сервис | Фреймворк | Порт | Описание |
|--------|-----------|------|----------|
| **gateway** | FastAPI | 8000 | API Gateway для маршрутизации запросов и аутентификации |
| **auth** | FastAPI | 8005 | Сервис аутентификации и авторизации (JWT) |
| **users** | FastAPI | 8004 | Управление пользователями |
| **decks** | FastAPI | 8001 | Управление колодами и карточками, режим изучения, тестирование |
| **teaching** | Django | 8002 | Управление курсами и образовательным контентом |
| **events-collector** | Python | 8006 | Сбор и обработка событий из Kafka в ClickHouse |

### Gateway

Все внешние запросы проходят через Gateway на порту 8000:

```
http://localhost:8000/<service>/<endpoint>
```

Примеры:
- Получение колод: `GET http://localhost:8000/decks/decks/`
- Регистрация: `POST http://localhost:8000/auth/register`

### Kafka и события

Сервисы публикуют события в Kafka для асинхронной коммуникации:
- `learning.events` — события обучения
- `course.events` — события курсов
- `content.events` — события контента
- `user.events` — события пользователей

Контракты событий описаны в отдельном репозитории `quizlet_event_contracts`.

### ClickHouse

Используется для хранения аналитики и событий:
- Пользователь `analytics_writer` — запись данных
- Пользователь `analytics_reader` — чтение данных

## Запуск бэкенда

```bash
cd backend
cp .env-example .env
docker compose up
```

Применение миграций:
```bash
# Django
docker compose exec teaching python manage.py migrate

# ClickHouse (внутри контейнера events-collector)
cd src && python3 migrate.py
```

## Порты

| Сервис | URL / Порт |
|--------|------------|
| Gateway | http://localhost:8000 |
| Users API | http://localhost:8004 |
| Auth API | http://localhost:8005 |
| Decks API | http://localhost:8001 |
| Teaching API | http://localhost:8002 |
| MinIO Console | http://localhost:9001 |
| Kafka UI | http://localhost:8080 |
| PostgreSQL Users | http://localhost:5433 |
| PostgreSQL Decks | http://localhost:5435 |
| PostgreSQL Teaching | http://localhost:5436 |

## Документация API

- Users API: http://localhost:8004/api/docs
- Auth API: http://localhost:8005/api/docs
- Decks API: http://localhost:8001/api/docs
- Teaching API: http://localhost:8002/api/docs

