CREATE TABLE IF NOT EXISTS analytics.learning_session_started
(
    event_time     DateTime64(3),
    produced_at    DateTime64(3),

    event_id       UUID,
    user_id        UInt64,
    deck_id        UInt64,
    session_id     UInt64
)
ENGINE = MergeTree
ORDER BY (event_time, user_id);

CREATE TABLE IF NOT EXISTS analytics.learning_session_finished
(
    event_time      DateTime64(3),
    produced_at     DateTime64(3),

    event_id        UUID,
    user_id         UInt64,
    deck_id         UInt64,
    session_id      UInt64,
    learned_cards   UInt32,
    total_cards     UInt32,
    duration_sec    UInt32,
    completed       Boolean
)
ENGINE = MergeTree
ORDER BY (event_time, user_id);

