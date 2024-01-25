from typing import List
from db.hash import Hash
from sqlalchemy.orm.session import Session
from schemas import UserBase
from db.models import DbUser


def create_user(db: Session, request: UserBase):
  new_user = DbUser(
    username = request.username,
    email = request.email,
    user_type = request.user_type,
    password = Hash.bcrypt(request.password),
    fav_list = [],
  )
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return new_user

def get_all_users(db: Session):
  return db.query(DbUser).all()

def get_user(db: Session, id: int):
  return db.query(DbUser).filter(DbUser.id == id).first()

def update_user(db: Session, id: int, request: UserBase):
  user = db.query(DbUser).filter(DbUser.id == id).first()
  user.update({
    DbUser.username: request.username,
    DbUser.email: request.email,
    DbUser.user_type : request.user_type,
    DbUser.password: Hash.bcrypt(request.password)
  })
  db.commit()
  return 'User updated successfully'

def delete_user(db:Session, id: int ):
  user = db.query(DbUser).filter(DbUser.id == id).first()
  db.delete(user)
  db.commit()
  return 'User deleted successfully'