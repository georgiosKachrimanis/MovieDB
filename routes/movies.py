from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from routes.categories import validate_category
from auth import oauth2
from db import db_movies
from db.database import get_db
from db.models import DbMovie
from schemas.movies_schemas import (
    MovieBase,
    MovieCategoryType,
    MovieDisplayAll,
    MovieDisplayOne,
    MovieTestDisplay,
    MovieUpdate,
)

router = APIRouter(prefix="/movies", tags=["Movies Endpoints"])


# Check if a movie with the given title already exists
def check_existing_movie(movie: MovieBase, db: Session):
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


# Get Movie By Title
@router.get("/", response_model=Optional[MovieDisplayOne])
def get_movie_by_title(
    movie_title: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if movie_title:
        movie = db_movies.get_movie(db=db, movie_title=movie_title)
        if movie is None:
            raise HTTPException(
                status_code=404,
                detail=f"Movie named: {movie_title} not found",
            )
        return movie

    raise HTTPException(status_code=400, detail="Movie title is required")


# Get Movie By Id
@router.get("/{movie_id}", response_model=Optional[MovieDisplayOne])
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    movie = db_movies.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(
            status_code=404, detail=f"Movie with Id :{movie_id} not found"
        )
    return movie


# TODO: Check how the request is created
@router.get("/category/{category_label}", response_model=List[MovieDisplayOne])
def get_movies_by_category(
    category: str = Depends(validate_category), db: Session = Depends(get_db)
):
    movies = db_movies.get_movies_by_category(category=category, db=db)

    return movies
