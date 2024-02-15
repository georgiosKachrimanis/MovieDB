from fastapi import Depends, HTTPException
from sqlalchemy.orm.session import Session
from db.database import get_db
from schemas import reviews_schemas
from db.models import Review
from db import db_reviews


# Create Review
def create_review(db: Session, request: reviews_schemas.ReviewBase,user_id: int):
    review = Review(
        review_content=request.review_content,
        movie_rate=request.movie_rate,
        user_id=user_id,
        movie_id=request.movie_id
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# Get Review By Id
def get_review(db: Session, review_id: int):
    return db.query(Review).filter(Review.id == review_id).first()

# Get All Reviews
def get_all_reviews(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Review).all()


# Update Review
def update_review(db: Session, review_id: int, review_data: reviews_schemas.ReviewUpdate):
    review = get_review(db, review_id)
    if review:
        for key, value in review_data.dict(exclude_unset=True).items():
            setattr(review, key, value)
        db.commit()
        db.refresh(review)
        return review

# Patch (Update Partially) Review
def patch_review(db: Session, review_id: int, review_data: reviews_schemas.ReviewUpdate):
    review = get_review(db, review_id)
    if review:
        for key, value in review_data.dict(exclude_unset=True).items():
            setattr(review, key, value)
        db.commit()
        db.refresh(review)
        return review    


# Delete Review
def delete_review(db: Session, review_id: int):
     review = db.query(Review).filter(Review.id == review_id).first()
     db.delete(review)
     db.commit()
     return 'Review with id :{review_id} deleted successfully'

# Get Review From DB
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

# Returns all Reviews from a movie
def all_reviews_for_movie(
    movie_id: int,
    db: Session = Depends(get_db),
):
    reviews = get_all_reviews(db=db)
    movie_reviews = []
    for review in reviews:
        if review.movie_id == movie_id:
            movie_reviews.append(review)

    if movie_reviews == []:
        raise HTTPException(
            status_code=404,
            detail="No reviews to show!",
        )
    return movie_reviews

# Returns all Reviews from a user
def all_reviews_for_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    reviews = get_all_reviews(db=db)
    user_reviews = []
    for review in reviews:
        if review.user_id == user_id:
            user_reviews.append(review)

    if user_reviews == []:
        raise HTTPException(
            status_code=404,
            detail="No reviews to show!",
        )
    return user_reviews