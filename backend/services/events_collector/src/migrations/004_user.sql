CREATE TABLE IF NOT EXISTS analytics.user_registered
(
    event_time     DateTime64(3),
    produced_at    DateTime64(3),

    event_id       UUID,
    user_id        UInt64,
    email          String
)
ENGINE = MergeTree
ORDER BY (event_time, user_id);


