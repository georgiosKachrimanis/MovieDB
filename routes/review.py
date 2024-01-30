from fastapi import APIRouter, Depends, HTTPException, Response
from schemas.review_schemas import ReviewBase, ReviewUpdate, ReviewDisplay
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_review
from typing import List


router = APIRouter(prefix="/review", tags=["Review Endpoints"])


# CRUD Operations for Review
def get_review(review_id, db: Session = Depends(get_db)):
    review = db_review.get_review(review_id=review_id, db=db)
    if review is None:
        raise HTTPException(
            status_code=404, detail=f"Review with id: {review_id}  not found "
        )
    return review


# Create Review
@router.post("/add", response_model=ReviewDisplay)
def create_review(request: ReviewBase, db: Session = Depends(get_db)):
    try:
        new_review = db_review.create_review(db=db, request=request)
        return new_review
    except Exception as e:
        return str(e)


# Read All Review With User
@router.get("/all", response_model=List[ReviewDisplay])
def read_reviews(db: Session = Depends(get_db)):
    try:
        reviews = db_review.get_all_reviews(db)
        return reviews
    except Exception as e:
        return str(e)


# Read User By Id
@router.get("/{review_id}", response_model=ReviewDisplay)
def read_review_by_id(review_id: int, db: Session = Depends(get_db)):
    try:
        return get_review(review_id=review_id, db=db)
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# Update Review
@router.put("/update/{review_id}", response_model=ReviewDisplay)
def update_review(review_id: int, request: ReviewUpdate, db: Session = Depends(get_db)):
    try:
        review = get_review(review_id, db=db)
        if review is not None:
            return db_review.update_review(db=db, review_id=review_id, review_data=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Delete Review
@router.delete("/delete/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    try:
        review = get_review(review_id, db=db)
        if review is None:
            db_review.delete_review(db, review_id)
        return {"message": f"Review with Id:{review_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
