from fastapi import APIRouter, Depends, HTTPException, status
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
from typing import List


router = APIRouter(
    prefix='/movies',
    tags=['Movies Endpoints']
)


@router.post("/add", response_model=MovieTestDisplay)
def create_movie(movie: MovieBase, db: Session = Depends(get_db)):
    try:
        return db_movies.create_movie(db, movie)
    except Exception as e:
        return str(e)