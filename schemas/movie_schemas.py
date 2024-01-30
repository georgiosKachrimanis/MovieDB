from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel


class Image(BaseModel):
    url: str
    alias: str


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
    thriller = 'Thriller'
    western = "Western"


class MovieBase(BaseModel):
    title: str
    type: MovieCategory
    number_comments: int
    year_published: int
    actors: List[str] = ['actor1', 'actor2', 'actor3']
    metadata: Dict[str, str] = {"key1": "value1"}
    image: Optional[Image] = None
