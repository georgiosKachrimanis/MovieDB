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
@router.post(
    "/",
    response_model=directors_schemas.DirectorDisplay,
    status_code=status.HTTP_201_CREATED,
)
def create_director(
    request: directors_schemas.DirectorBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    if oauth2.admin_authentication(token=token):
        return db_directors.create_director(db, request)


# Get Director By Id
@router.get("/{director_id}", response_model=directors_schemas.DirectorDisplay)
def get_director_by_id(director_id: int, db: Session = Depends(get_db)):
    director = db_directors.get_director(db, director_id)
    if director:
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
    if oauth2.admin_authentication(token=token):
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
    if oauth2.admin_authentication(token=token):
        director = db_directors.get_director(db, director_id)
        if director is None:
            raise HTTPException(
                status_code=404, detail=f"Director with id {director_id} not found"
            )
        else:
            if db_directors.check_director_in_movies(db, director_id):
                db_directors.delete_director(db, director_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Director is associated with movies and cannot be deleted",
                )
            return f"Director with id: {director_id} deleted successfully"


# Add Sample Data to Directors
@router.post("/auto_add_directors", status_code=status.HTTP_201_CREATED)
def auto_add_directors(db: Session = Depends(get_db)):
    """
    THIS IS ONLY TO BE USED FOR TESTING PURPOSES
    """
    import json

    with open("sampleData/example_directors.json", "r") as file:
        directors = json.load(file)

    for director in directors:
        db_directors.create_director(
            db=db, request=directors_schemas.DirectorBase(**director)
        )
    return {"message": "Directors added successfully"}
