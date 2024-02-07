from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from typing import Optional, List


# User inside ReviewDisplay
class User(BaseModel):
    id: int
    username: str


# Movie inside ReviewDisplay
class Movie(BaseModel):
    id: int
    title: str

class ReviewDisplayAll(BaseModel):
    id: int
    review_content: str
    created_at: datetime
    movie_rate: Optional[float] = None


class ReviewDisplayOne(BaseModel):
    id: int
    review_content: str
    created_at: datetime
    movie: Movie
    movie_rate: Optional[float] = None
    user: User
    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    review_content: str
    user_id: int
    movie_id: int
    movie_rate: Optional[float] = None


class ReviewUpdate(BaseModel):
    review_content: Optional[str] = None
    movie_rate: Optional[float] = None


class UserBase(BaseModel):
        username: str
        email: EmailStr
        user_type: str
        password: str
        created_at: Optional[datetime] = None
    