from sqlalchemy.orm.session import Session
from schemas import ReviewDisplay,ReviewBase,ReviewUpdate
from db.models import Review
from fastapi import Response


def get_review(db: Session, review_id: int):
    return db.query(Review).filter(Review.id == review_id).first()

def get_all_reviews(db: Session, skip: int = 0):
        return db.query(Review).all()

def create_review(db: Session, request:ReviewBase):
    new_review = Review(
                review_content = request.review_content,
                user_rate = request.user_rate,
                user_id = request.user_id,
        )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


def update_review(db: Session, review_id: int, review_data: ReviewUpdate):
    review = get_review(db, review_id)
    if review:
        for key, value in review_data.dict(exclude_unset=True).items():
            setattr(review, key, value)
        db.commit()
        db.refresh(review)
        return review



def delete_review(db: Session, review_id: int):
     db_review = db.query(Review).filter(Review.id == review_id).first()
     db.delete(db_review)
     db.commit()
     return 'Review deleted successfully'
