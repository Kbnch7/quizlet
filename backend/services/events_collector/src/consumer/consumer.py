import json
import logging
import signal

from confluent_kafka import Consumer, KafkaError, TopicPartition
from event_contracts.base import EventEnvelope
from pydantic import ValidationError
from src.storage.clickhouse import BatchBuffer
from src.validation.registry import EVENT_REGISTRY

logger = logging.getLogger(__name__)


def on_assign(consumer, partitions):
    logger.info("Assigned partitions: %s", partitions)


def on_revoke(consumer, partitions):
    logger.info("Revoked partitions: %s", partitions)


def parse_envelope_and_payload(
    raw_event,
    payload_schema,
):
    try:
        envelope = EventEnvelope.model_validate(raw_event)
    except ValidationError as e:
        logger.error(
            "Invalid event envelope: %s\nRaw event: %s",
            e,
            raw_event,
        )
        raise

    try:
        payload = payload_schema.model_validate(envelope.payload)
    except ValidationError as e:
        logger.error(
            "Invalid payload for event %s v%s: %s\nPayload: %s",
            envelope.event_type,
            envelope.event_version,
            e,
            envelope.payload,
        )
        raise

    return envelope, payload


class KafkaEventConsumer:
    def __init__(
        self,
        consumer: Consumer,
        clickhouse,
        topics: list[str],
    ):
        self.consumer = consumer
        self.clickhouse = clickhouse
        self.topics = topics
        self._running = True

        # (topic, partition) -> last_processed_offset
        self._pending_offsets: dict[tuple[str, int], int] = {}

        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

    def _shutdown(self, *_):
        logger.info("Shutdown signal received")
        self._running = False

    def run(self):
        logger.info(f"Subscribing to topics: {self.topics}")
        self.consumer.subscribe(self.topics, on_assign=on_assign, on_revoke=on_revoke)

        logger.info("Initializing buffers")
        self.buffers: dict[str, BatchBuffer] = {}

        for descriptor in EVENT_REGISTRY.values():
            if descriptor.table not in self.buffers:
                self.buffers[descriptor.table] = BatchBuffer(
                    client=self.clickhouse,
                    table=descriptor.table,
                )
        while self._running:
            msg = self.consumer.poll(1.0)
            if msg is None:
                self._flush_due_buffers()
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error(f"Kafka error: {msg.error()}")
                continue

            try:
                self._process_message(msg)
            except Exception:
                logger.exception("Failed to process message")
                continue

        logger.info("Final flush before shutdown")
        self._flush_all_buffers()
        self._commit_offsets()

        logger.info("Closing consumer")
        self.consumer.close()

    def _process_message(self, msg):
        event = json.loads(msg.value())

        event_type = event["event_type"]
        event_version = event["event_version"]

        descriptor = EVENT_REGISTRY.get((event_type, event_version))
        if not descriptor:
            logger.warning(
                "Unknown event type: %s v%s",
                event_type,
                event_version,
            )
            return

        envelope: EventEnvelope
        envelope, payload = parse_envelope_and_payload(event, descriptor.schema)

        row = descriptor.mapper(envelope.occured_at, envelope.event_id, payload)

        buffer = self.buffers[descriptor.table]
        buffer.add(row)

        tp = (msg.topic(), msg.partition())
        self._pending_offsets[tp] = max(
            self._pending_offsets.get(tp, -1),
            msg.offset(),
        )

        if buffer.should_flush():
            self._flush_buffer(buffer)
            self._commit_offsets()

    def _flush_due_buffers(self):
        flushed = False
        for buffer in self.buffers.values():
            if buffer.should_flush():
                self._flush_buffer(buffer)
                flushed = True

        if flushed:
            self._commit_offsets()

    def _flush_buffer(self, buffer: "BatchBuffer"):
        logger.info(f"Flushing buffer {buffer.table} ({buffer.size} rows)")
        buffer.flush()

    def _flush_all_buffers(self):
        for buffer in self.buffers.values():
            if buffer.size > 0:
                buffer.flush()

    def _commit_offsets(self):
        if not self._pending_offsets:
            return

        tps = []
        for (topic, partition), offset in self._pending_offsets.items():
            tps.append(TopicPartition(topic, partition, offset + 1))

        logger.debug("Committing offsets: %s", tps)

        self.consumer.commit(offsets=tps, asynchronous=False)
        self._pending_offsets.clear()
