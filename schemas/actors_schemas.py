from typing import List
from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel

# Movie inside ActorDisplay
class Movie(BaseModel):
    id: int
    title: str

class ActorBase(BaseModel):
    actor_name: str

class ActorDisplayOne(BaseModel):
    id: int
    actor_name: str
    movies: List[Movie] = []
    class Config:
        from_attributes = True

class ActorDisplayAll(BaseModel):
    id: int
    actor_name: str
    class Config:
        from_attributes = True

class ActorPatch(BaseModel):
    actor_name: Optional[str] = None
    movies: Optional[List[int]] = None