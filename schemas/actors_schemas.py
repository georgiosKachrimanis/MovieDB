from typing import List
from pydantic import BaseModel

# Movie inside ActorDisplay
class Movie(BaseModel):
    id: int
    title: str

class ActorBase(BaseModel):
    actor_name: str

class ActorDisplay(BaseModel):
    id: int
    actor_name: str
    movies: List[Movie] = []
    class Config:
        from_attributes = True