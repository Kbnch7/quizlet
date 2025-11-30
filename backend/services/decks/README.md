1) Создаем .env файл
```
cp .env-example .env
```

2) Запускаем docker сервисы

Запуск БД
```
docker compose up db
```
Запуск хранилища файлов
```
docker compose up minio
```
Запуск api
```
docker compose up api
```

3) Инициализируем бд:
```
docker compose exec -it api python3 src/init_db.py
```

4) Заходим на веб интерфейс minio и создаем пользователя с логином и паролем, совпадающими с MINIO_ACCESS_KEY и MINIO_SECRET_KEY. 
5) Создаем bucket с названием cards

Swagger UI - localhost:8000/docs

# Примечания
1) При получении presinged url на загрузку объекта в хранилище, например
```json
{
  "put_url": "http://minio:9000/cards/temp/1/uploads/363775d16c56454eb5ba6a9ae0753b0e.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=miniouser%2F20251107%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20251107T123404Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=eeb8777584f1804cae463d9a5f78b16829c80dbc104e76476a68862732ee4238",
  "get_url": "http://minio:9000/cards/temp/1/uploads/363775d16c56454eb5ba6a9ae0753b0e.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=miniouser%2F20251107%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20251107T123404Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=59e7df80b7c13cded55858db950dd750d56bb70fa7c57fe935920bf85dbb3be3",
  "object_key": "temp/1/uploads/363775d16c56454eb5ba6a9ae0753b0e.jpeg"
}
```
когда мы отправляем файл на put_url, важно, чтобы ссылка была точно такая же, какой и была выдана. То есть при отправке запросов с хоста, а не внутри сети docker, нельзя заменять minio:9000 на другой адрес. Для того, чтобы отправлять запросы с хоста, можно добавить строчку в /etc/hosts на хосте
```
127.0.0.1 minio
```
и тогда адреса будут совпадать и ошибок не будет.

2) Сейчас для аутентификации используется заглушка. при передаче любого токена в "Authorization": "Bearer -token-" будет возвращаться пользователь с id=1, но если токен будет заканчиаться на "-manager", то вернется админ-пользователь с id=2
