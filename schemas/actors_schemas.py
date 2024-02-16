from typing import List, Optional
from pydantic import BaseModel


# To avoid circular imports
class MovieBasicDisplay(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


# =================================== Actors ==================================


# Movie inside ActorDisplay
class Actor(BaseModel):
    id: int
    actor_name: str


class ActorAutoUpdate(BaseModel):
    actor_name: str


class ActorFullUpdate(Actor):
    movies: List[int] = []


class ActorPatch(BaseModel):
    actor_name: Optional[str] = None
    movies: Optional[List[int]] = None


class ActorDisplay(Actor):
    movies: List[MovieBasicDisplay] = []

    class Config:
        from_attributes = True
