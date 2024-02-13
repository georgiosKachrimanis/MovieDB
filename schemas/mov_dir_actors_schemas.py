from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from schemas.users_reviews_schemas import Review


class Image(BaseModel):
    url: str
    alias: str


# ============================== Categories Schemas==========================
class CategoryName(BaseModel):
    category_name: str


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


# =========================== Directors Schemas ===============================
class Director(BaseModel):
    director_name: str


class DirectorUpdate(Director):
    movies: List[int] = []


class DirectorPatchUpdate(BaseModel):
    None


class MovieShortDisplay(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class DirectorDisplay(Director):
    id: int
    movies: List[MovieShortDisplay] = []

    class Config:
        from_attributes = True


# =================================== Actors ==================================


# Movie inside ActorDisplay
class Actor(BaseModel):
    actor_name: str


class ActorFullUpdate(Actor):
    movies: List[int] = []


class ActorPatch(BaseModel):
    actor_name: Optional[str] = None
    movies: Optional[List[int]] = None


class ActorDisplay(Actor):
    id: int
    movies: List[MovieShortDisplay] = []

    class Config:
        from_attributes = True


# =========================== Movies Schemas ==================================
class MovieBase(BaseModel):
    title: str
    released_date: Optional[datetime]
    categories: List[int] = []
    director_id: Optional[int] = None
    actors: Optional[List[int]] = []
    plot: str
    poster_url: Optional[str]
    imdb_id: Optional[str]


class MovieDisplayAll(BaseModel):
    id: int
    title: str
    director: Optional[Director]
    actors: Optional[List[Actor]]
    plot: str
    released_date: datetime
    imdb_id: Optional[str]
    categories: List[Category]
    poster_url: Optional[str] = None
    reviews_count: Optional[int] = None
    average_movie_rate: Optional[float] = None

    class Config:
        from_attributes = True


class MovieDisplayOne(MovieDisplayAll):
    reviews: List[Review] = []

    class Config:
        from_attributes = True


# to be used with the patch(update) function
class MoviePatchUpdate(BaseModel):
    title: Optional[str] = None
    released_date: Optional[datetime] = None
    categories: Optional[List[int]] = None
    plot: Optional[str] = None
    poster_url: Optional[str] = None
    imdb_id: Optional[str] = None
    director_id: Optional[int] = None
    actors: Optional[List[int]] = None


# To be used with the put(update) function
class MovieUpdate(BaseModel):
    title: str
    released_date: datetime
    categories: List[int]
    plot: str
    poster_url: str
    imdb_id: str
    director_id: Optional[int]
    actors: Optional[List[int]]


class MovieExtraData(BaseModel):
    imdbRating: float
    imdbVotes: int
    Language: str
    Country: str


class MovieStats(BaseModel):
    id: int
    title: str
    requests_count: Optional[int]

    class Config:
        from_attributes = True


class MovieSingleRequest(BaseModel):
    movie_id: int
    user_id: int
    request_time: datetime


class MovieTotalRequests(BaseModel):
    movie_id: int
    total_requests: Optional[int] = None
    last_request: Optional[datetime] = None
