from typing import Optional

from pydantic import BaseModel


class CustomError(BaseModel):
    code: str
    statusCode: str
    detail: Optional[dict] = None
