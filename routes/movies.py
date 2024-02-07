from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from schemas import movies_schemas
from db import db_movies
from auth import oauth2

router = APIRouter(prefix="/movie", tags=["Movie Endpoints"])


# CRUD Operations for Movie
# Create Movie
@router.post("/", response_model=movies_schemas.MovieDisplayOne)
def create_movie(
    movie: movies_schemas.MovieBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create a movie",
        )
    else:
        return db_movies.create_movie(db, movie)


# Get All Movies
@router.get("/", response_model=List[movies_schemas.MovieDisplayAll])
def read_all_movies(db: Session = Depends(get_db)):
    try:
        return db_movies.get_all_movies(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get Movie By Id
@router.get("/{movie_id}", response_model=Optional[movies_schemas.MovieDisplayOne])
def read_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    try:
        movie = db_movies.get_movie(db, movie_id)
        if movie is None:
            raise HTTPException(
                status_code=404, detail="Movie with Id :{movie_id} not found"
            )
        return movie
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{movie_id}", response_model=Optional[movies_schemas.MovieDisplayOne])
def update_movie(
    movie_id: int,
    movie: movies_schemas.MovieUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") == "admin":
        movie = db_movies.get_movie(db, movie_id)
        if movie is None:
            raise HTTPException(
                status_code=404, detail="Movie with Id :{movie_id} not found"
            )
        return db_movies.update_movie(db, movie_id, movie)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create a movie",
        )


@router.delete("/{movie_id}")
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") == "admin":
        if  db_movies.check_movie_in_reviews(db, movie_id):
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete movie with Id :{movie_id} , it has review/s ",
            )
        success = db_movies.delete_movie(db, movie_id)
        if not success:
            raise HTTPException(
                status_code=404, detail=f"Movie with Id :{movie_id} not found"
            )
        return f"Movie with id: {movie_id} deleted successfully"
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete a movie",
        )
