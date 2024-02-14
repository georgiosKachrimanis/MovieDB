from fastapi import HTTPException, Depends, APIRouter
from db.database import get_db
from sqlalchemy.orm import Session
from db import db_categories, db_movies
from typing import List
from schemas import categories_schemas, movies_schemas
from auth import oauth2


router = APIRouter(prefix="/categories", tags=["Category Endpoints"])


# CRUD Operations for Category


# Create Category
@router.post("/", response_model=categories_schemas.CategoryDisplay)
def create_category(
    category: categories_schemas.CategoryBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    if oauth2.admin_authentication(token=token):
        return db_categories.create_category(db, category)


# Get All Categories
@router.get("/", response_model=List[categories_schemas.CategoryDisplay])
def get_all_categories(db: Session = Depends(get_db)):
    return db_categories.get_all_categories(db)


# Get Category By Id
@router.get("/{category_id}", response_model=categories_schemas.CategoryDisplay)
def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    category = db_categories.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# Get Movies By Category
@router.get(
    "/{category_id}/movies",
    response_model=List[movies_schemas.MovieDisplayBase],
)
def get_movies_by_category(
    category: int,
    db: Session = Depends(get_db),
):
    category_check = get_category_by_id(
        category_id=category,
        db=db,
    )
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
            detail=f"No movies in category {category_check.category_name}",
        )

    return movies


# Get Top 10 Movies By Category
@router.get(
    "/{category_id}/movies/top10",
    response_model=List[movies_schemas.MovieDisplayBase],
)
def get_top10_movies_by_category(movies=Depends(get_movies_by_category)):
    sorted_movies = sorted(
        movies,
        key=lambda x: x.average_movie_rate,
        reverse=True,
    )

    top_10_movies = sorted_movies[:10]
    return top_10_movies


# Update Category
@router.put("/{category_id}", response_model=categories_schemas.CategoryDisplay)
def update_category(
    category_id: int,
    request: categories_schemas.CategoryBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    if oauth2.admin_authentication(token=token):
        category = db_categories.get_category(db, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return db_categories.update_category(
            db=db, category_id=category_id, request=request
        )


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    if oauth2.admin_authentication(token=token):
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


# Add sample data to the categories table
@router.post("/auto_add_categories")
def auto_add_categories(db: Session = Depends(get_db)):
    """
    THIS IS ONLY TO BE USED FOR TESTING PURPOSES
    """
    import json

    with open("sampleData/example_categories.json", "r") as file:
        categories = json.load(file)

    for category in categories:
        db_categories.create_category(
            db=db, category=categories_schemas.CategoryBase(**category)
        )
    return {"message": "Categories added successfully"}
