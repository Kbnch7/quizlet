def handle_learning_session_started(env, payload, ch):
    ch.insert(
        "learning_session_started",
        {
            "event_time": env.occurred_at,
            "produced_at": env.produced_at,
            "user_id": payload.user_id,
            "deck_id": payload.deck_id,
            "session_id": payload.session_id,
        },
    )
