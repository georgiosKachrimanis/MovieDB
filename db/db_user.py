from sqlalchemy.orm.session import Session
from schemas.user_schemas import UserBase, UserUpdate
from db.models import DbUser
from db.hash import Hash


def create_user(db: Session, request: UserBase):
    new_user = DbUser(
        username=request.username,
        email=request.email,
        password=Hash.bcrypt(request.password),
        user_type="user"  # We should maybe start here with a Null value and then populate by the table.
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


# Maybe we should create 2 types of update.
# One for the user to update his email/password and,
# another for Admins to update the role!
def update_user(db: Session, id: int, request: UserUpdate):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    if user is None:
        return None
    else:
        user.username = request.username
        user.email = request.email
        user.user_type: request.user_type
        user.password = Hash.bcrypt(request.password)

        db.commit()
        return user


def delete_user(db: Session, id: int):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    db.delete(user)
    db.commit()
    return user
