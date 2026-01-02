import logging

from clickhouse_driver import Client
from confluent_kafka import Consumer
from src.config.log_settings import configure_logging
from src.config.settings import Settings
from src.consumer.consumer import KafkaEventConsumer


def create_kafka_consumer(settings: Settings) -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.kafka_group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "session.timeout.ms": 10000,
            "max.poll.interval.ms": 300000,
        }
    )


def create_clickhouse_client(settings: Settings) -> Client:
    return Client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        database=settings.clickhouse_database,
        user=settings.clickhouse_user_writer,
        password=settings.clickhouse_password_writer,
        send_receive_timeout=10,
    )


def main():
    configure_logging("INFO")
    logger = logging.getLogger("main")

    settings = Settings()
    logger.info("Starting statistics service")

    clickhouse = create_clickhouse_client(settings)
    consumer = create_kafka_consumer(settings)

    service = KafkaEventConsumer(
        consumer=consumer,
        clickhouse=clickhouse,
        topics=settings.kafka_topics.split(","),
    )

    service.run()


if __name__ == "__main__":
    main()
