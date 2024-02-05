from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from auth import oauth2
from db import db_movies
from db.database import get_db
from db.models import DbCategory, DbMovie
from schemas.movies_schemas import (
    MovieBase,
    MovieDisplay,
    MoviePatchUpdate,
    MovieUpdate,
)

router = APIRouter(prefix="/movies", tags=["Movies Endpoints"])


# Create a new movie
@router.post("/", response_model=MovieDisplay)
def create_movie(movie: MovieBase, db: Session = Depends(get_db)):
    if db_movies.get_movie(db=db, movie_title=movie.title):
        raise HTTPException(
            status_code=409,
            detail=f"A movie with the title {movie.title} already exists.",
        )
    return db_movies.create_movie(db, movie)


@router.get("/", response_model=Optional[List[MovieDisplay]])
def get_movies(db: Session = Depends(get_db)):
    movies = db_movies.get_all_movies(db=db)
    if not movies:
        raise HTTPException(
            status_code=404,
            detail="The movies list is empty!",
        )
    return movies


# Get Movie By Id
@router.get("/{movie_id}", response_model=Optional[MovieDisplay])
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    movie = db_movies.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(
            status_code=404, detail=f"Movie with Id: {movie_id} not found"
        )
    return movie


# Update Movie
@router.put("/{movie_id}", response_model=Optional[MovieDisplay])
def update_movie_data(
    movie_id: int,
    movie_updates: MovieUpdate,
    db: Session = Depends(get_db),
):
    movie = db_movies.get_movie(db, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=404, detail="Movie with Id :{movie_id} not found"
        )
    else:
        updated_movie = db_movies.update_movie(
            db=db,
            movie=movie,
            request=movie_updates,
        )

    return updated_movie


# Update some items in the movie
@router.patch("/title/{movie_id}", response_model=Optional[MovieDisplay])
def update_movie_title(
    movie_id: int,
    title: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):

    movie = db_movies.get_movie(db, movie_id)
    if movie:
        db_movies.patch_movie(db=db, movie=movie, title_update=title)
    return movie


@router.patch("/plot/{movie_id}", response_model=Optional[MovieDisplay])
def update_movie_plot(
    movie_id: int,
    plot: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):

    movie = db_movies.get_movie(db, movie_id)
    if movie:
        db_movies.patch_movie(db=db, movie=movie, plot=plot)
    return movie


@router.patch("/poster_url/{movie_id}", response_model=Optional[MovieDisplay])
def update_movie_poster_url(
    movie_id: int,
    poster_url: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):

    movie = db_movies.get_movie(db, movie_id)
    if movie:
        db_movies.patch_movie(db=db, movie=movie, poster_url=poster_url)
    return movie


@router.patch("/categories/{movie_id}", response_model=Optional[MovieDisplay])
def update_movie_categories(
    movie_id: int,
    category_ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    movie = db_movies.get_movie(db, movie_id)
    if movie:
        db_movies.patch_movie(db=db, movie=movie, category_ids=category_ids)
    return movie

@router.delete("/{movie_id}")
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
):
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
    return f"Movie with id: {movie_id} deleted successfully"


# Return Movie Categories
@router.get("/categories/")
def get_movie_categories(db: Session = Depends(get_db)):
    categories = db.query(DbCategory.id, DbCategory.category_name).all()
    return [
        {"id": category.id, "category_name": category.category_name}
        for category in categories
    ]


# Return All Movies of the requested Category
@router.get(
    "/categories/{category_id}",
    response_model=List[MovieDisplay],
)
def get_movies_by_category(category: int, db: Session = Depends(get_db)):
    category_check = db.query(DbCategory).filter(DbCategory.id == category).first()
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
