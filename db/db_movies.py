from typing import List
from sqlalchemy.orm import Session
from db.models import Movie, Review, Category, Actor,Director
from sqlalchemy import func
from schemas import movies_schemas


# Create Movie
def create_movie(db: Session, movie: movies_schemas.MovieBase):
    categories = db.query(Category).filter(Category.id.in_(movie.categories)).all()

    new_movie = Movie(
        title=movie.title,
        released_date=movie.released_date,
        categories=categories,
        director_id=movie.director_id,
        actors=db.query(Actor).filter(Actor.id.in_(movie.actors)).all(),
        plot=movie.plot,
        poster_url=movie.poster_url,
        imdb_rate=movie.imdb_rate,
    )

    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

# Get All Movies
def get_all_movies(db: Session, skip: int = 0, limit: int = 100):
    movies = db.query(Movie).all()
    for movie in movies:
        movie.review_count = (
            db.query(func.count(Review.id)).filter(Review.movie_id == movie.id).scalar()
        )
        movie.average_movie_rate = (
            db.query(func.avg(Review.movie_rate))
            .filter(Review.movie_id == movie.id)
            .scalar()
        )
        movie.director_name = db.query(Director.director_name).filter(Director.id == movie.director_id).scalar()
    return movies

# Get Movie By Id
def get_movie(db: Session, movie_id: int):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    movie.average_movie_rate = (
        db.query(func.avg(Review.movie_rate))
        .filter(Review.movie_id == movie.id)
        .scalar()
    )
    return movie

# Update Movie
def update_movie(db: Session, movie_id: int, request: movies_schemas.MovieUpdate):
    movie = get_movie(db, movie_id)
    if movie:
        categories = [category.id for category in movie.categories]
        actors = [actor.id for actor in movie.actors]
        for key, value in request.__dict__.items():
            if key == "categories":
                categories = db.query(Category).filter(Category.id.in_(value)).all()
            else:
                setattr(movie, key, value)
        for key, value in request.__dict__.items():
            if key == "actors":
                actors = db.query(Actor).filter(Actor.id.in_(value)).all()
            else:
                setattr(movie, key, value)        
        movie.actors = actors
        db.commit()
        db.refresh(movie)
        return movie
    return None

# Delete Movie
def delete_movie(db: Session, movie_id: int) -> bool:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        db.delete(movie)
        db.commit()
        return True
    return False

# Check if movie is in any review
def check_movie_in_reviews(db: Session, movie_id: int):
    return db.query(Movie).filter(Movie.id == movie_id).first().reviews != []

