from confluent_kafka import Consumer

from config.settings import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_GROUP_ID,
)


def create_consumer() -> Consumer:
    conf = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": KAFKA_GROUP_ID,
        "enable.auto.commit": False,
        "auto.offset.reset": "earliest",
        "session.timeout.ms": 10000,
        "max.poll.interval.ms": 300000,
        "client.id": "events-collector",
    }

    return Consumer(conf)
