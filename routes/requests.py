from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from schemas import movies_schemas,reviews_schemas
from db import db_movies, db_reviews
from auth import oauth2
import os
from db.db_movies import update_movie_poster_url,create_request_log
from routes import reviews
from services.movie_service import get_movie_extra_data


router = APIRouter(prefix="/movie", tags=["Movie Endpoints"])

AUTHENTICATION_TEXT = "You are not authorized to add, edit or delete a movie!"
# CRUD Operations for Movie

@router.get("/{movie_id}/request-count", response_model=MovieRequestCount)
def get_movie_request_count(
    movie_id: int,
    db: Session = Depends(get_db),
):
    movie = db_movies.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    request_count = db_movies.get_movie_request_count(db, movie_id)
    return MovieRequestCount(
        movie_id=movie.id,
        movie_title=movie.title,
        request_count=request_count,
    )

def post_review_for_movie(
    review_request: ReviewUpdate,
    movie: MovieBase = Depends(get_movie_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    oauth2.admin_authentication(
        token=token,
        exception_text=AUTHENTICATION_TEXT,
    )

    new_review = CreateReview(
        review_content=review_request.review_content,
        user_rating=review_request.user_rating,
        movie_id=movie.id,
    )
    return create_review(
        request=new_review,
        db=db,
        token=token,
    )