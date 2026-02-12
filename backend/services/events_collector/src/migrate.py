import os
from pathlib import Path

from clickhouse_driver import Client

MIGRATIONS_DIR = Path(__file__).parent / "migrations"

client = Client(
    host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
    database=os.getenv("CLICKHOUSE_DB", "analytics"),
    user=os.getenv("CLICKHOUSE_USER_WRITER"),
    password=os.getenv("CLICKHOUSE_PASSWORD_WRITER"),
)

client.execute("""
CREATE TABLE IF NOT EXISTS schema_migrations (
    version UInt32,
    name String,
    applied_at DateTime DEFAULT now()
) ENGINE = MergeTree
ORDER BY version
""")

applied = {row[0] for row in client.execute("SELECT version FROM schema_migrations")}

for file in sorted(MIGRATIONS_DIR.glob("*.sql")):
    version = int(file.name.split("_")[0])
    if version in applied:
        continue

    print(f"Applying migration {file.name}")
    # sql = file.read_text()
    #
    # client.execute(sql)

    with open(file, "r") as f:
        sql_statements = f.read().split(";")

    for stmt in sql_statements:
        stmt = stmt.strip()
        if stmt:
            client.execute(stmt)
    client.execute(
        "INSERT INTO schema_migrations (version, name) VALUES",
        [(version, file.name)],
    )
