from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from schemas.users_reviews_schemas import Review


class Image(BaseModel):
    url: str
    alias: str


class CategoryName(BaseModel):
    category_name: str


# expenses
class Category(BaseModel):
    id: int
    category_name: str


# Class to be used for the creation and management of Movie Category table
class MovieCategoryType(Enum):
    action = (1, "Action")
    adventure = (2, "Adventure")
    animation = (3, "Animation")
    biography = (4, "Biography")
    comedy = (5, "Comedy")
    crime = (6, "Crime")
    documentary = (7, "Documentary")
    drama = (8, "Drama")
    family = (9, "Family")
    fantasy = (10, "Fantasy")
    film_noir = (11, "Film Noir")
    history = (12, "History")
    horror = (13, "Horror")
    musical = (14, "Musical")
    mystery = (15, "Mystery")
    romance = (16, "Romance")
    sci_fi = (17, "Science Fiction")
    sport = (18, "Sport")
    superhero = (19, "Superhero")
    thriller = (20, "Thriller")
    war = (21, "War")
    western = (22, "Western")

    def __init__(self, num, label):
        self.num = num
        self.label = label


class Director(BaseModel):
    director_name: str


class MovieBase(BaseModel):
    title: str
    released_date: Optional[datetime]
    categories: List[int] = []
    directors_id: Optional[int] = None
    plot: str
    poster_url: Optional[str]
    imdb_rate: Optional[float]


class MovieDirectorDisplay(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class DirectorDisplay(BaseModel):
    id: int
    director_name: str
    movies: List[MovieDirectorDisplay] = []

    class Config:
        from_attributes = True


class MovieDisplayAll(BaseModel):
    id: int
    title: str
    released_date: datetime
    categories: List[Category]
    plot: str
    poster_url: Optional[str] = None
    average_movie_rate: Optional[float] = None
    imdb_rate: Optional[float]
    reviews_count: Optional[int] = None
    director: Optional[Director]

    class Config:
        from_attributes = True


class MovieDisplayOne(BaseModel):
    id: int
    title: str
    released_date: datetime
    categories: List[Category]
    plot: str
    poster_url: Optional[str] = None
    average_movie_rate: Optional[float] = None
    imdb_rate: Optional[float]
    reviews: List[Review] = []
    director: Optional[Director]

    class Config:
        from_attributes = True


# to be used with the patch(update) function
class MoviePatchUpdate(BaseModel):
    title: Optional[str] = None
    released_date: Optional[datetime] = None
    categories: Optional[List[int]] = None
    plot: Optional[str] = None
    poster_url: Optional[str] = None
    imdb_rate: Optional[float] = None


# To be used with the put(update) function
class MovieUpdate(BaseModel):
    title: str
    released_date: datetime
    categories: List[int]
    plot: str
    poster_url: str
    imdb_rate: float
    directors_id: Optional[int] = None
