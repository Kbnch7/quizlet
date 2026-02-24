# Backend

Стек

- Backend: Python 3.11, FastAPI, Django
- СУБД: PostgreSQL для каждого сервиса (Users, Decks, Teaching)
- Очередь сообщений: Kafka (Confluent Platform)
- OLAP хранилище: ClickHouse
- Кеш: Redis
- Объектное хранилище: MinIO

## Запуск бэкенда

```
cp .env-example .env
docker compose up
```

Создание топиков в kafka с помощью terraform

```
cd kafka
terraform init
terraform plan
terraform apply
```

Применение миграций clickhouse

```
# В контейнере сервиса events-collector
cd src
python3 migrate.py
```

Инициализируем бд для сервиса decks:

```
docker compose exec decks python3 src/init_db.py
```

Заходим на веб интерфейс minio и создаем пользователя с логином и паролем, совпадающими с MINIO_ACCESS_KEY и MINIO_SECRET_KEY, и создаем bucket с названием `cards`

Особенности настройки для сервиса decks см. в `/backend/services/decks/README.md`

## Основные порты

| Сервис / UI         | URL / Порт                                     |
| ------------------- | ---------------------------------------------- |
| Gateway             | [http://localhost:8000](http://localhost:8000) |
| Users API           | [http://localhost:8004](http://localhost:8004) |
| Auth API            | [http://localhost:8005](http://localhost:8005) |
| Decks API           | [http://localhost:8001](http://localhost:8001) |
| Teaching API        | [http://localhost:8002](http://localhost:8002) |
| Prometheus          | [http://localhost:9090](http://localhost:9090) |
| Grafana             | [http://localhost:3000](http://localhost:3000) |
| MinIO Console       | [http://localhost:9001](http://localhost:9001) |
| Redis               | [http://localhost:6378](http://localhost:6378) |
| ClickHouse HTTP     | [http://localhost:8123](http://localhost:8123) |
| ClickHouse TCP      | [http://localhost:9000](http://localhost:9000) |
| Kafka Broker        | [http://localhost:9092](http://localhost:9092) |
| Kafka UI            | [http://localhost:8080](http://localhost:8080) |
| Users PostgreSQL    | [http://localhost:5433](http://localhost:5433) |
| Decks PostgreSQL    | [http://localhost:5435](http://localhost:5435) |
| Teaching PostgreSQL | [http://localhost:5436](http://localhost:5436) |

## Мониторинг и метрики

- **Prometheus**:
  - Конфиг: `backend/monitoring/prometheus.yml`.
  - Скрапит `/metrics` у сервисов:
    - Auth: `http://localhost:8005/metrics` (job `auth_service`),
    - Decks: `http://localhost:8001/metrics` (job `decks_service`),
    - Teaching: `http://localhost:8002/metrics` (job `teaching_service`),
    - MinIO: `http://localhost:9000/minio/v2/metrics/cluster` (job `minio_storage`).
- **Grafana**:
  - URL: `http://localhost:3000`.
  - Дашборды и датасорсы провиженятся из `backend/monitoring/grafana/`:
    - Дашборды сервисов: `decks_service_dashboard.json`, `teaching_service_dashboard.json`, `auth_service_dashboard.json`.
- **Типы метрик**:
  - HTTP-метрики: RPS, latency, 4xx/5xx по endpoint (например, `auth_http_requests_total`, `teaching_http_request_duration_seconds`, `http_requests_total` для decks).
  - Бизнес-метрики: счётчики доменных событий (создание колод/курсов, регистрации пользователей, логины и т.п.).
  - Внешние вызовы: метрики запросов из auth в users-сервис (`auth_users_service_requests_total`, `auth_users_service_request_duration_seconds`).

## Эндпоинты

- Users API http://localhost:8004/api/docs
- Auth API http://localhost:8005/api/docs
- Decks API http://localhost:8001/api/docs
- Teaching API http://localhost:8002/api/docs

## Gateway

Gateway проксирует запросы к сервисам

Для обращения к конкретному сервису url будет выглядеть так:

```
http://localhost:8000/<auth|users|decks|teaching>/<эндпоинт на сервисе>
```

Например для получения списка колод:

```
GET http://localhost:8000/decks/decks
```

Для регистрации:

```
POST http://localhost:8000/auth/register
```

## Kafka

В данный момент используется для событий в сервисах decks, teaching, auth с дальнейшей обработкой в сервисе `events-collector` и сохранения в `clickhouse`

Топики:

- learning.events
- course.events
- content.events
- user.events

Контракт событий описан в репозитории github.com/delawer33/quizlet_event_contracts, он подключается как библиотека в сервисах

## Clickhouse

Используется как хранилище для аналитики и событий.

Пользователи:

- analytics_writer — запись данных
- analytics_reader — чтение данных (для аналитических сервисов)

Миграции:
Таблицы создаются через отдельный скрипт migrate.py из events-collector под пользователем analytics_writer.

## Events Collector

Сервис считывает события из Kafka и сохраняет их в ClickHouse.

Принцип работы:

- Подписка на Kafka-топики
- Буферизация событий в памяти и запись батчами в ClickHouse
- Commit offset после успешной записи
- Гарантия at-least-once delivery
