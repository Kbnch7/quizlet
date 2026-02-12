CREATE TABLE IF NOT EXISTS analytics.deck_created
(
    event_time   DateTime64(3),
    produced_at  DateTime64(3),

    event_id     UUID,
    deck_id      UInt64,
    author_id    UInt64
)
ENGINE = MergeTree
ORDER BY event_time;


CREATE TABLE IF NOT EXISTS analytics.card_created
(
    event_time   DateTime64(3),
    produced_at  DateTime64(3),

    event_id     UUID,
    card_id      UInt64,
    deck_id      UInt64
)
ENGINE = MergeTree
ORDER BY (event_time, deck_id);

