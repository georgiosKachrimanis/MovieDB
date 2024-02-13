from typing import List
from sqlalchemy.orm import Session
from db.models import Movie, Review, Category, Actor, Director
from sqlalchemy import func,and_
from schemas import movies_schemas
from services.movie_service import get_movie_extra_data
from db.db_directors import get_director
from datetime import datetime
from db.models import MovieRequest



def check_director(
    director_id: int,
    db: Session,
):
    return get_director(
        director_id=director_id,
        db=db,
    ).id

def check_movie(db,movie_id: int,) -> bool:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        return True
    return False

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
        imdb_id=movie.imdb_id,
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
        movie.director_name = (
            db.query(Director.director_name)
            .filter(Director.id == movie.director_id)
            .scalar()
        )
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

# Patch (update partially) movie
def patch_movie(
    db: Session,
    movie: movies_schemas.MovieBase,
    request: movies_schemas.MoviePatchUpdate,
):
    if getattr(request, 'title', None) is not None:
        movie.title = request.title
    if getattr(request, 'plot', None) is not None:
        movie.plot = request.plot
    if getattr(request, 'poster_url', None) is not None:
        movie.poster_url = request.poster_url
    if getattr(request, 'categories', None) is not None:
        categories = db.query(Category).filter(Category.id.in_(request.categories)).all()
        movie.categories = categories
    if getattr(request, 'director_id', None) is not None:
        movie.director_id = check_director(director_id=request.director_id, db=db,)
    if getattr(request, 'actors', None) is not None:
        actors = db.query(Actor).filter(Actor.id.in_(request.actors)).all()
        movie.actors = actors
    if getattr(request, 'imdb_id', None) is not None:
        movie.imdb_id = request.imdb_id
    if getattr(request, 'number_of_request', None) is not None:
        movie.number_of_request = request.number_of_request
    db.commit()
    db.refresh(movie)
    return movie

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


from sqlalchemy.orm import Session
from .models import Movie


def update_movie_poster_url(db: Session, movie, file_path: str):
    if movie:
        movie.poster_url = file_path
        db.commit()
        db.refresh(movie)
        return True


# Get Movie Extra Data
def get_movie_extra(db: Session, movie_id):
    movie = get_movie(db, movie_id)
    if movie.imdb_id is None:
        return "No imdb_id found for this movie."
    else:
        imdb_id = movie.imdb_id
        result = get_movie_extra_data(imdb_id)
        return result

# Movie request loggers
def create_request_log(
        db: Session, 
        movie_id: int,
        ):
    request = MovieRequest(
        movie_id=movie_id,
        request_time=datetime.now(),
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

# Get Movie Request Count
def get_movie_request_count(db: Session, start_date: datetime = None, end_date: datetime = None):
    all_movies = db.query(Movie).all()
    movie_request_count = []
    for movie in all_movies:
        query = db.query(MovieRequest).filter(MovieRequest.movie_id == movie.id)
        if start_date:
            query = query.filter(MovieRequest.request_time >= start_date)
        if end_date:
            query = query.filter(MovieRequest.request_time <= end_date)
        request_count = query.count()
        movie_request_count.append(
            {
                "movie_id": movie.id,
                "movie_title": movie.title,
                "request_count": request_count,
            }
        )
    return movie_request_count