from db.hash import Hash
from sqlalchemy.orm.session import Session 
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from schemas import  UserUpdate, UserBase
from db.models import User , Review


# Create User
def create_user(db: Session, request: UserBase):
  new_user = User(
      username = request.username,
      email = request.email,
      user_type = request.user_type,
      created_at = request.created_at,
      password = Hash.bcrypt(request.password),
    )
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return new_user

# Get All Users
def get_all_users(db: Session):
    users = db.query(User).all()
    for user in users:
        user.review_count = db.query(func.count(Review.id)).filter(Review.user_id == user.id).scalar()
    return users
  

# Get All Users with Reviews
def get_all_users_with_reviews(db: Session):
    return db.query(User).options(joinedload(User.reviews)).all()

# Get User By Id
def get_user(db: Session, id: int):
  return db.query(User).filter(User.id == id).first()

# Update User
def update_user(db: Session, user_id: int, request: UserUpdate):
  user = get_user(db, user_id)
  for field, value in request.dict(exclude_unset=True).items():
    if field == 'password' and value is not None:
      value = Hash.bcrypt(value)
    setattr(user, field, value)
  db.commit()
  db.refresh(user)
  return user


# Delete User
def delete_user(db:Session, id: int ):
  user = db.query(User).filter(User.id == id).first()
  db.delete(user)
  db.commit()
  return 'User deleted successfully'