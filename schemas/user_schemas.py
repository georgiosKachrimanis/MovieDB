from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: str
    email: EmailStr
    password: str
    user_type: str


class UserDisplay(BaseModel):
    username: str
    email: EmailStr
    user_type: str

    class Config:
        from_attributes = True


# User inside Reviews
class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
