from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Review inside MovieDisplayOne
class Review(BaseModel):
    id: int
    review_content: str
    movie_rate: float
    created_at: datetime

# Actors inside MovieDisplayOne
class Actor(BaseModel):
    actor_name: str

# Director inside MovieDisplay
class Director(BaseModel):
    director_name: str


# CategoryBase inside MovieDisplayOne
class CategoryBase(BaseModel):
    category_name: str


class MovieBase(BaseModel):
    title: str
    released_date: datetime
    categories: List[int] = []
    director_id: Optional[int] = None
    actors: Optional[List[int]] = []
    plot: str
    poster_url: Optional[str] = None
    imdb_rate: float


class MovieDisplayOne(BaseModel):
    id: int
    title: str
    released_date: datetime
    categories: List[CategoryBase]
    plot: str
    poster_url: str
    average_movie_rate: Optional[float] = None
    imdb_rate: float
    reviews: List[Review] = []
    director: Optional[Director]
    actors: Optional[List[Actor]]
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
    director_name: str
    class Config:
        from_attributes = True


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    released_date: Optional[datetime] = None
    categories: List[int]
    plot: Optional[str] = None
    poster_url: Optional[str] = None
    imdb_rate: float
    director_id: int
    actors: List[int]
