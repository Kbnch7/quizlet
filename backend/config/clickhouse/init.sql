CREATE DATABASE IF NOT EXISTS analytics;

-- роли
CREATE ROLE IF NOT EXISTS analytics_writer_role;
CREATE ROLE IF NOT EXISTS analytics_reader_role;

-- права
GRANT INSERT ON analytics.* TO analytics_writer_role;
GRANT CREATE TABLE ON analytics.* TO analytics_writer_role;
GRANT SELECT ON analytics.* TO analytics_writer_role;
GRANT SELECT ON analytics.* TO analytics_reader_role;

-- writer
CREATE USER IF NOT EXISTS ${CLICKHOUSE_USER_WRITER}
IDENTIFIED WITH sha256_password BY '${CLICKHOUSE_PASSWORD_WRITER}';

GRANT analytics_writer_role TO ${CLICKHOUSE_USER_WRITER};

-- reader
CREATE USER IF NOT EXISTS ${CLICKHOUSE_USER_READER}
IDENTIFIED WITH sha256_password BY '${CLICKHOUSE_PASSWORD_READER}';

GRANT analytics_reader_role TO ${CLICKHOUSE_USER_READER};
