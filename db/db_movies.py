# from typing import List
from sqlalchemy.orm import Session, joinedload
from db.models import DbMovie, DbReview, DbCategory
from schemas.movies_schemas import (
    MovieBase,
    MovieUpdate,
    MovieDisplayOne,
)
from sqlalchemy import func


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


def get_movie(db: Session, movie_id: int):
    movie = (
        db.query(DbMovie)
        .options(joinedload(DbMovie.categories))
        .filter(DbMovie.id == movie_id)
        .first()
    )

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
