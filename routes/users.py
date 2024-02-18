from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
)
from sqlalchemy.orm import Session
from auth import oauth2
from db import db_users
from db.database import get_db
from routes.reviews import get_all_reviews
from schemas.users_schemas import (
    UserBase,
    UserDisplay,
    UserTypeDisplay,
    UserTypeUpdate,
    UserUpdate,
)

router = APIRouter(
    prefix="/users",
    tags=["Users Endpoints"],
)


AUTHENTICATION_TEXT = "You are not authorized to interact with the user(s)!"
DELETE_TEXT = "You are not allowed to delete your self!"


def check_user(
    db: Session,
    user_id: int,
):
    """
    Checks if a user exists in the database by their ID.

    Parameters:
    - db (Session): Database session for executing database operations.
    - user_id (int): The ID of the user to check.

    Raises:
    - HTTPException: 404 Not Found if the user with the specified ID does not 
    exist.

    Returns:
    - The user object if found.
    """

    user = db_users.get_user(
        db=db,
        id=user_id,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID: {user_id} not found",
        )
    return user


# ======================= GET Functions ====================
# Get all the users(Only Admins)
@router.get(
    "/",
    response_model=List[UserDisplay],
)
def get_users(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Retrieves all users from the database. This endpoint is restricted
    to admins only.

    Parameters:
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Raises:
    - HTTPException: 404 Not Found if the users table is empty.
    - HTTPException: 401 Unauthorized if the requester is not an admin.

    Returns:
    - List[UserDisplay]: A list of all users.
    """

    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )
    users = db_users.get_all_users(db=db)
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users table is empty!",
        )

    return users


# Get User Information (Only User)
@router.get(
    "/{user_id}",
    response_model=UserDisplay,
)
def get_user(
    response: Response,
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Retrieves information for a specific user. Users can only access their
    own information.

    Parameters:
    - response (Response): The FastAPI response object.
    - user_id (int): The ID of the user to retrieve.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Raises:
    - HTTPException: 401 Unauthorized if the requester is not the user or
        an admin.

    Returns:
    - UserDisplay: The requested user's information.
    """

    payload = oauth2.decode_access_token(token=token)
    user = check_user(db=db, user_id=user_id)

    if payload.get("user_id") == user.id:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTHENTICATION_TEXT,
        )


@router.get("/{user_id}/reviews")
def get_all_user_reviews(
    user_id=int,
    db: Session = Depends(get_db),
):
    """
    Retrieves all reviews made by a specific user.

    Parameters:
    - user_id (int): The ID of the user whose reviews are to be retrieved.
    - db (Session): Database session for executing database operations.

    Returns:
    - A list of reviews made by the specified user.
    """

    db_reviews = get_all_reviews(db=db)
    user_reviews = []
    for review in db_reviews:
        if review.user_id == int(user_id):
            user_reviews.append(review)

    return user_reviews


# =========================== POST Functions ========================
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserDisplay,
)
def create_user(
    request: UserBase,
    db: Session = Depends(get_db),
):
    """
    Creates a new user in the database.

    Parameters:
    - request (UserBase): The user information to create.
    - db (Session): Database session for executing database operations.

    Raises:
    - HTTPException: 409 Conflict if a user with the same email already exists.

    Returns:
    - UserDisplay: The created user's information.
    """

    if (
        db_users.get_user(
            db=db,
            email=request.email,
        )
        is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {request.email} already exists!",
        )
    new_user = db_users.create_user(
        db=db,
        request=request,
    )
    return new_user


# =============================== PUT Functions ==========================
# Update User Information (Only User)
@router.put(
    "/",
    response_model=UserDisplay,
)
def update_user(
    request: UserUpdate,
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Updates information for a specific user. Users can only update
    their own information.

    Parameters:
    - request (UserUpdate): The new information for the user.
    - user_id (int): The ID of the user to update.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Raises:
    - HTTPException: 401 Unauthorized if the requester is not the user.

    Returns:
    - UserDisplay: The updated user's information.
    """

    payload = oauth2.decode_access_token(token=token)
    user = check_user(db=db, user_id=user_id)

    if payload.get("user_id") == user.id:
        db_users.update_user(
            db=db,
            user=user,
            request=request,
        )
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTHENTICATION_TEXT,
        )


# ============================ PATCH Functions ===========================
# Update User Type Information (Admin User)
@router.patch(
    "/{user_id}",
    response_model=UserTypeDisplay,
)
def update_user_type(
    request: UserTypeUpdate,
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Updates the type for a specific user. This endpoint is restricted
    to admins only.

    Parameters:
    - request (UserTypeUpdate): The new type for the user.
    - user_id (int): The ID of the user whose type is to be updated.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request as an admin.

    Raises:
    - HTTPException: 401 Unauthorized if the requester is not an admin.

    Returns:
    - UserTypeDisplay: The user with updated type information.
    """

    user = check_user(
        db=db,
        user_id=user_id,
    )

    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )
    db_users.update_user_type(
        db=db,
        user=user,
        request=request,
    )

    return user


# ============================ DELETE Functions ===========================
# Delete User (Only Admins)
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Deletes a specific user from the database. This endpoint is
    restricted to admins only.

    Parameters:
    - user_id (int): The ID of the user to delete.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request as an admin.

    Raises:
    - HTTPException: 401 Unauthorized if the requester is not an admin.

    Returns:
    - A success message indicating the user was deleted successfully.
    """

    payload = oauth2.decode_access_token(token=token)

    user = check_user(
        db=db,
        user_id=user_id,
    )
    if payload.get("user_type") == "admin" and user.id != payload.get("user_id"):
    
        db_users.delete_user(
            db=db,
            user=user,
        )
        return {"message": f"User with id:{user_id} was deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=DELETE_TEXT,
        )
