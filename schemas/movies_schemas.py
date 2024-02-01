from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class Image(BaseModel):
    url: str
    alias: str


class CategoryID(BaseModel):
    id: int


class Category(BaseModel):
    id: int
    name: str


class Review(BaseModel):
    id: int
    review_content: str
    # Sezgin uses movie_rate here!
    user_rate: float
    created_at: datetime


class MovieCategory(str, Enum):
    action = "Action"
    animation = "Animation"
    documentary = "Documentary"
    comedy = "Comedy"
    drama = "Drama"
    fantasy = "Fantasy"
    musical = "Musical"
    romance = "Romance"
    scifi = "Science Fiction"
    thriller = "Thriller"
    western = "Western"


class MovieBase(BaseModel):
    title: str
    released_date: Optional[datetime] = None
    categories: Optional[List[CategoryID]] = None
    plot: str
    poster_url: Optional[str] = None
    imdb_rate: Optional[float] = None


class MovieDisplayOne(BaseModel):
    id: int
    title: str
    released_date: datetime
    categories: List[Category] = []
    plot: str
    poster_url: str
    average_movie_rate: Optional[float] = None
    imdb_rate: float
    reviews: List[Review] = []

    class Config:
        from_attributes = True


class MovieDisplayAll(BaseModel):
    id: int
    title: str
    released_date: datetime
    plot: str
    poster_url: str
    average_movie_rate: Optional[float] = None
    imdb_rate: float
    review_count: int

    class Config:
        from_attributes = True


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    released_date: Optional[datetime] = None
    categories: List[CategoryID]
    plot: Optional[str] = None
    poster_url: Optional[str] = None
    imdb_rate: Optional[float] = None
