from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str


# User inside Reviews
class UserReviewModel(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Review(BaseModel):
    id: int
    review_content: str
    user_movie_rate: float
    created_at: datetime


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


# Review Schemas
class ReviewBase(BaseModel):
    review_content: str
    user_movie_rate: float
    user_id: Optional[int]


class CreateReview(BaseModel):
    review_content: str
    user_movie_rate: float
    movie_id: int


class ReviewDisplay(BaseModel):
    id: int
    review_content: str
    user_movie_rate: float
    created_at: datetime
    user: UserReviewModel  # From user_schemas

    class Config:
        from_attributes = True


class ReviewUpdate(BaseModel):
    review_content: Optional[str] = None
    user_movie_rate: Optional[float] = None
