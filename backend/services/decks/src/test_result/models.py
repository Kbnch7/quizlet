from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class STestResultCardIn(BaseModel):
    card_id: int
    correct: bool
    answer_time_ms: int
    user_answer: Optional[str] = None


class STestResultCreate(BaseModel):
    user_id: int
    total_time_ms: int
    score: float
    card_results: List[STestResultCardIn]


class STestResultCardOut(BaseModel):
    id: int
    card_id: int
    correct: bool
    answer_time_ms: int
    user_answer: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class STestResultResponse(BaseModel):
    id: int
    deck_id: int
    user_id: int
    total_time_ms: int
    score: float
    card_results: List[STestResultCardOut]

    model_config = ConfigDict(from_attributes=True)


