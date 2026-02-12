from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str
    kafka_group_id: str = "events-consumer"
    kafka_topics: str

    clickhouse_host: str
    clickhouse_port: int = 9000
    clickhouse_database: str
    clickhouse_user_writer: str
    clickhouse_password_writer: str
    clickhouse_user_reader: str
    clickhouse_password_reader: str
