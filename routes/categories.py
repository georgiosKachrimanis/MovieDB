from fastapi import HTTPException, Depends, APIRouter, status
from db.database import get_db
from sqlalchemy.orm import Session
from db import db_categories
from typing import List
from schemas import categories_schemas
from auth import oauth2


router = APIRouter(prefix="/categories", tags=["Category Endpoints"])


# CRUD Operations for Category
# Create Category
@router.post("/", response_model=categories_schemas.CategoryDisplay)
def create_category(
    category_name: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create a category",
        )
    else:
        return db_categories.create_category(db, category_name)


# Get All Categories
@router.get("/", response_model=List[categories_schemas.CategoryDisplay])
def read_all_categories(db: Session = Depends(get_db)):
    return db_categories.get_all_categories(db)


# Get Category By Id
@router.get("/{category_id}", response_model=categories_schemas.CategoryDisplay)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = db_categories.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# Update Category
@router.put("/{category_id}", response_model=categories_schemas.CategoryDisplay)
def update_category(
    category_id: int,
    request: categories_schemas.CategoryBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") == "admin":
        category = db_categories.get_category(db, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return db_categories.update_category(
            db=db, category_id=category_id, request=request
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to update a category",
        )


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") == "admin":
        category = db_categories.get_category(db, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        else:
            if db_categories.check_category_in_movie(db, category_id):
                db_categories.delete_category(db, category_id)
            else:
                raise HTTPException(
                    status_code=409,
                    detail="This category is associated with a movie. Cannot delete.",
                )
        return f"Category with id: {category_id} deleted successfully"
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete a category",
        )
