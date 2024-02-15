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
    """
    Creates a new review for a movie.
    
    Requires authentication. This endpoint allows authenticated users to post reviews for movies.
    It validates the existence of the movie in the database before creating the review.
    
    Parameters:
    - request: reviews_schemas.ReviewBase - The review to be created.
    - db: Session - Dependency injection of the database session.
    - token: str - The OAuth2 token for user authentication.
    
    Returns:
    - The created review's details as defined by the ReviewDisplayOne schema.
    
    Raises:
    - HTTPException: If the movie is not found or if there's an issue with user authentication.
    """
    
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
    """
    Retrieves all reviews, optionally filtered by user ID or movie ID.
    
    Parameters:
    - db: Session - Dependency injection of the database session.
    - user_id: Optional[int] - Optional user ID to filter reviews by user.
    - movie_id: Optional[int] - Optional movie ID to filter reviews by movie.
    
    Returns:
    - A list of reviews, each conforming to the ReviewDisplayAll schema.
    
    Raises:
    - HTTPException: If no reviews are found.
    """
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
    """
    Retrieves a review by its ID.
    
    Parameters:
    - review_id: int - The ID of the review to retrieve.
    - db: Session - Dependency injection of the database session.
    
    Returns:
    - The review's details as defined by the ReviewDisplayOne schema.
    """
    return db_reviews.get_review_from_db(review_id=review_id, db=db)


# Patch (Update Partially) Review
@router.patch("/{review_id}",response_model=reviews_schemas.ReviewDisplayOne)
def patch_review(
    review_id: int,
    request: reviews_schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Partially updates a review.
    
    Requires authentication. This endpoint allows users to partially update their own reviews or for admins to update any review.
    
    Parameters:
    - review_id: int - The ID of the review to update.
    - request: reviews_schemas.ReviewUpdate - The partial update data.
    - db: Session - Dependency injection of the database session.
    - token: str - The OAuth2 token for user authentication.
    
    Returns:
    - The updated review's details as defined by the ReviewDisplayOne schema.
    
    Raises:
    - HTTPException: If the review is not found, not owned by the user, or the user is not an admin.
    """
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
    """
    Fully updates a review.
    
    Requires authentication. This endpoint allows users to fully update their own reviews or for admins to update any review.
    
    Parameters:
    - review_id: int - The ID of the review to be updated.
    - request: reviews_schemas.ReviewUpdate - The new review data.
    - db: Session - Dependency injection of the database session.
    - token: str - The OAuth2 token for user authentication.
    
    Returns:
    - The fully updated review's details as defined by the ReviewDisplayOne schema.
    
    Raises:
    - HTTPException: If the review is not found, not owned by the user, or the user is not an admin.
    """
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
    """
    Deletes a review.
    
    Requires authentication. This endpoint allows users to delete their own reviews or for admins to delete any review.
    
    Parameters:
    - review_id: int - The ID of the review to be deleted.
    - db: Session - Dependency injection of the database session.
    - token: str - The OAuth2 token for user authentication.
    
    Returns:
    - A success message upon deletion.
    
    Raises:
    - HTTPException: If the review is not found, not owned by the user, or the user is not an admin.
    """
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
