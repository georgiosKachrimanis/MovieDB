from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import DbCategory


router = APIRouter(prefix="/categories", tags=["Categories Endpoints"])

# TODO: Update the validate category
@router.get("/")
def list_available_categories(db: Session = Depends(get_db)):
    categories = db.query(DbCategory.category_name).all()
    return [category.category_name for category in categories]


def validate_category(category_label: str = Path(..., description="The category of the movie")):
    db = next(get_db())  # Assuming get_db is a generator dependency
    category = db.query(DbCategory).filter(DbCategory.category_name == category_label).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{category_label}' not found")
    return category_label

