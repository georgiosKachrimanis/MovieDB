from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session
from auth import oauth2
from db import db_reviews
from db.database import get_db
from schemas.users_reviews_schemas import (
    CreateReview,
    ReviewDisplayOne,
    ReviewUpdate,
    ReviewDisplayAll,
)

router = APIRouter(prefix="/reviews", tags=["Review Endpoints"])


# CRUD Operations for Review
def get_review_from_db(
    review_id,
    db: Session = Depends(get_db),
):
    review = db_reviews.get_review(review_id=review_id, db=db)
    if review is None:
        raise HTTPException(
            status_code=404,
            detail=f"Review with id: {review_id} not found ",
        )
    return review


# Create Review
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ReviewDisplayOne,
)
def create_review(
    request: CreateReview,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

    user = oauth2.decode_access_token(token=token).get("user_id")

    new_review = db_reviews.create_review(
        db=db,
        request=request,
        user_id=user,
    )
    return new_review


# Read All Review With User
@router.get(
    "/",
    response_model=List[ReviewDisplayAll],
)
def get_all_reviews(db: Session = Depends(get_db)):

    reviews = db_reviews.get_all_reviews(db)
    if reviews is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews to show!",
        )
    return reviews


# Read User By Id
@router.get(
    "/{review_id}",
    response_model=ReviewDisplayOne,
)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
):
    return get_review_from_db(review_id=review_id, db=db)


# Update Review
@router.put(
    "/{review_id}")
def update_review(
    review_id: int,
    request: ReviewUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

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
@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

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
