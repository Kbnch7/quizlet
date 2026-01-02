#!/bin/bash
set -e

echo "Initializing ClickHouse users..."

envsubst </init.sql | clickhouse-client --multiquery

echo "ClickHouse users initialized"
