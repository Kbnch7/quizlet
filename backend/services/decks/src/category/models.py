from pydantic import BaseModel, ConfigDict
from typing import Optional


class SCategoryResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)


class SCategoryCreate(BaseModel):
    name: str
    slug: str


class SCategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
