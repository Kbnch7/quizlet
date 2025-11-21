from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SCardResultIn(BaseModel):
    card_id: int
    correct: bool
    answer_time_seconds: int
    user_answer: Optional[str] = None


class STestResultCreate(BaseModel):
    user_id: int
    total_time_seconds: int
    correct_rate: float
    card_results: List[SCardResultIn]


class SCardResultOut(BaseModel):
    id: int
    card_id: int
    correct: bool
    answer_time_seconds: int
    user_answer: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class STestResultResponse(BaseModel):
    id: int
    deck_id: int
    user_id: int
    total_time_seconds: int
    correct_rate: float
    card_results: List[SCardResultOut]

    model_config = ConfigDict(from_attributes=True)
