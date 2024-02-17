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
    """
    Creates a new category in the database.
    
    This endpoint requires admin authentication. It accepts category data conforming to the CategoryBase schema,
    creates a new category record in the database, and returns the created category's data including the generated ID.
    
    Parameters:
    - category: categories_schemas.CategoryBase - The category data to create.
    - db: Session - The database session.
    - token: str - The OAuth2 token for admin authentication.
    
    Returns:
    - The created category's data, including the ID.
    """
    if oauth2.admin_authentication(token=token):
        return db_categories.create_category(db, category)


# Get All Categories
@router.get("/", response_model=List[categories_schemas.CategoryDisplay])
def get_all_categories(db: Session = Depends(get_db)):
    """
    Retrieves all categories from the database.
    
    This endpoint fetches and returns a list of all categories currently stored in the database,
    with each category's information conforming to the CategoryDisplay schema.
    
    Parameters:
    - db: Session - The database session.
    
    Returns:
    - A list of all categories in the database.
    """
    return db_categories.get_all_categories(db)


# Get Category By Id
@router.get("/{category_id}", response_model=categories_schemas.CategoryDisplay)
def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single category by its ID.
    
    Fetches and returns the data of a specific category, identified by its ID.
    If the category with the given ID does not exist, it raises a 404 HTTPException.
    
    Parameters:
    - category_id: int - The ID of the category to retrieve.
    - db: Session - The database session.
    
    Returns:
    - The data of the requested category.
    """
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
    """
    Retrieves movies associated with a specific category.
    
    This endpoint fetches and returns a list of movies that are associated with the specified category ID.
    It validates if the category exists before fetching the movies. If the category or movies are not found, it raises a 404 HTTPException.
    
    Parameters:
    - category: int - The ID of the category whose movies are to be fetched.
    - db: Session - The database session.
    
    Returns:
    - A list of movies associated with the specified category.
    """
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
    """
    Retrieves the top 10 movies within a specific category based on average movie rate.
    
    This endpoint sorts the movies within a given category by their average movie rate in descending order
    and returns the top 10 movies.
    
    Dependencies:
    - movies: Depends(get_movies_by_category) - A list of movies fetched based on the category.
    
    Returns:
    - A list of the top 10 movies in the specified category.
    """
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
    """
    Updates an existing category's information.
    
    Requires admin authentication to update the data of an existing category, identified by its ID.
    If the category does not exist, it raises a 404 HTTPException.
    
    Parameters:
    - category_id: int - The ID of the category to update.
    - request: categories_schemas.CategoryBase - The new data for the category.
    - db: Session - The database session.
    - token: str - The OAuth2 token for admin authentication.
    
    Returns:
    - The updated category's data.
    """
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
    """
    Deletes a category from the database.
    
    Requires admin authentication. This endpoint allows for the deletion of a category by its ID.
    If the category does not exist or is associated with a movie, it raises an HTTPException.
    
    Parameters:
    - category_id: int - The ID of the category to delete.
    - db: Session - The database session.
    - token: str - The OAuth2 token for admin authentication.
    
    Returns:
    - A success message indicating the category has been deleted.
    """
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
