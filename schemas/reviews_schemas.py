from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# User inside Reviews (Same as User in user_schemas)
class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


# Movie inside ReviewDisplay
class Movie(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


# Review Schemas
class ReviewBase(BaseModel):
    review_content: str
    user_rate: float
    user_id: Optional[int]


class CreateReview(BaseModel):
    review_content: str
    user_rate: float
    # Sezgin uses movie_rate here!


class ReviewDisplay(BaseModel):
    id: int
    review_content: str
    user_rate: float
    # Sezgin uses movie_rate here!
    created_at: datetime
    user: User  # From user_schemas

    class Config:
        from_attributes = True


class ReviewUpdate(BaseModel):
    review_content: Optional[str] = None
    # Sezgin uses movie_rate here!
    user_rate: Optional[float] = None


class Review(BaseModel):
    id: int
    review_content: str
    # Sezgin uses movie_rate here!
    user_rate: float
    created_at: datetime
