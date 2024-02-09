from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    HTTPException,
)
from typing import List
from schemas.users_reviews_schemas import (
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

router = APIRouter(
    prefix="/users",
    tags=["Users Endpoints"],
)


def check_user(db: Session, user_id: int):

    user = db_users.get_user(db=db, id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID: {user_id} not found",
        )
    return user


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserDisplay,
)
def create_user(request: UserBase, db: Session = Depends(get_db)):

    if db_users.get_user(db=db, email=request.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {request.email} already exists!",
        )
    new_user = db_users.create_user(db=db, request=request)
    return new_user


# Get all the users(Only Admins)
@router.get(
    "/",
    response_model=List[UserDisplay],
)
def get_users(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

    payload = oauth2.decode_access_token(token=token)
    users = db_users.get_all_users(db=db)
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users table is empty!",
        )
    elif payload.get("user_type") == "admin":
        return users
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


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

    payload = oauth2.decode_access_token(token=token)
    user = check_user(db=db, user_id=user_id)

    if payload.get("user_id") == user.id:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


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

    payload = oauth2.decode_access_token(token=token)
    user = check_user(db=db, user_id=user_id)

    if payload.get("user_id") == user.id:
        db_users.update_user(db=db, id=user_id, request=request)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


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

    payload = oauth2.decode_access_token(token=token)
    user = check_user(db=db, user_id=user_id)

    if payload.get("user_type") == "admin":
        db_users.update_user_type(db=db, id=user_id, request=request)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


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

    payload = oauth2.decode_access_token(token=token)
    user = check_user(db=db, user_id=user_id)
    if payload.get("user_type") == "admin" and user:
        db_users.delete_user(db=db, id=user_id)
        return {"message": f"User with id:{user_id}  was deleted successfully"}
