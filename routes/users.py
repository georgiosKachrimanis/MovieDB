from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    HTTPException,
)
from typing import Optional, List
from schemas import users_schemas
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_users
from auth import oauth2
from routes.reviews import get_all_reviews

router = APIRouter(prefix="/users", tags=["Users Endpoints"])


#  Check if a user exists in the database by ID or email.
def check_user(db: Session, user_id: int):
    """
    Checks if a user exists in the database by user ID.
    
    Parameters:
    - db: Session - Dependency injection of the database session.
    - user_id: int - The ID of the user to check.
    
    Returns:
    - The user object if found.
    
    Raises:
    - HTTPException: If no user is found with the given ID.
    """
    user = db_users.get_user(db=db, id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID: {user_id} not found",
        )

    return user


# Create User
@router.post("/", response_model=users_schemas.UserDisplayOne)
def create_user(request: users_schemas.UserBase, db: Session = Depends(get_db)):
    """
    Creates a new user in the database.
    
    Parameters:
    - request: users_schemas.UserBase - The user data to create.
    - db: Session - Dependency injection of the database session.
    
    Returns:
    - The created user's details as defined by the UserDisplayOne schema.
    
    Raises:
    - HTTPException: If a user with the given email already exists or if the user type is invalid.
    """
    if db_users.get_user(db=db, email=request.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {request.email} already exists!",
        )
    elif request.user_type not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User type can only be 'admin' or 'user'",
        )
    else:
        new_user = db_users.create_user(db=db, request=request)
        return new_user


# Get all the users
@router.get("/", response_model=List[users_schemas.UserDisplayAll])
def get_all_users(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Retrieves all users from the database.
    
    Requires admin authentication. This endpoint fetches and returns a list of all users.
    
    Parameters:
    - db: Session - Dependency injection of the database session.
    - token: str - The OAuth2 token for admin authentication.
    
    Returns:
    - A list of all users in the database.
    
    Raises:
    - HTTPException: If the user is not logged in or not authorized to view this information.
    """
    try:
        payload = oauth2.decode_access_token(token=token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="You need to log in to view this information!",
        ) from e
    else:
        users = db_users.get_all_users(db=db)
        if users is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Users table is empty!",
            )
        elif payload.get("user_type") == "admin":
            return users
        else:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to view this information!",
        )


# Get User Information by ID
@router.get("/{user_id}", response_model=users_schemas.UserDisplayOne)
def get_user_by_id(
    response: Response,
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    try:
        payload = oauth2.decode_access_token(token=token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="You need to log in to view this information!",
        ) from e
    else:
        user = check_user(db=db, user_id=user_id)
        if payload.get("user_id") == user.id:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to view this information!",
            )


# Update User Information (Only User)
@router.put("/{user_id}", response_model=users_schemas.UserDisplayOne)
def update_user(
    request: users_schemas.UserUpdate,
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Updates user information for the logged-in user.
    
    Requires user authentication. This endpoint allows users to update their own information.
    
    Parameters:
    - request: users_schemas.UserUpdate - The updated user data.
    - user_id: int - The ID of the user to update.
    - db: Session - Dependency injection of the database session.
    - token: str - The OAuth2 token for user authentication.
    
    Returns:
    - The updated user's details as defined by the UserDisplayOne schema.
    
    Raises:
    - HTTPException: If the user is not logged in, not authorized to update the information, or the user does not exist.
    """
    try:
        payload = oauth2.decode_access_token(token=token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="You need to log in to create a user!",
        ) from e
    else:
        user = check_user(db=db, user_id=user_id)
        if payload.get("user_id") == user.id:
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID: {user_id} not found",
                )
            db_users.update_user(db=db, user_id=user_id, request=request)
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to view this information!",
            )


# Update User Type Information (Admin User)
@router.patch("/{user_id}", response_model=users_schemas.UserTypeDisplay)
def update_user_type(
    request: users_schemas.UserTypeUpdate,
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Updates the user type of a specific user.
    
    Requires admin authentication. This endpoint allows admins to change the user type of other users.
    
    Parameters:
    - request: users_schemas.UserTypeUpdate - The new user type data.
    - user_id: int - The ID of the user whose type is to be updated.
    - db: Session - Dependency injection of the database session.
    - token: str - The OAuth2 token for admin authentication.
    
    Returns:
    - The user's updated type details as defined by the UserTypeDisplay schema.
    
    Raises:
    - HTTPException: If the admin is not logged in, not authorized to update the information, or the user does not exist.
    """
    try:
        payload = oauth2.decode_access_token(token=token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="You need to log in to update !",
        ) from e
    else:
        user = check_user(db=db, user_id=user_id)
        if payload.get("user_type") == "admin":
            db_users.update_user_type(db=db, id=user_id, request=request)
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to update this information!",
            )


# Delete User (Only Admins)
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Deletes a user from the database.
    
    Requires admin authentication. This endpoint allows admins to delete users.
    
    Parameters:
    - user_id: int - The ID of the user to delete.
    - db: Session - Dependency injection of the database session.
    - token: str - The OAuth2 token for admin authentication.
    
    Returns:
    - A success message indicating the user was deleted successfully.
    
    Raises:
    - HTTPException: If the admin is not logged in, not authorized to delete the user, or the user does not exist.
    """
    try:
        payload = oauth2.decode_access_token(token=token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="You need to log in to update !",
        ) from e
    else:
        if payload.get("user_id") == user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You can not delete your own account!",
            )
        user = check_user(db=db, user_id=user_id)
        if payload.get("user_type") == "admin" and user:
            db_users.delete_user(db=db, id=user_id)
            return {"message": f"User with id:{user_id}  was deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to delete this information!",
            )

