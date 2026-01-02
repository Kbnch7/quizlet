from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserCreate(BaseModel):
    name: str
    surname: str
    password: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name", "surname", "password")
    @classmethod
    def check_not_empty_name(cls, value: str):
        if not value:
            raise ValueError("Field can not be empty.")
        return value.strip().capitalize()

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if " " in value:
            raise ValueError("Field can not contain spaces.")
        return value.strip()


class UserBaseInfo(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    is_manager: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("name", "surname")
    @classmethod
    def check_not_empty_name(cls, value: str):
        if not value:
            raise ValueError("Field can not be empty.")
        return value.strip().capitalize()


class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None

    @field_validator("name", "surname")
    @classmethod
    def check_not_empty_name(cls, value: Optional[str]):
        if value is None:
            return value
        if not value.strip():
            raise ValueError("Field cannot be empty.")
        return value.strip().capitalize()

    @field_validator("password")
    @classmethod
    def check_password(cls, value: Optional[str]):
        if value is None:
            return value
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if " " in value:
            raise ValueError("Password cannot contain spaces.")
        return value.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str
