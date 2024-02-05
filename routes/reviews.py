from fastapi import APIRouter, Depends, HTTPException, status
from schemas.users_reviews_schemas import (
    ReviewUpdate,
    ReviewDisplay,
    CreateReview,
)
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_reviews
from auth import oauth2
from typing import List


router = APIRouter(prefix="/reviews", tags=["Review Endpoints"])


# CRUD Operations for Review
def get_review_from_db(
    review_id,
    db: Session = Depends(get_db),
):
    """
    Retrieves a single review by its ID from the database.

    Parameters: (Injected by FastAPI)
    - review_id (int): The unique identifier of the review to retrieve.
    - db (Session, optional): The database session for executing database
    operations.

    Returns:
    - The retrieved review object if found, otherwise raises an HTTPException
    with a 404 status code.

    Raises:
    - HTTPException: A 404 error if no review with the given ID was found
    in the database.
    """
    review = db_reviews.get_review(review_id=review_id, db=db)
    if review is None:
        raise HTTPException(
            status_code=404,
            detail=f"Review with id: {review_id} not found ",
        )
    return review


# Create Review
@router.post("/", response_model=ReviewDisplay)
def create_review(
    request: CreateReview,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Creates a new review in the database.

    Parameters:
    - request (CreateReview): The review data to create, excluding the user ID.
    - db (Session, optional): The database session for executing database
    operations. Injected by FastAPI.
    - token (str, optional): The OAuth2 token for user authentication.
    Injected by FastAPI.

    Returns:
    - ReviewDisplay: The created review data.

    This endpoint requires a valid OAuth2 token for authentication.
    """
    user = oauth2.decode_access_token(token=token).get("user_id")
    new_review = db_reviews.create_review(
        db=db,
        request=request,
        user_id=user,
    )
    return new_review


# Read All Review With User
@router.get("/", response_model=List[ReviewDisplay])
def get_all_reviews(db: Session = Depends(get_db)):
    """
    Retrieves all reviews from the database.

    Parameters:
    - db (Session, optional): The database session for executing database
    operations. Injected by FastAPI.

    Returns:
    - List[ReviewDisplay]: A list of all review objects in the database.

    Raises:
    - HTTPException: A 404 error if no reviews are found in the database.
    """
    reviews = db_reviews.get_all_reviews(db)
    if reviews is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews to show!",
        )
    return reviews


# Read User By Id
@router.get("/{review_id}", response_model=ReviewDisplay)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves a specific review by its ID.

    Parameters:
    - review_id (int): The unique identifier of the review to retrieve.
    - db (Session, optional): The database session for executing database
    operations. Injected by FastAPI.

    Returns:
    - ReviewDisplay: The requested review object if found.

    Utilizes the get_review_from_db utility function to fetch the review.
    """
    return get_review_from_db(review_id=review_id, db=db)


# Update Review
@router.put(
    "/{review_id}",
)  # response_model=ReviewBase)
def update_review(
    review_id: int,
    request: ReviewUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Updates an existing review in the database.

    Parameters:
    - review_id (int): The unique identifier of the review to update.
    - request (ReviewUpdate): The updated review data.
    - db (Session, optional): The database session for executing database
    operations. Injected by FastAPI.
    - token (str, optional): The OAuth2 token for user authentication.
    Injected by FastAPI.

    Returns:
    - The updated review object if the operation is successful.

    Raises:
    - HTTPException: A 418 error if the user attempting the update is neither
    the owner of the review nor an admin.

    This endpoint requires a valid OAuth2 token for authentication and
    authorization.
    """
    user_payload = oauth2.decode_access_token(token=token)
    review = get_review_from_db(review_id=review_id, db=db)

    if (
        review.user_id == user_payload.get("user_id")
        or user_payload.get("user_type") == "admin"
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
    Deletes a specific review from the database.

    Parameters:
    - review_id (int): The unique identifier of the review to delete.
    - db (Session, optional): The database session for executing database
    operations. Injected by FastAPI.
    - token (str, optional): The OAuth2 token for user authentication.
    Injected by FastAPI.

    Returns:
    - A message indicating successful deletion if the operation is successful.

    Raises:
    - HTTPException: A 418 error if the user attempting the deletion is
    neither the owner of the review nor an admin.

    This endpoint requires a valid OAuth2 token for authentication
    and authorization.
    """
    user_payload = oauth2.decode_access_token(token=token)
    review = get_review_from_db(review_id=review_id, db=db)

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
