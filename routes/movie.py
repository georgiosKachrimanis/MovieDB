from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from schemas import MovieBase, MovieDisplayAll, MovieUpdate, MovieDisplayOne
from db import db_movie

router = APIRouter(prefix="/movie", tags=["Movie Endpoints"])


# CRUD Operations for Movie
# Create Movie
@router.post("/", response_model=MovieDisplayOne)
def create_movie(movie: MovieBase, db: Session = Depends(get_db)):
    try:
        return db_movie.create_movie(db, movie)
    except Exception as e:
        return str(e)


# Get All Movies
@router.get("/", response_model=List[MovieDisplayAll])
def get_all_movies(db: Session = Depends(get_db)):
    try:
        return db_movie.get_all_movies(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get Movie By Id
@router.get("/{movie_id}", response_model=Optional[MovieDisplayOne])
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    try:
        movie = db_movie.get_movie(db, movie_id)
        if movie is None:
            raise HTTPException(
                status_code=404, detail="Movie with Id :{movie_id} not found"
            )
        return movie
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{movie_id}", response_model=Optional[MovieDisplayOne])
def update_movie(movie_id: int, movie: MovieUpdate, db: Session = Depends(get_db)):
    try:
        updated_movie = db_movie.update_movie(db, movie_id, movie)
        if updated_movie is None:
            raise HTTPException(
                status_code=404, detail="Movie with Id :{movie_id} not found"
            )
        return updated_movie
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    reviews = db_movie.get_movie_reviews(db, movie_id)
    if reviews:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete movie with Id :{movie_id} , it has review/s ",
        )
    success = db_movie.delete_movie(db, movie_id)
    if not success:
        raise HTTPException(
            status_code=404, detail=f"Movie with Id :{movie_id} not found"
        )
    return f'Movie with id: {movie_id} deleted successfully'
