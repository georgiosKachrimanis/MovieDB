from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# In order to avoid circular imports!
class MovieBasicDisplay(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class UserReviewModel(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


# ================================ Review Schemas ===================


class ReviewBase(BaseModel):
    review_content: str
    user_rating: float
    user_id: Optional[int]


class Review(ReviewBase):
    id: int
    review_content: str
    user_rating: float
    created_at: datetime


class CreateReview(BaseModel):
    review_content: str
    user_rating: float
    movie_id: int


class ReviewDisplayOne(BaseModel):
    id: int
    review_content: str
    movie: MovieBasicDisplay
    user: UserReviewModel
    user_rating: float
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewUpdate(BaseModel):
    movie_id: Optional[int] = None
    review_content: Optional[str] = None
    user_rating: Optional[float] = None
