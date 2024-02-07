from pydantic import BaseModel
from typing import  List
from db.models import Movie


# Movie inside ReviewDisplay
class Movie(BaseModel):
    id: int
    title: str

class DirectorBase(BaseModel):
    director_name: str

class DirectorDisplay(BaseModel):
    id: int
    director_name: str
    movies: List[Movie] = []

    class Config:
        from_attributes = True