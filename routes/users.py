from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    HTTPException,
)
from typing import Optional, List
from schemas.users_schemas import (
    UserBase,
    UserDisplay,
    UserUpdate,
    UserTypeDisplay,
    UserTypeUpdate,
)
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_users
from auth import oauth2

router = APIRouter(prefix="/users", tags=["Users Endpoints"])


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
        user = db_users.get_user(db=db, id=user_id)
    elif user_email is not None:
        user = db_users.get_user(db=db, email=user_email)
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


@router.post("/", response_model=UserDisplay)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    """
    Create a new user in the database.

    This function adds a new user to the database using the details
    provided in the request body. If a user with the same email
    already exists in the database, it raises an HTTP 400 error.

    Parameters:
    - request (UserBase): An object containing the new user's details.
    - db (Session, optional): The db session dependency. Injected by FastAPI.

    Returns:
    - UserDisplay: A model representing the created user's public data.

    Raises:
    - HTTPException: 400 error if a user with the provided email exists.
    """

    if db_users.get_user(db=db, email=request.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email: {request.email} already exists!",
        )
    new_user = db_users.create_user(db=db, request=request)
    return new_user


# Get all the users(Only Admins)
@router.get("/all", response_model=List[UserDisplay])
def get_users(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Retrieve a list of all users from the database.

    This endpoint fetches and returns all the users in the database.
    It is intended to be used by administrators for retrieving user info.
    The data of each user is formatted according to the UserDisplay model.

    Parameters: (Injected by FastAPI.)
    - db (Session, optional): The db session dependency.
    - token (str, optional): The OAuth2 token for authentication.

    Returns:
    - List[UserDisplay]: A list of users, with each user's information
    formatted as per the UserDisplay model.

    Raises:
    - HTTPException: 404 error if no users are found in the database.
    """
    payload = oauth2.decode_access_token(token=token)
    users = db_users.get_all_users(db=db)
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users table is empty!",
        )
    elif payload.get('user_type') == 'admin':
        return users
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


# Get User Information (Only User)
@router.get("/", response_model=UserDisplay)
def get_user(
    response: Response,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Retrieve information for a specific user.

    This endpoint fetches and returns the information of a specified user.
    The user can be identified by either their user ID or email address.
    The information returned is formatted according to the UserDisplay model.
    This endpoint is designed for individual users to access their own data.

    Parameters: (Injected by FastAPI)
    - response (Response): The response object.
    - db (Session, optional): The database session dependency.
    - user_id (int, optional): The user's unique identifier.
    - user_email (str, optional): The user's email address.
    - token (str, optional): The OAuth2 token for authentication.

    Returns:
    - UserDisplay: A model representing the user's public data.

    Raises:
    - HTTPException: 401 error if the user is unauthorized to view the data.
    """

    payload = oauth2.decode_access_token(token=token)
    user = check_user(db=db, user_email=user_email, user_id=user_id)
    if payload.get("user_id") == user.id:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


# Update User Information (Only User)
@router.put("/", response_model=UserDisplay)
def update_user(
    request: UserUpdate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Update information for a specific user.

    This endpoint allows a user to update their own information.
    The user can be identified by either their user ID or email address.
    The endpoint requires authentication and checks if the request is
    made by the user themselves or an admin.

    Parameters: (Injected by FastAPI)
    - request (UserUpdate): An object containing the updated user details.
    - db (Session, optional): The database session dependency.
    - user_id (int, optional): The user's unique identifier.
    - user_email (str, optional): The user's email address.
    - token (str, optional): The OAuth2 token for authentication.

    Returns:
    - UserDisplay: A model representing the updated user's public data.

    Raises:
    - HTTPException: 401 error if the user is unauthorized to update the data.
    """

    payload = oauth2.decode_access_token(token=token)
    user = check_user(db=db, user_id=user_id, user_email=user_email)

    if payload.get("user_id") == user.id:
        db_users.update_user(db=db, id=user_id, request=request)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


# Update User Type Information (Admin User)
@router.put("/type", response_model=UserTypeDisplay)
def update_user_type(
    request: UserTypeUpdate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Update the type of a specific user.

    This endpoint allows an admin to update the type of a user.
    It requires admin authentication. The user can be identified by either
    their user ID or email address.

    Parameters: (Injected by FastAPI)
    - request (UserUpdate): An object containing the updated user type details.
    - db (Session, optional): The database session dependency.
    - user_id (int, optional): The user's unique identifier.
    - user_email (str, optional): The user's email address.
    - token (str, optional): The OAuth2 token for authentication.

    Returns:
    - UserDisplay: A model representing the updated user's type.

    Raises:
    - HTTPException: 401 error if the user making the request is not an admin.
    """
    payload = oauth2.decode_access_token(token=token)
    user = check_user(db=db, user_id=user_id, user_email=user_email)

    if payload.get("user_type") == "admin":
        db_users.update_user_type(db=db, id=user_id, request=request)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


# Delete User (Only Admins)
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Delete a specific user from the database.

    This endpoint allows an admin to delete a user from the database.
    It requires admin authentication and is intended for administrative
    purposes.

    Parameters: (Injected by FastAPI)
    - user_id (int): The unique identifier of the user to be deleted.
    - db (Session, optional): The database session dependency.
    - token (str, optional): The OAuth2 token for authentication.

    Returns:
    - dict: A message indicating successful deletion of the user.

    Raises:
    - HTTPException: 401 error if the user making the request is not an admin.
    """
    payload = oauth2.decode_access_token(token=token)
    user = check_user(db=db, user_id=user_id)
    if payload.get("user_type") == "admin" and user:
        db_users.delete_user(db=db, id=user_id)
        return {"message": f"User with id:{user_id}  was deleted successfully"}
