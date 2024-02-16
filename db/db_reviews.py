from sqlalchemy.orm.session import Session
from fastapi import HTTPException
from db.models import DbReview
from schemas.reviews_schemas import (
    CreateReview,
    ReviewUpdate,
)


# TODO: check if i am passing user/reviews objects and not just ids
def get_review(review_id: int, db: Session):
    return db.query(DbReview).filter(DbReview.id == review_id).first()


def get_all_reviews(
    db: Session,
    skip: int = 0,
):
    return db.query(DbReview).all()


def create_review(
    db: Session,
    request: CreateReview,
    user_id: int,
):

    new_review = DbReview(
        review_content=request.review_content,
        user_rating=request.user_rating,
        movie_id=request.movie_id,
        user_id=user_id,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


def update_review(
    db: Session,
    review_id: int,
    review_data: ReviewUpdate,
):
    review = get_review(db=db, review_id=review_id)
    if review:
        for key, value in review_data.dict(exclude_unset=True).items():
            setattr(review, key, value)
        db.commit()
        db.refresh(review)
        return review


def delete_review(
    db: Session,
    review_id: int,
):
    db_review = db.query(DbReview).filter(DbReview.id == review_id).first()
    db.delete(db_review)
    db.commit()
    return "Review deleted successfully"


def get_all_reviews_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
):
    user_reviews = db.query(DbReview).filter(DbReview.user_id == user_id).all()

    if not user_reviews:
        raise HTTPException(
            status_code=404,
            detail=f"No reviews for user with id: {user_id}",
        )

    return user_reviews
