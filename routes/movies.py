from fastapi import APIRouter, Depends, HTTPException, Request, status
from db.models import DbMovie
from schemas.movies_schemas import (
    MovieBase,
    MovieDisplayAll,
    MovieDisplayOne,
    MovieUpdate,
    MovieTestDisplay,
)
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_movies
from auth import oauth2
from typing import List, Optional


router = APIRouter(prefix="/movies", tags=["Movies Endpoints"])


def check_existing_movie(movie: MovieBase, db: Session):
    # Check if a movie with the given title already exists
    existing_movie = db.query(DbMovie).filter(DbMovie.title == movie.title).first()
    if existing_movie:

        raise HTTPException(
            status_code=400, detail="A movie with the given title already exists."
        )
    return "ok"


@router.post("/", response_model=MovieDisplayOne)
def create_movie(movie: MovieBase, db: Session = Depends(get_db)):
    if check_existing_movie(movie=movie, db=db) == "ok":
        try:
            return db_movies.create_movie(db, movie)
        except Exception as e:
            return str(e)


# Get Movie By Id
@router.get("/{movie_id}", response_model=Optional[MovieDisplayOne])
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    try:
        movie = db_movies.get_movie(db, movie_id)
        if movie is None:
            raise HTTPException(
                status_code=404, detail="Movie with Id :{movie_id} not found"
            )
        return movie
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
