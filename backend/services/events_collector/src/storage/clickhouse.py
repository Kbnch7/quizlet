import time
from typing import Any, List

from clickhouse_driver import Client

BATCH_SIZE = 500
FLUSH_INTERVAL = 3.0


class ClickHouseWriter:
    def __init__(self, client: Client):
        self.client = client

    def insert(self, table: str, row: dict):
        self.client.execute(
            f"INSERT INTO {table} VALUES",
            [row],
        )


class BatchBuffer:
    def __init__(self, client, table: str):
        self.client = client
        self.table = table
        self.rows: List[Any] = []
        self.last_flush = time.monotonic()
        self.size = 0

    def add(self, row: tuple):
        self.rows.append(row)
        self.size += 1

    def should_flush(self) -> bool:
        if len(self.rows) >= BATCH_SIZE:
            return True
        if time.monotonic() - self.last_flush >= FLUSH_INTERVAL:
            return True
        return False

    def flush(self):
        if not self.rows:
            return

        self.client.execute(
            f"INSERT INTO {self.table} VALUES",
            self.rows,
        )
        self.rows.clear()
        self.last_flush = time.monotonic()
        self.size = 0
