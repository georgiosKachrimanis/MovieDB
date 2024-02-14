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
from schemas.users_reviews_schemas import (
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


def check_user(
    db: Session,
    user_id: int,
):

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

    payload = oauth2.decode_access_token(token=token)
    user = check_user(
        db=db,
        user_id=user_id,
    )
    if payload.get("user_type") == "admin" and user:
        db_users.delete_user(
            db=db,
            user=user,
        )
        return {"message": f"User with id:{user_id} was deleted successfully"}
