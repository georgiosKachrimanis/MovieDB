from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from schemas.users_schemas import Review
from schemas import categories_schemas
from schemas.actors_schemas import Actor


# =========================== Directors Schemas ===============================
class Director(BaseModel):
    director_name: str


class DirectorUpdate(Director):
    movies: List[int] = []


class MovieBasicDisplay(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class DirectorDisplay(Director):
    id: int
    movies: List[MovieBasicDisplay] = []

    class Config:
        from_attributes = True


# =================================== Actors ==================================


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
    categories: List[categories_schemas.Category]
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


# Used in Actors and Directors
class MovieBasicDisplay(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True
