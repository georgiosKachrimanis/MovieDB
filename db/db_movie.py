from sqlalchemy.orm import Session
from .models import Movie , Review 
from schemas import MovieBase, MovieUpdate
from sqlalchemy import func

def create_movie(db: Session, request: MovieBase):
    new_movie = Movie(
        title=request.title,
        released_date=request.released_date,
        categories=request.categories,
        plot=request.plot,
        poster_url=request.poster_url,
        imdb_rate=request.imdb_rate
    )
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

def get_all_movies(db: Session, skip: int = 0):
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
        for key, value in request.dict(exclude_unset=True).items():
            setattr(movie, key, value)
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

