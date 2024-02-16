from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import oauth2
from db import db_directors
from db.database import get_db
from schemas.directors_schemas import Director, DirectorDisplay, DirectorUpdate

router = APIRouter(
    prefix="/directors",
    tags=["Directors Endpoints"],
)

AUTHENTICATION_TEXT = "You are not authorized to add, edit or delete directors"


# CRUD Operations for Directors
# Create Director
@router.post(
    "/",
    response_model=Director,
    status_code=status.HTTP_201_CREATED,
)
def create_director(
    request: Director,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Creates a new director in the database. Requires admin authentication.

    Parameters:
    - request (Director): The director data to create.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Returns:
    - Director: The created director object.
    """
    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )

    return db_directors.create_director(
        db=db,
        request=request,
    )


# Get Director By Id
@router.get(
    "/{director_id}",
    response_model=DirectorDisplay,
)
def get_director_by_id(
    director_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves a director by their ID.

    Parameters:
    - director_id (int): The ID of the director to retrieve.
    - db (Session): Database session for executing database operations.

    Raises:
    - HTTPException: 404 Not Found if the director with the specified ID does
    not exist.

    Returns:
    - DirectorDisplay: The requested director's information.
    """
    director = db_directors.get_director(
        db=db,
        director_id=director_id,
    )
    if director:
        return director
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Director with id {director_id} not found",
        )


# Get All Directors
@router.get(
    "/",
    response_model=List[DirectorDisplay],
)
def get_all_directors(db: Session = Depends(get_db)):
    """
    Retrieves all directors from the database.

    Parameters:
    - db (Session): Database session for executing database operations.

    Returns:
    - List[DirectorDisplay]: A list of all director objects.
    """
    return db_directors.get_all_directors(db)


# Update Director
@router.put(
    "/{director_id}",
    response_model=DirectorDisplay,
)
def update_director(
    request: DirectorUpdate,
    director: Director = Depends(get_director_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Updates an existing director in the database. Requires admin
    authentication.

    Parameters:
    - request (DirectorUpdate): The updated data for the director.
    - director (Director): The current director object from the database,
    obtained via dependency.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Returns:
    - DirectorDisplay: The updated director's information.
    """
    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )

    return db_directors.update_director(
        db=db,
        director=director,
        request=request,
    )


# Delete Director
@router.delete(
    "/{director_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_director(
    director: Director = Depends(get_director_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Deletes a director from the database. Requires admin authentication.
    The director cannot be deleted if they are associated with any movies.

    Parameters:
    - director (Director): The director object to delete, obtained via
        dependency.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Raises:
    - HTTPException: 409 Conflict if the director is associated with any
        movies.

    Returns:
    - A status code of 204 No Content on successful deletion.
    """
    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )

    movies = db_directors.check_director_in_movie(db, director.id)
    if movies:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Director is associated with movies. Can't be deleted!",
        )
    else:
        return db_directors.delete_director(db, director.id)


@router.post("/auto_add_directors", status_code=status.HTTP_201_CREATED)
def auto_add_directors(db: Session = Depends(get_db)):
    """
    THIS IS ONLY TO BE USED FOR TESTING PURPOSES
    """
    import json

    with open("example_files/example_directors.json", "r") as file:
        directors = json.load(file)

    for director in directors:
        db_directors.create_director(db=db, request=Director(**director))
    return {"message": "Directors added successfully"}
