from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


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


class MovieReviewModel(BaseModel):
    id: int
    title: str


class Review(BaseModel):
    id: int
    review_content: str
    user_rating: float
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
    user_rating: float
    user_id: Optional[int]


class CreateReview(BaseModel):
    review_content: str
    user_rating: float
    movie_id: int


class ReviewDisplayOne(BaseModel):
    id: int
    created_at: datetime
    review_content: str
    movie: MovieReviewModel
    user_rating: float
    created_at: datetime
    user: UserReviewModel

    class Config:
        from_attributes = True


class ReviewDisplayAll(BaseModel):
    id: int
    created_at: datetime
    review_content: str
    user_rating: float
    created_at: datetime
    user: UserReviewModel

    class Config:
        from_attributes = True


class ReviewUpdate(BaseModel):
    review_content: Optional[str] = None
    user_rating: Optional[float] = None
