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
    imdb_id: Optional[str] = None


class MovieDisplayOne(BaseModel):
    id: int
    title: Optional[str]
    released_date: Optional[datetime]
    categories: List[CategoryBase]
    plot: Optional[str]
    poster_url: Optional[str]
    average_movie_rate: Optional[float] = None
    imdb_id: Optional[str] = None
    number_of_request: Optional[int] = None  
    reviews: List[Review] = []
    director: Optional[Director]
    actors: Optional[List[Actor]]
    class Config:
        from_attributes = True


class MovieDisplayAll(BaseModel):
    id: int
    title: Optional[str]
    released_date: datetime
    plot: Optional[str]
    poster_url: Optional[str]
    average_movie_rate: Optional[float] = None
    number_of_request: Optional[int] = None  
    imdb_id: Optional[str] = None
    review_count: Optional[int]
    director_name: Optional[str]
    class Config:
        from_attributes = True


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    released_date: Optional[datetime] = None
    categories: List[int]
    plot: Optional[str] = None
    poster_url: Optional[str] = None
    imdb_id: Optional[str] = None
    director_id: int
    actors: List[int]

class MovieExtraData(BaseModel):
    imdbRating: float
    imdbVotes: int
    Language: str
    Country: str

class MoviePatchUpdate(BaseModel):
    title: Optional[str] = None
    released_date: Optional[datetime] = None
    categories: Optional[List[int]] = None
    plot: Optional[str] = None
    imdb_id: Optional[str] = None
    director_id: Optional[int] = None
    actors: Optional[List[int]] = None 
    number_of_request: Optional[int] = None   

class RequestBase():
    movie_id : int
    request_time : datetime

class MovieRequestCount(BaseModel):
    movie_id: int
    movie_title: str
    request_count: int
    class Config:
        from_attributes = True    