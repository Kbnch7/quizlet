from pydantic import BaseModel

from typing import List, Any, Dict

class CustomError(BaseModel):
    code: str
    statusCode: str
