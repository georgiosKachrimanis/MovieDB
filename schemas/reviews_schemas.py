from pydantic import BaseModel
from schemas.users_schemas import User
from typing import Optional
from datetime import datetime


# Review Schemas
# Review inside UserDisplay
class ReviewBase(BaseModel):
    review_content: str
    user_rate: float
    user_id: Optional[int]


class CreateReview(BaseModel):
    review_content: str
    user_rate: float


class ReviewDisplay(BaseModel):
    id: int
    review_content: str
    user_rate: float
    created_at: datetime
    user: User  # From user_schemas

    class Config:
        from_attributes = True


class ReviewUpdate(BaseModel):
    user_id: User
    review_content: Optional[str] = None
    user_rate: Optional[float] = None


class Review(BaseModel):
    id: int
    review_content: str
    user_rate: float
    created_at: datetime
