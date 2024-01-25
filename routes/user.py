from fastapi import APIRouter, Depends, Response, status
from typing import Optional
from schemas.user_schemas import UserBase, UserDisplay
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_user

router = APIRouter(prefix="/user", tags=["user"])


def get_user_from_db(id: int) -> Optional[UserDisplay]:
    print("get_user_id")
    if id == 5:
        return UserDisplay(
            username="johndoe", email="john@example.com", user_type="admin"
        )
    else:
        return None


# @router.post('/add', response_model=UserDisplay)
# def create_user(request: UserBase, db: Session = Depends(get_db)):
#     return db_user.create_user(db=db, request=request)


@router.post("/add", response_model=UserDisplay)
def create_user(request: UserBase, db: Session = Depends(get_db)):

    return db_user.create_user(db=db, request=request)


# TODO: Read User
@router.get("/{id}", status_code=status.HTTP_202_ACCEPTED)
def get_user(
    id: int, response: Response
):  # <---- Declare type otherwise you will get issues!!d
    user = get_user_from_db(id)
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"User with {id} not found!"}
    else:
        response.status_code = status.HTTP_200_OK
        return user


# TODO: Update User

# TODO: Delete User
