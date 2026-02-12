from pydantic import BaseModel

class TokenPair(BaseModel):
    access: str
    refresh: str

class RefreshToken(BaseModel):
    refresh: str

class AccessToken(BaseModel):
    access: str
