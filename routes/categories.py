from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from auth import oauth2
from db import db_categories
from db.database import get_db
from schemas.mov_dir_actors_schemas import (
    Category,
    CategoryName,
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories Endpoints"],
)


AUTH_EXCEPTION = "You aren't authorized to add, edit or delete categories"


# CRUD Operations for Category
# Create Category
@router.post(
    "/",
    response_model=Category,
    status_code=201,
)
def create_category(
    category_name: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Creates a new category in the database. Requires admin authentication.

    Parameters:
    - category_name (str): The name of the category to create.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Returns:
    - Category: The created category object.
    """

    oauth2.admin_authentication(token=token, detail=AUTH_EXCEPTION)

    return db_categories.add_category(
        db,
        category_name,
    )


# Get All Categories
@router.get(
    "/",
    response_model=List[Category],
)
def get_categories(db: Session = Depends(get_db)):
    """
    Retrieves all categories from the database.

    Parameters:
    - db (Session): Database session for executing database operations.

    Returns:
    - List[Category]: A list of all category objects.
    """
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
    """
    Retrieves a category by its ID.

    Parameters:
    - category_id (int): The ID of the category to retrieve.
    - db (Session): Database session for executing database operations.

    Raises:
    - HTTPException: 404 Not Found if the category with the specified ID 
        does not exist.

    Returns:
    - Category: The requested category object.
    """
    category = db_categories.get_category_with_id(
        db,
        category_id,
    )
    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )
    return category


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
    """
    Updates the name of an existing category. Requires admin authentication.

    Parameters:
    - category_id (int): The ID of the category to update.
    - request (CategoryName): The new name for the category.
    - token (str): OAuth2 token to authenticate the request.
    - db (Session): Database session for executing database operations.

    Raises:
    - HTTPException: 404 Not Found if the category with the specified ID 
        does not exist.

    Returns:
    - Category: The updated category object.
    """
    oauth2.admin_authentication(token=token)

    category = db_categories.get_category_with_id(
        db=db,
        category_id=category_id,
    )

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return db_categories.update_category(
        db=db,
        category_id=category_id,
        request=request,
    )


@router.delete(
    "/{category_id}",
    status_code=204,
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Deletes a category from the database. Requires admin authentication.

    Parameters:
    - category_id (int): The ID of the category to delete.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Raises:
    - HTTPException: 404 Not Found if the category with the specified ID does
    not exist.

    Returns:
    - A status code of 204 No Content on successful deletion.
    """

    oauth2.admin_authentication(token=token)

    category = db_categories.get_category_with_id(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    db_categories.delete_category(db, category_id)
