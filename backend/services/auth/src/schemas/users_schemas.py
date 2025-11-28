from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    name: str
    surname: str
    password: str
    email: EmailStr

class UserLogin(BaseModel):
    email: str
    password: str

class UserBaseInfo(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr