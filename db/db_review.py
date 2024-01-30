from sqlalchemy.orm.session import Session
from schemas import ReviewBase,ReviewUpdate
from db.models import Review



def get_review(db: Session, review_id: int):
    return db.query(Review).filter(Review.id == review_id).first()

def get_all_reviews(db: Session):
    return db.query(Review).all()

def create_review(db: Session, request: ReviewBase):
    new_review = Review(
        review_content=request.review_content,
        movie_rate=request.movie_rate,
        user_id=request.user_id,
        movie_id=request.movie_id
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
