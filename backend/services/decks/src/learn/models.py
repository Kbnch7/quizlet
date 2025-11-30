from typing import Optional, List
from pydantic import BaseModel


class SLearnSession(BaseModel):
    id: int
    deck_id: int
    status: str
    total_cards: int
    learned_cards: int


class SLearnSessionResponse(SLearnSession):
    started_at: str
    ended_at: Optional[str] = None


class SLearnSessionCreateResponse(BaseModel):
    session: SLearnSessionResponse
    progress: float


class SLearnBatchResponse(BaseModel):
    session_id: int
    card_id: Optional[int] = None
    learned_cards: int
    total_cards: int
    progress: float


class SLearnAnswer(BaseModel):
    correct: bool
    answer_time_seconds: int


class SLearnProgressResponse(BaseModel):
    session_id: int
    learned_cards: int
    total_cards: int
    progress: float
    is_completed: bool
