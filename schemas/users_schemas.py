from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


# User inside ReviewDisplay
class User(BaseModel):
    id: int
    username: str


# Review inside UserDisplay
class Review(BaseModel):
    id: int
    review_content: str
    movie_rate: float
    created_at: datetime


# Movie inside ReviewDisplay
class Movie(BaseModel):
    id: int
    title: str

class UserType(str, Enum):
    user = "user"
    admin = "admin"

    class Config:
        error_messages = {
            "enum": "User type must be 'user' or 'admin'"
        }

class UserBase(BaseModel):
    username: str
    email: EmailStr
    user_type: UserType   # Default value is "user"
    password: str
    created_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    user_type: Optional[str] = None
    password: Optional[str] = None


class UserDisplayOne(BaseModel):
    id: int
    username: str
    email: EmailStr
    user_type: str
    created_at: Optional[datetime] = None
    reviews: List[Review] = []

    class Config:
        from_attributes = True


class UserDisplayAll(BaseModel):
    id: int
    username: str
    email: EmailStr
    user_type: str
    created_at: Optional[datetime] = None
    review_count: int

    class Config:
        from_attributes = True


class UserTypeUpdate(BaseModel):
    user_type: str


class UserTypeDisplay(BaseModel):
    user_type: str

    class Config:
        from_attributes = True

class UserTypeUpdate(BaseModel):
    user_type: str