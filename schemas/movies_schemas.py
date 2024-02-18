from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, validator
from schemas.users_schemas import Review
from schemas.categories_schemas import Category
from schemas.actors_schemas import Actor
from schemas.directors_schemas import Director


# =========================== Movies Schemas ==================================
class MovieBase(BaseModel):
    title: str
    director_id: Optional[int] = None
    actors: Optional[List[int]] = []
    plot: str
    categories: List[int] = []
    release_year: Optional[int]
    poster_url: Optional[str]
    imdb_id: Optional[str]

    # @validator("release_year")
    # def check_valid_year(cls, input_year):
    #     if input < 1900 or input_year > 2030:
    #         raise ValueError("Release year must be between 1900 and 2030.")
    #     return input_year


class MovieDisplayOne(BaseModel):
    id: int
    title: str
    director: Optional[Director]
    actors: Optional[List[Actor]]
    plot: str
    release_year: Optional[int]
    imdb_id: Optional[str]
    categories: List[Category]
    poster_url: Optional[str] = None
    reviews_count: Optional[int] = None
    average_movie_rate: Optional[float] = None
    reviews: List[Review] = []

    class Config:
        from_attributes = True


# to be used with the patch(update) function
class MoviePatchUpdate(BaseModel):
    title: Optional[str] = None
    release_year: Optional[int] = None
    categories: Optional[List[int]] = None
    plot: Optional[str] = None
    poster_url: Optional[str] = None
    imdb_id: Optional[str] = None
    director_id: Optional[int] = None
    actors: Optional[List[int]] = None


# To be used with the put(update) function
class MovieUpdate(BaseModel):
    title: str
    release_year: Optional[int]
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
