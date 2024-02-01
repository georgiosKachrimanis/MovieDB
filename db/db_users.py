from sqlalchemy.orm.session import Session
from schemas.users_schemas import (
    UserBase,
    UserUpdate,
    UserTypeUpdate,
)
from db.models import DbUser
from db.hash import Hash


def create_user(db: Session, request: UserBase):
    new_user = DbUser(
        username=request.username,
        email=request.email,
        password=Hash.bcrypt(request.password),
        user_type="user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_all_users(db: Session):
    return db.query(DbUser).all()


def get_user(db: Session, id: int = None, email: str = None):
    if id is not None:
        return db.query(DbUser).filter(DbUser.id == id).first()
    elif email is not None:
        return db.query(DbUser).filter(DbUser.email == email).first()
    else:
        return None


<<<<<<< HEAD:db/db_users.py
=======
# Maybe we should create 2 types of update.
# One for the user to update his email/password and,
# another for Admins to update the role!
>>>>>>> main:db/db_user.py
def update_user(db: Session, id: int, request: UserUpdate):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    if user is None:
        return None
    else:
        user.username = request.username
        user.email = request.email
        user.password = Hash.bcrypt(request.password)
<<<<<<< HEAD:db/db_users.py
        db.commit()
        return user
=======
>>>>>>> main:db/db_user.py


def update_user_type(db: Session, id: int, request: UserTypeUpdate):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    if user is None:
        return None
    else:
        user.user_type = request.user_type  # request.user_type
        db.commit()
        return user


def delete_user(db: Session, id: int):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    db.delete(user)
    db.commit()
    return user
