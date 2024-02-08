from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db.models import DbDirector
from schemas.movies_directors_schemas import Director


# Create Director
def create_director(
    db: Session,
    request: Director,
):
    new_director = DbDirector(director_name=request.director_name)
    db.add(new_director)
    db.commit()
    db.refresh(new_director)
    return new_director


# Get director By Id
def get_director(db: Session, director_id: int):
    return db.query(DbDirector).filter(DbDirector.id == director_id).first()


# Get All Directors
def get_all_directors(
    db: Session,
    skip: int = 0,
    limit: int = 100,
):
    return db.query(DbDirector).offset(skip).limit(limit).all()


# Update Director
def update_director(
    db: Session,
    director_id: int,
    request: Director,
):
    director = get_director(db, director_id)
    director.director_name = request.director_name
    db.commit()
    db.refresh(director)
    return director


# Delete Director
def delete_director(
    db: Session,
    director_id: int,
):
    director = get_director(db, director_id)
    if director:
        db.delete(director)
        db.commit()
        return f"Director with id {director_id} deleted successfully"
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Director with id {director_id} not found",
        )


# Check if director is in any movie
def check_director_in_movie(db: Session, director_id: int) -> bool:
    return (
        db.query(DbDirector)
        .filter(DbDirector.id == director_id)
        .first()
        .movies != []
    )
