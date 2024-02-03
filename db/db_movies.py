from typing import List

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from routes.categories import validate_category
from db.models import DbCategory, DbMovie, DbReview
from schemas.movies_schemas import (
    MovieBase,
    MovieCategoryType,
    MovieDisplayOne,
    MovieUpdate,
)


def create_movie(db: Session, request: MovieBase):
    categories = (
        db.query(DbCategory).filter(DbCategory.id.in_(request.categories)).all()
    )

    new_movie = DbMovie(
        title=request.title,
        released_date=request.released_date,
        categories=categories,
        plot=request.plot,
        poster_url=request.poster_url,
        imdb_rate=request.imdb_rate,
    )
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)

    movie_display = get_movie(db=db, movie_id=new_movie.id)
    return movie_display


def get_all_movies(db: Session, skip: int = 0, limit: int = 100):
    movies = db.query(DbMovie).all()
    for movie in movies:
        movie.review_count = (
            db.query(func.count(DbReview.id))
            .filter(DbReview.movie_id == movie.id)
            .scalar()
        )
        movie.average_movie_rate = (
            db.query(func.avg(DbReview.movie_rate))
            .filter(DbReview.movie_id == movie.id)
            .scalar()
        )
    return movies


def get_movie(db: Session, movie_id: int = None, movie_title: str = None):
    if movie_id is not None:
        movie = (
            db.query(DbMovie)
            .options(joinedload(DbMovie.categories))
            .filter(DbMovie.id == movie_id)
            .first()
        )
    elif movie_title is not None:
        movie = (
            db.query(DbMovie)
            .options(joinedload(DbMovie.categories))
            .filter(DbMovie.title == movie_title)
            .first()
        )
    # We can raise an exception here but maybe is better to just have a fun
    # function if you do not provide a search parameter!
    return movie

    # movie.average_movie_rate = (
    #     db.query(func.avg(DbReview.movie_rate))
    #     .filter(DbReview.movie_id == movie.id)
    #     .scalar()
    # )
    return movie


def update_movie(db: Session, movie_id: int, request: MovieUpdate):
    movie = get_movie(db, movie_id)
    if movie:
        categories = [category.id for category in movie.categories]
        for key, value in request.__dict__.items():
            if key == "categories":
                categories = db.query(DbCategory).filter(DbCategory.id.in_(value)).all()
            else:
                setattr(movie, key, value)
        movie.categories = categories
        db.commit()
        db.refresh(movie)
        return movie
    return None


def delete_movie(db: Session, movie_id: int) -> bool:
    movie = db.query(DbMovie).filter(DbMovie.id == movie_id).first()
    if movie:
        db.delete(movie)
        db.commit()
        return "Movie with id: {movie_id} deleted successfully"
    return False


def get_movie_reviews(db: Session, movie_id: int):
    return db.query(DbReview).filter(DbReview.movie_id == movie_id).all()


def get_movies_by_category(category: MovieCategoryType, db: Session):
    category = (
        db.query(DbCategory).filter(DbCategory.category_name == category.label).first()
    )
    print(category)
    if not category:
        raise HTTPException(
            status_code=404, detail=f"Category {category.label} not found"
        )

    movies = (
        db.query(DbMovie)
        .join(DbMovie.categories)
        .filter(DbCategory.id == category.id)
        .all()
    )
    if not movies:
        raise HTTPException(
            status_code=404,
            detail=f"No movies found for category {category.label}",
        )

    return movies
