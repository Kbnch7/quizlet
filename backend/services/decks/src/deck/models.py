from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.card.models import SCardResponse
from src.category.models import SCategoryResponse
from src.tag.models import STagResponse


class SDeckCreate(BaseModel):
    title: str
    owner_id: Optional[int] = None
    description: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class SDeckUpdate(BaseModel):
    title: Optional[str] = None
    owner_id: Optional[int] = None
    description: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class SDeckResponse(BaseModel):
    id: int
    owner_id: int
    title: str
    description: Optional[str] = None
    categories: Optional[List[SCategoryResponse]] = None
    tags: Optional[List[STagResponse]] = None

    model_config = ConfigDict(
        from_attributes=True
    )


class SDeckDetailedResponse(SDeckResponse):
    cards: List[SCardResponse] = []
