from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from schemas.reviews_schemas import Review


# In order to avoid circular imports!
class MovieBasicDisplay(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


# ============================ User Schemas =======================
class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserTypeUpdate(BaseModel):
    user_type: str


class UserTypeDisplay(BaseModel):
    user_type: str

    class Config:
        from_attributes = True


class UserDisplay(BaseModel):
    id: int
    username: str
    email: EmailStr
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
