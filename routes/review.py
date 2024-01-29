from fastapi import APIRouter,Depends ,HTTPException
from schemas import ReviewBase, ReviewDisplay,ReviewUpdate
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_review
from typing import List





router = APIRouter(
    prefix='/review',
    tags=['Review Endpoints']
)
# CRUD Operations for Review

# Create Review
@router.post('/add', response_model=ReviewDisplay)
def create_review(request: ReviewBase, db: Session = Depends(get_db)):
    try:
        new_review = db_review.create_review(db=db, request=request)
        return new_review
    except Exception as e:
        return str(e)
    
# Read All Review With User
@router.get('/all', response_model=List[ReviewDisplay])
def read_reviews(db: Session = Depends(get_db)):
    try:
        reviews = db_review.get_all_reviews(db)
        return reviews
    except Exception as e:
        return str(e)
  

# Read User By Id
@router.get('/{review_id}', response_model=ReviewDisplay)
def read_review_by_id(review_id: int, db: Session = Depends(get_db)):
     try:
         review = db_review.get_review(db, review_id)
         if review is None:
             raise HTTPException(status_code=404, detail=f"Review not found with user id: {review_id}")
         else:
             return review 
     except Exception as e:
         raise HTTPException(status_code= e.status_code, detail =  e.detail)



# Update Review
@router.post('/update/{review_id}', response_model=ReviewDisplay)
def update_review(review_id: int, request: ReviewUpdate, db: Session = Depends(get_db)):
    try:
        review = db_review.get_review(db, review_id)
        if review is None:
            raise HTTPException(status_code=404, detail=f"Review not found with review id: {review_id}")
        return db_review.update_review(db=db, review_id=review_id, review_data=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete Review
@router.delete('/delete/{review_id}')
def delete_review(review_id: int, db: Session = Depends(get_db)):
    try:
        review = db_review.get_review(db, review_id)
        if review is None:
            raise HTTPException(status_code=404, detail=f"Review not found with review id: {review_id}")
        db_review.delete_review(db, review_id)
        return {"message": f"Review with Id:{review_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code= e.status_code, detail =  e.detail)
    

