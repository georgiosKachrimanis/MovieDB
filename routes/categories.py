from fastapi import HTTPException, Depends, APIRouter, status
from db.database import get_db
from sqlalchemy.orm import Session
from db import db_categories, db_movies
from typing import List
from schemas.movies_schemas import Category, CategoryName, MovieDisplayOne
from auth import oauth2
import routes.movies

router = APIRouter(prefix="/categories", tags=["Categories Endpoints"])


# CRUD Operations for Category
# Create Category
@router.post(
    "/add",
    response_model=Category,
    status_code=201,
)
def create_category(
    category_name: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    if oauth2.decode_access_token(token=token).get("user_type") == "admin":
        return db_categories.add_category(db, category_name)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


# Get All Categories
@router.get(
    "/",
    response_model=List[Category],
)
def get_categories(db: Session = Depends(get_db)):
    return db_categories.get_all_categories(db=db)


# Get Category By Id
@router.get(
    "/{category_id}",
    response_model=Category,
)
def get_category_by_id(
    category_id: int,
    db: Session = Depends(get_db),
):
    category = db_categories.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/{category_id}/movies", response_model=List[MovieDisplayOne])
def get_movies_by_category(
    category: int,
    db: Session = Depends(get_db),
):
    category_check = get_category_by_id(category_id=category, db=db)
    if not category_check:
        raise HTTPException(
            status_code=404,
            detail=f"Category {category} not found",
        )
    movies = db_movies.get_movies_by_category(
        category=category_check,
        db=db,
    )
    if not movies:
        raise HTTPException(
            status_code=404,
            detail=f"No movies found in category {category_check.category_name}",
        )

    return movies


# Update Category
@router.put(
    "/{category_id}",
    response_model=Category,
)
def update_category(
    category_id: int,
    request: CategoryName,
    token: str = Depends(oauth2.oauth2_schema),
    db: Session = Depends(get_db),
):
    category = db_categories.get_category(db=db, category_id=category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    if oauth2.decode_access_token(token=token).get("user_type") == "admin":
        return db_categories.update_category(
            db=db,
            category_id=category_id,
            request=request,
        )
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.delete(
    "/{category_id}",
    status_code=204,
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    category = db_categories.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    success = db_categories.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=500, detail="Something went wrong")
    return "Category with id: {category_id} deleted successfully"
