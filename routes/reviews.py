from fastapi import APIRouter, Depends, HTTPException, status
from schemas import reviews_schemas
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_reviews, db_movies
from auth import oauth2
from typing import List, Optional
from db.models import Movie


router = APIRouter(prefix="/reviews", tags=["Review Endpoints"])


# CRUD Operations for Review

# Create Review
@router.post("/", response_model=reviews_schemas.ReviewDisplayOne)
def create_review(
    request: reviews_schemas.ReviewBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    
    try:
        payload = oauth2.decode_access_token(token=token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="You need to log in to create a review!",
        ) from e
    else:
        movie = db_movies.get_movie(db=db, movie_id=request.movie_id)
        if movie is not None:
            user_id = payload.get("user_id")
            new_review = db_reviews.create_review(db=db, request=request, user_id=user_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found!",
        )
    return new_review


# Get All Reviews
@router.get("/", response_model=List[reviews_schemas.ReviewDisplayAll])
def get_all_reviews(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    movie_id: Optional[int] = None,
    ):
    reviews = db_reviews.get_all_reviews(db)
    if reviews is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews to show!",
        )
    
    if user_id:
        user_reviews = []
        for review in reviews:
            if review.user_id == user_id:
                user_reviews.append(review)
        reviews = user_reviews
    if movie_id:
            movie_reviews = []
            for review in reviews:
                if review.movie_id == movie_id:
                    movie_reviews.append(review)
            reviews = movie_reviews
    return reviews



# # Get all reviews for a user
# @router.get("/{user_id}/reviews",response_model=List[reviews_schemas.ReviewDisplayAll])
# def get_all_user_reviews(user_id=int, db: Session = Depends(get_db)):
#     db_reviews = get_all_reviews(db=db)
#     user_reviews = []
#     for review in db_reviews:
#         if review.user_id == int(user_id):
#             user_reviews.append(review)
#     return user_reviews


# Get Reviw By Id
@router.get("/{review_id}", response_model=reviews_schemas.ReviewDisplayOne)
def get_review_by_id(
    review_id: int,
    db: Session = Depends(get_db),

):
    return db_reviews.get_review_from_db(review_id=review_id, db=db)


# Patch (Update Partially) Review
@router.patch("/{review_id}",response_model=reviews_schemas.ReviewDisplayOne)
def patch_review(
    review_id: int,
    request: reviews_schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    review = db_reviews.get_review_from_db(review_id=review_id, db=db)

    if (
        review.user_id == payload.get("user_id")
        or payload.get("user_type") == "admin"
    ):
        if review is not None:
            return db_reviews.patch_review(
                db=db, review_id=review_id, review_data=request
            )
        return review
    else:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Not your review, you can not change it!",
        )

# Update Review
@router.put(
    "/{review_id}",response_model=reviews_schemas.ReviewDisplayOne
)  
def update_review(
    review_id: int,
    request: reviews_schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    review = db_reviews.get_review_from_db(review_id=review_id, db=db)

    if (
        review.user_id == payload.get("user_id")
        or payload.get("user_type") == "admin"
    ):
        if review is not None:
            return db_reviews.update_review(
                db=db, review_id=review_id, review_data=request
            )
        return review
    else:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Not your review, you can not change it!",
        )


# Delete Review
@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    user_payload = oauth2.decode_access_token(token=token)
    review = db_reviews.get_review_from_db(review_id=review_id, db=db)

    if (
        review.user_id == user_payload.get("user_id")
        or user_payload.get("user_type") == "admin"
    ):
        if review is not None:
            return db_reviews.delete_review(
                db=db,
                review_id=review_id,
            )
        return review
    else:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Not your review, you can not delete it!",
        )




@router.post("/auto_add_reviews")
def auto_add_reviews(db: Session = Depends(get_db)):
    import random
    import json

    """
    THIS IS ONLY TO BE USED FOR TESTING PURPOSES
    """

    with open("sampleData/example_reviews.json", "r") as file:
        reviews = json.load(file)

    for review_data in reviews:
        user_id = random.randint(1, 5)
        db_reviews.create_review(
            db=db,
            request=reviews_schemas.ReviewBase(**review_data),
            user_id=user_id,
        )
    return {"message": "Reviews added successfully"}