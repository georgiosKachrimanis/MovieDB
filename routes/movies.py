from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from auth import oauth2
from db import db_movies
from db.database import get_db
from db.models import (
    DbMovie,
    DbCategory,
)
from schemas.movies_schemas import (
    MovieBase,
    MovieCategoryType,
    MovieDisplayAll,
    MovieDisplayOne,
    MovieTestDisplay,
    MovieUpdate,
)

router = APIRouter(prefix="/movies", tags=["Movies Endpoints"])


# Create a new movie
@router.post("/", response_model=MovieDisplayOne)
def create_movie(movie: MovieBase, db: Session = Depends(get_db)):
    if db_movies.get_movie(db=db, movie_title=movie.title):
        raise HTTPException(
            status_code=409,
            detail=f"A movie with the title {movie.title} already exists.",
        )
    return db_movies.create_movie(db, movie)


# Get Movie By Title
# @router.get("/", response_model=Optional[MovieDisplayOne])
# def get_movie_by_title(
#     movie_title: Optional[str] = None,
#     db: Session = Depends(get_db),
# ):
#     if movie_title:
#         movie = db_movies.get_movie(db=db, movie_title=movie_title)
#         if movie is None:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Movie named: {movie_title} not found",
#             )
#         return movie

#     raise HTTPException(status_code=400, detail="Movie title is required")


@router.get("/", response_model=Optional[List[MovieDisplayOne]])
def get_movies(db: Session = Depends(get_db)):
    movies = db_movies.get_all_movies(db=db)
    if not movies:
        raise HTTPException(
            status_code=404,
            detail="The movies list is empty!",
        )
    return movies


# Get Movie By Id
@router.get("/{movie_id}", response_model=Optional[MovieDisplayOne])
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    movie = db_movies.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(
            status_code=404, detail=f"Movie with Id: {movie_id} not found"
        )
    return movie


@router.delete("/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    reviews = db_movies.get_movie_reviews(db, movie_id)
    if reviews:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete movie with Id: {movie_id}, it has review/s",
        )
    success = db_movies.delete_movie(db, movie_id)
    if not success:
        raise HTTPException(
            status_code=404, detail=f"Movie with Id :{movie_id} not found"
        )
    return f'Movie with id: {movie_id} deleted successfully'


# Return Movie Categories
@router.get("/categories/")
def get_movie_categories(db: Session = Depends(get_db)):
    categories = db.query(DbCategory.category_name).all()
    return [category.category_name for category in categories]


# Return All Movies of the requested Category
@router.get(
    "/categories/{category_label}",
    response_model=List[MovieDisplayOne],
)
def get_movies_by_category(category: str, db: Session = Depends(get_db)):
    category_check = (
        db.query(DbCategory)
        .filter(DbCategory.category_name == category.capitalize())
        .first()
    )
    if not category_check:
        raise HTTPException(
            status_code=404,
            detail=f"Category {category} not found",
        )
    movies = db_movies.get_movies_by_category(
        category=category_check,
        db=db,
    )
    if not movies:
        raise HTTPException(
            status_code=404,
            detail=f"No movies found in category {category.capitalize()}",
        )

    return movies
