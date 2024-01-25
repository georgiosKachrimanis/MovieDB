from fastapi import APIRouter, Depends
from schemas.users import UserBase, UserDisplay
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_user

router = APIRouter(
    prefix='/user',
    tags=['user']
)

# CRUD Operations
# TODO: Create User


# @router.post('/add', response_model=UserDisplay)
# def create_user(request: UserBase, db: Session = Depends(get_db)):
#     return db_user.create_user(db=db, request=request)

@router.post('/add')
def create_user(request: UserBase):
    name = request.username
    email = request.email
    return {
        "Name": name,
        "email": email
    } 

# TODO: Read User

# TODO: Update User

# TODO: Delete User