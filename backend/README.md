# Запуск бекенда

```
cp .env-example .env
docker compose up
```

## Основные порты

- Gateway http://localhost:8000 — единая точка входа для всех API
- Users API http://localhost:8004
- Auth API http://localhost:8005
- Decks API http://localhost:8001
- Teaching API http://localhost:8002
- MinIO Console http://localhost:9001
- Redis localhost:6378

БД:

- Users PostgreSQL: localhost:5433
- Decks PostgreSQL: localhost:5435
- Teaching PostgreSQL: localhost:5436

## Эндпоинты

- Users API http://localhost:8004/api/docs
- Auth API http://localhost:8005/api/docs
- Decks API http://localhost:8001/api/docs
- Teaching API http://localhost:8002/api/docs

## Gateway

Gateway проксирует запросы к сервисам
Для обращения к конкретному сервису url будет выглядеть так:

```
http://localhost:8000/<auth|users|decks|teching>/<эндпоинт на сервисе>
```

Например для получения списка колод:

```
GET http://localhost:8000/decks/decks
```

Для регистрации:

```
POST http://localhost:8000/auth/register
```
