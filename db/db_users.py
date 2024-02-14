from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session

from db.hash import Hash
from db.models import DbReview, DbUser
from schemas.users_reviews_schemas import UserBase, UserTypeUpdate, UserUpdate


# TODO: check if i am passing user/reviews objects and not just ids
def create_user(
    db: Session,
    request: UserBase,
):
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
    users = db.query(DbUser).all()
    for user in users:
        user.review_count = (
            db.query(func.count(DbReview.id))
            .filter(DbReview.user_id == user.id)
            .scalar()
        )
    return users


def get_user(
    db: Session,
    id: int = None,
    email: str = None,
):
    if id is not None:
        return db.query(DbUser).filter(DbUser.id == id).first()
    elif email is not None:
        return db.query(DbUser).filter(DbUser.email == email).first()
    else:
        return None


def update_user(
    db: Session,
    user: DbUser,
    request: UserUpdate,
):

    if user is None:
        return None
    else:
        user.username = request.username
        user.email = request.email
        user.password = Hash.bcrypt(request.password)
        db.commit()
        return user


def update_user_type(
    db: Session,
    user: DbUser,
    request: UserTypeUpdate,
):
    if user:
        user.user_type = request.user_type

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: DbUser):
    db.delete(user)
    db.commit()
    return user


# Get All Users with Reviews
def get_all_users_with_reviews(db: Session):
    return db.query(DbUser).options(joinedload(DbUser.reviews)).all()
