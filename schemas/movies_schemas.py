from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from schemas.users_reviews_schemas import Review


class Image(BaseModel):
    url: str
    alias: str


class CategoryID(BaseModel):
    id: int


# expenses
class Category(BaseModel):
    id: int
    name: str


# Class to be used for the creation and management of Movie Category table
class MovieCategoryType(Enum):
    action = (1, "Action")
    animation = (2, "Animation")
    documentary = (3, "Documentary")
    comedy = (4, "Comedy")
    drama = (5, "Drama")
    fantasy = (6, "Fantasy")
    musical = (7, "Musical")
    romance = (8, "Romance")
    scifi = (9, "Science Fiction")
    thriller = (10, "Thriller")
    western = (11, "Western")

    def __init__(self, num, label):
        self.num = num
        self.label = label


class MovieBase(BaseModel):
    title: str
    released_date: Optional[datetime]
    categories: List[int] = []
    plot: str
    poster_url: Optional[str]
    imdb_rate: Optional[float]

class MovieTestDisplay(BaseModel):
    title: str
    released_date: Optional[datetime]
    plot: str
    poster_url: Optional[str]
    imdb_rate: Optional[float]
    
    class Config:
        from_attributes = True

class MovieDisplayOne(BaseModel):
    id: int
    title: str
    released_date: datetime
    categories: List[Category]
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
