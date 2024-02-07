from fastapi import HTTPException, Depends, APIRouter, status
from db.database import get_db
from sqlalchemy.orm import Session
from db import db_directors
from typing import List
from schemas import directors_schemas
from auth import oauth2

router = APIRouter(prefix="/directors", tags=["Directors Endpoints"])


# CRUD Operations for Directors
# Create Director
@router.post("/", response_model=directors_schemas.DirectorDisplay)
def create_director(
    director: directors_schemas.DirectorBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create a director",
        )
    else:
        return db_directors.create_director(db, director)
    
# Get Director By Id
@router.get("/{director_id}", response_model=directors_schemas.DirectorDisplay)
def read_director_by_id(director_id: int, db: Session = Depends(get_db)):
    director = db_directors.get_director(db, director_id)
    if director :
        return director
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Director with id {director_id} not found",
        )

# Get All Directors
@router.get("/", response_model=List[directors_schemas.DirectorDisplay])
def read_all_directors(db: Session = Depends(get_db)):
    return db_directors.get_all_directors(db)

# Update Director
@router.put("/{director_id}", response_model=directors_schemas.DirectorDisplay)
def update_director(
    director_id: int,
    request: directors_schemas.DirectorBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to update a director",
        )
    else:
        director = db_directors.get_director(db, director_id)
        if director is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Director with id {director_id} not found",
            )
        else:
            return db_directors.update_director(db, director_id, request)
    
# Delete Director
@router.delete("/{director_id}")
def delete_director(
    director_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete a director",
        )
    else:
        director = db_directors.get_director(db, director_id)
        if director is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Director with id {director_id} not found",
            )
        else:
            movies = db_directors.check_director_in_movie(db, director_id)
            if movies:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Director is associated with movies and cannot be deleted",
                )
            else:
                return db_directors.delete_director(db, director_id)
        
