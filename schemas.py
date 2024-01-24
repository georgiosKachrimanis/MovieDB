from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel


class Image(BaseModel):
    url: str
    alias: str


class UserBase(BaseModel):
    username: str
    email: str
    password: str


class UserDisplay(BaseModel):
    username: str
    email: str

    class Config():
        orm_mode = True


class MovieCategory(str, Enum):
    action = "action"
    comedy = "comedy"
    drama = "drama"
    thriller = 'thriller'


class MovieModel(BaseModel):
    title: str
    type: MovieCategory
    number_comments: int
    year_published: int
    actors: List[str] = ['actor1', 'actor2', 'actor3']
    metadata: Dict[str, str] = {"key1": "value1"}
    image: Optional[Image] = None