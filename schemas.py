from pydantic import BaseModel, EmailStr
from typing import Optional, List 
from datetime import datetime
from typing import Optional, List

# User inside ReviewDisplay
class User(BaseModel):
    id: int
    username: str

# Review inside UserDisplay
class Review(BaseModel):
    id: int
    review_content: str
    movie_rate: float
    created_at: datetime


# Movie inside ReviewDisplay
class Movie(BaseModel):
    id: int
    title: str

class CategoryBase(BaseModel):
    category_name: str

class CategoryDisplay(BaseModel):
    id: int
    category_name: str
    class Config:
        from_attributes = True   


class UserBase(BaseModel):
        username: str
        email: EmailStr
        user_type: str
        password: str
        created_at: Optional[datetime] = None
    
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    user_type: Optional[str] = None
    password: Optional[str]  = None


class UserDisplayOne(BaseModel):
    id: int
    username: str
    email: EmailStr
    user_type: str
    created_at: Optional[datetime] = None
    reviews: List[Review] = []
    class Config:
        from_attributes = True

class UserDisplayAll(BaseModel):
    id: int
    username: str
    email: EmailStr
    user_type: str
    created_at: Optional[datetime] = None
    review_count: int
    class Config:
        from_attributes = True        

class ReviewDisplay(BaseModel):
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

class MovieBase(BaseModel):
    title: str
    released_date: datetime
    categories: str
    plot: str
    poster_url: str
    imdb_rate: float


class MovieDisplayOne(BaseModel):
    id: int
    title: str
    released_date: datetime
    categories: List[CategoryBase] = []
    plot: str
    poster_url: str
    average_movie_rate : float
    imdb_rate: float
    reviews: List[Review] = []
    class Config:
        from_attributes = True


class MovieDisplayAll(BaseModel):
    id: int
    title: str
    released_date: datetime
    categories: List[str]
    plot: str
    poster_url: str
    average_movie_rate : float
    imdb_rate: float
    review_count: int
    class Config:
        from_attributes = True        

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    released_date: Optional[datetime] = None
    categories: List[str] = None
    actors: Optional[List[int]] = None
    plot: Optional[str] = None
    poster_url: Optional[str] = None
    imdb_rate: float


 