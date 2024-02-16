# To avoid circular imports
from typing import List
from pydantic import BaseModel


# In order to avoid circular imports
class MovieBasicDisplay(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


# =========================== Directors Schemas ===============================
class Director(BaseModel):
    director_name: str


class DirectorUpdate(Director):
    movies: List[int] = []


class DirectorDisplay(Director):
    id: int
    movies: List[MovieBasicDisplay] = []

    class Config:
        from_attributes = True
