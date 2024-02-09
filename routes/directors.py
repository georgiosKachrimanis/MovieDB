from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session
from auth import oauth2
from db import db_directors
from db.database import get_db
from schemas.mov_dir_actors_schemas import (
    Director,
    DirectorDisplay,
    DirectorFullUpdate,
)

router = APIRouter(
    prefix="/directors",
    tags=["Directors Endpoints"],
)

AUTHENTICATION_TEXT = "You are not authorized to add, edit or delete directors"


# CRUD Operations for Directors
# Create Director
@router.post(
    "/",
    response_model=Director,
    status_code=status.HTTP_201_CREATED,
)
def create_director(
    request: Director,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    oauth2.admin_authentication(
        token=token,
        exception_text=AUTHENTICATION_TEXT,
    )

    return db_directors.create_director(
        db=db,
        request=request,
    )


# Get Director By Id
@router.get(
    "/{director_id}",
    response_model=DirectorDisplay,
)
def get_director_by_id(
    director_id: int,
    db: Session = Depends(get_db),
):
    director = db_directors.get_director(
        db=db,
        director_id=director_id,
    )
    if director:
        return director
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Director with id {director_id} not found",
        )


# Get All Directors
@router.get(
    "/",
    response_model=List[DirectorDisplay],
)
def get_all_directors(db: Session = Depends(get_db)):
    return db_directors.get_all_directors(db)


# Update Director
@router.put(
    "/{director_id}",
    response_model=DirectorDisplay,
)
def update_director(
    request: DirectorFullUpdate,
    director: Director = Depends(get_director_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    oauth2.admin_authentication(
        token=token,
        exception_text=AUTHENTICATION_TEXT,
    )

    return db_directors.update_director(
        db=db,
        director=director,
        request=request,
    )


# Delete Director
@router.delete(
    "/{director_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_director(
    director: Director = Depends(get_director_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    oauth2.admin_authentication(
        token=token,
        exception_text=AUTHENTICATION_TEXT,
    )

    movies = db_directors.check_director_in_movie(db, director.id)
    if movies:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Director is associated with movies. Can't be deleted!",
        )
    else:
        return db_directors.delete_director(db, director.id)
