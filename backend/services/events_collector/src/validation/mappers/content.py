from event_contracts.content.v1 import (
    CardCreated as CardCreatedV1,
)
from event_contracts.content.v1 import (
    DeckCreated as DeckCreatedV1,
)


def map_deck_created(produced_at: str, event_id: int, event: DeckCreatedV1) -> tuple:
    return (
        event.created_at,
        produced_at,
        event_id,
        event.deck_id,
        event.author_id,
    )


def map_card_created(produced_at: str, event_id: int, event: CardCreatedV1) -> tuple:
    return (
        event.created_at,
        produced_at,
        event_id,
        event.card_id,
        event.deck_id,
    )
