from fastapi import APIRouter,Depends ,HTTPException
from schemas import UserBase, UserDisplayOne,UserDisplayAll,UserUpdate
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_user
from typing import List

router = APIRouter(
    prefix='/user',
    tags=['Users Endpoints']
)

# CRUD Operations

# Create User
@router.post('/add', response_model=UserDisplayOne)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    try:
        new_user = db_user.create_user(db=db, request=request)
        return new_user
    except Exception as e:
        return str(e)


# Read All User With Reviews
@router.get('/', response_model=List[UserDisplayAll])
def get_all_users(db: Session = Depends(get_db)):
  return db_user.get_all_users(db)


# Read User By Id
@router.get('/{user_id}', response_model=UserDisplayOne)
def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db_user.get_user(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User not found with user id: {user_id}")
        else:
            return user 
    except Exception as e:
        raise HTTPException(status_code= e.status_code, detail =  e.detail)

# Update User
@router.put('/update/{user_id}', response_model=UserDisplayOne)
def update_user(user_id: int, request: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = db_user.get_user(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User not found with user id: {user_id}")
        return db_user.update_user(db=db, user_id=user_id, request=request)
    except Exception as e:
        raise HTTPException(status_code= e.status_code, detail =  e.detail)
    

# Delete User
@router.delete('/delete/{user_id}')
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db_user.get_user(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User not found with user id: {user_id}")
        db_user.delete_user(db, user_id)
        return {"message": f"User with Id:{user_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code= e.status_code, detail =  e.detail)