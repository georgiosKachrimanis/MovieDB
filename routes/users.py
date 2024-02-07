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

router = APIRouter(prefix="/users", tags=["Users Endpoints"])

#  Check if a user exists in the database by ID or email.
def check_user(db: Session, user_id: int):
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
    if db_users.get_user(db=db, email=request.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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


# Get all the users(Only Admins)
@router.get("/", response_model=List[users_schemas.UserDisplayAll])
def read_all_users(
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
@router.get("/{user_id}", response_model=users_schemas.UserDisplayOne)
def read_user_by_id(
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
@router.put("/{user_id}", response_model=users_schemas.UserDisplayOne)
def update_user(
    request: users_schemas.UserUpdate,
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    user = check_user(db=db, user_id=user_id)
    if payload.get("user_id") == user.id:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID: {user_id} not found",
            )
        db_users.update_user(db=db,user_id=user_id, request=request)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


# Update User Type Information (Admin User)
@router.patch("/{user_id}", response_model=users_schemas.UserTypeDisplay)
def update_user_type(
    request: users_schemas.UserTypeUpdate,
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
@router.delete("/{user_id}")
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
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
