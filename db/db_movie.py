from typing import List
from sqlalchemy.orm import Session
from .models import Movie , Review,Category
from schemas import MovieBase, MovieUpdate
from sqlalchemy import func


def create_movie(db: Session, movie: MovieBase):
    categories = db.query(Category).filter(Category.id.in_(movie.categories)).all()
    
    new_movie = Movie(
        title=movie.title,
        released_date=movie.released_date,
        categories=categories,
        plot=movie.plot,
        poster_url=movie.poster_url,
        imdb_rate=movie.imdb_rate
    )
    
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

def get_all_movies(db: Session, skip: int = 0, limit: int = 100):
    movies = db.query(Movie).all()
    for movie in movies:
        movie.review_count = db.query(func.count(Review.id)).filter(Review.movie_id == movie.id).scalar()
        movie.average_movie_rate = db.query(func.avg(Review.movie_rate)).filter(Review.movie_id == movie.id).scalar()
    return movies

def get_movie(db: Session, movie_id: int) :
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    movie.average_movie_rate = db.query(func.avg(Review.movie_rate)).filter(Review.movie_id == movie.id).scalar()
    return movie

def update_movie(db: Session, movie_id: int, request: MovieUpdate):
    movie = get_movie(db, movie_id)
    if movie:
        categories = [category.id for category in movie.categories]
        for key, value in request.__dict__.items():
            if key == "categories":
                categories = db.query(Category).filter(Category.id.in_(value)).all()
            else:
                setattr(movie, key, value)
        movie.categories = categories
        db.commit()
        db.refresh(movie)
        return movie
    return None


def delete_movie(db: Session, movie_id: int) -> bool:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        db.delete(movie)
        db.commit()
        return True
    return False


def get_movie_reviews(db: Session, movie_id: int):
    return db.query(Review).filter(Review.movie_id == movie_id).all()

