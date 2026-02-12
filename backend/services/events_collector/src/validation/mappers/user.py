from event_contracts.user.v1 import UserRegistered as UserRegisteredV1


def map_user_registered(
    produced_at: str, event_id: int, event: UserRegisteredV1
) -> tuple:
    return (
        event.registered_at,
        produced_at,
        event_id,
        event.user_id,
        event.email,
    )
