from fastapi import APIRouter, Depends, Response, status, HTTPException
from typing import Optional, List
from schemas.user_schemas import UserBase, UserDisplay, UserUpdate
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_user

router = APIRouter(prefix="/user", tags=["user"])


def check_user(db: Session, user_id: int = None, user_email: str = None):
    """
    Check if a user exists in the database by ID or email.

    This function checks for the existence of a user either by their unique ID
    or by their email address. If neither user_id nor user_email is provided,
    it raises an HTTP 404 error.

    Parameters:
    - db (Session): The SQLAlchemy session for database operations.
    - user_id (int, optional): The unique identifier of the user.
    - user_email (str, optional): The email address of the user.

    Returns:
    - The user object if found.

    Raises:
    - HTTPException: 404 error if neither user_id nor user_email is provided,
                     or if no user is found with the provided identifier.
    """
    if user_id is not None:
        user = db_user.get_user(db=db, id=user_id)
    elif user_email is not None:
        user = db_user.get_user(db=db, email=user_email)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User ID or email must be provided",
        )
    if user is None:
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email: {user_email} not found",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID: {user_id} not found",
            )
    return user


@router.post("/add", response_model=UserDisplay)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    """
    Create a new user.

    This function creates a new user with the provided details. If a user
    with the given email already exists, it raises an HTTP 400 error.

    - request: UserBase - The user details.
    - db: Session - The database session.

    Returns a UserDisplay model of the created user.
    """
    if db_user.get_user(db=db, email=request.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email: {request.email} already exists!",
        )
    new_user = db_user.create_user(db=db, request=request)
    return new_user


@router.get("/all", response_model=List[UserDisplay])
def get_users(db: Session = Depends(get_db)):
    """
    Retrieve all users.

    This endpoint retrieves a list of all users from the database. Each user's
    data is formatted according to the UserDisplay model. This operation is
    useful for obtaining a complete list of users for administrative or
    data analysis purposes.

    Parameters:
    - db (Session, optional): The SQLAlchemy session for database operations.
    This dependency is injected automatically by FastAPI.

    Returns:
    - List[UserDisplay]: A list containing user information, with each user's
                        data formatted according to the UserDisplay model.
                        If the users table is empty, an HTTP 404 error is
                        raised with a message indicating that table is empty.

    Raises:
    - HTTPException: A 404 error is raised if the users table is empty.
    """

    users = db_user.get_all_users(db=db)
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users table is empty!",
        )
    else:
        return users


@router.get("/", response_model=UserDisplay)
def get_user(
    response: Response,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
):
    """
    Retrieve a user by their ID or email.

    This endpoint retrieves user details from the database either by the user's
    unique ID or by their email address.

    Parameters:
    - response (Response): The FastAPI response object.
    - db (Session): The SQLAlchemy session for database operations.
    - user_id (int, optional): The unique identifier of the user.
    - user_email (str, optional): The email address of the user.

    Returns:
    - UserDisplay: The user's information in the format defined
                    by the UserDisplay model.

    Raises:
    - HTTPException: 404 error if neither user_id nor user_email is provided,
                     or if no user is found with the provided identifier.
    """
    return check_user(db=db, user_email=user_email, user_id=user_id)


@router.put("/update/", response_model=UserDisplay)
def update_user(
    request: UserUpdate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
):
    """
    Update an existing user's information.

    Updates user data identified by either ID or email with new details
    provided in the request. If the user isn't found, it returns an error.

    Parameters:
    - request (UserUpdate): New details for the user.
    - db (Session): SQLAlchemy session for DB operations.
    - user_id (int, optional): Unique identifier of the user.
    - user_email (str, optional): Email address of the user.

    Returns:
    - UserDisplay: Updated user information.

    Raises:
    - HTTPException: 404 error if the user is not found.
    """
    user = check_user(db=db, user_id=user_id, user_email=user_email)
    if user is not None:
        db_user.update_user(db=db, id=user_id, request=request)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by their ID.

    Deletes a user from the database using their unique ID. Returns a message
    on successful deletion or raises a 404 error if the user is not found.

    Parameters:
    - user_id (int): The unique identifier of the user.
    - db (Session, optional): SQLAlchemy session for database operations.

    Returns:
    - dict: Message indicating the user's successful deletion.

    Raises:
    - HTTPException: 404 error if no user with the specified ID is found.
    """
    user = check_user(db=db, user_id=user_id)
    if user is not None:
        db_user.delete_user(db=db, id=user_id)
        return {"message": f"User with id:{user_id}  was deleted successfully"}
