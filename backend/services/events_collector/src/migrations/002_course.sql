CREATE TABLE IF NOT EXISTS analytics.course_created
(
    event_time   DateTime64(3),
    produced_at  DateTime64(3),

    event_id     UUID,
    course_id    UInt64,
    author_id    UInt64
)
ENGINE = MergeTree
ORDER BY event_time;


CREATE TABLE IF NOT EXISTS analytics.course_enrolled
(
    event_time   DateTime64(3),
    produced_at  DateTime64(3),

    event_id     UUID,
    course_id    UInt64,
    user_id      UInt64
)
ENGINE = MergeTree
ORDER BY (event_time, course_id);


CREATE TABLE IF NOT EXISTS analytics.course_progress_updated
(
    event_time   DateTime64(3),
    produced_at  DateTime64(3),

    event_id     UUID,
    course_id    UInt64,
    user_id      UInt64,
    deck_id      UInt64,
    progress_percent Float32,
)
ENGINE = MergeTree
ORDER BY (event_time, course_id);



