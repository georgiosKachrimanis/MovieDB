from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import (
    Session,
    joinedload,
)
from sqlalchemy.sql.functions import coalesce
from db.models import (
    DbCategory,
    DbDirector,
    DbMovie,
    DbReview,
    DbActor,
    DbMovieRequest,
)
from routes.directors import get_director_by_id
from services.movie_service import get_movie_extra_data
from schemas.movies_schemas import (
    MovieBase,
    MoviePatchUpdate,
    MovieUpdate,
)


def check_director(
    director_id: int,
    db: Session,
):
    return get_director_by_id(
        director_id=director_id,
        db=db,
    ).id


def create_movie(
    db: Session,
    request: MovieBase,
):

    new_movie = DbMovie(
        title=request.title,
        released_date=request.released_date,
        categories=get_movie_categories(db=db, request=request),
        plot=request.plot,
        poster_url=request.poster_url,
        imdb_id=request.imdb_id,
        actors=db.query(DbActor).filter(DbActor.id.in_(request.actors)).all(),
        director_id=check_director(
            director_id=request.director_id,
            db=db,
        ),
    )
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)

    return new_movie


def get_all_movies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
):
    movies = db.query(DbMovie).filter(DbMovie.movie_active).all()
    for movie in movies:
        movie.average_movie_rate = calculate_average(
            db=db,
            movie=movie,
        )
        movie.reviews_count = calculate_reviews(
            db=db,
            movie=movie,
        )
        movie.director_name = (
            db.query(DbDirector.director_name)
            .filter(DbDirector.id == movie.director_id)
            .first()
        )
    return movies


def get_movie(
    db: Session,
    movie_id: int = None,
    movie_title: str = None,
    user_id: int = None,
):
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

    if movie:
        movie.reviews_count = calculate_reviews(
            db=db,
            movie=movie,
        )
        movie.average_movie_rate = calculate_average(
            db=db,
            movie=movie,
        )

        movie.requests_count += 1

        create_request_log(
            db=db,
            movie_id=movie.id,
            user_id=user_id,
        )
        db.commit()
        db.refresh(movie)
    return movie


# Maybe I should use a different type of update.
def patch_movie(
    db: Session,
    movie: MovieBase,
    request: MoviePatchUpdate,
):
    if getattr(request, "title", None) is not None:
        movie.title = request.title
    if getattr(request, "plot", None) is not None:
        movie.plot = request.plot
    if getattr(request, "poster_url", None) is not None:
        movie.poster_url = request.poster_url
    if getattr(request, "categories", None) is not None:
        movie.categories = get_movie_categories(
            db=db,
            request=request,
        )
    if getattr(request, "director_id", None) is not None:
        movie.director_id = check_director(
            director_id=request.director_id,
            db=db,
        )
    if getattr(request, "imdb_id", None) is not None:
        movie.imdb_id = request.imdb_id
    if getattr(request, "actors", None) is not None:
        actors = db.query(DbActor).filter(DbActor.id.in_(request.actors)).all()
        movie.actors = actors
    db.commit()
    db.refresh(movie)
    return movie


def update_movie(
    db: Session,
    movie: DbMovie,
    request: MovieUpdate,
):

    check_director(
        request.director_id,
        db=db,
    )

    if "categories" in request.__dict__:
        categories = get_movie_categories(
            db=db,
            request=request,
        )
        movie.categories = categories
    if "actors" in request.__dict__:
        actors = db.query(DbActor).filter(DbActor.id.in_(request.actors)).all()
        movie.actors = actors

    for key, value in request.__dict__.items():
        if key not in ["categories", "actors"]:
            setattr(movie, key, value)

    db.commit()
    db.refresh(movie)
    return movie


def delete_movie(
    db: Session,
    movie_id: int,
):
    movie = db.query(DbMovie).filter(DbMovie.id == movie_id).first()
    if not movie:
        return False
    db.delete(movie)
    db.commit()
    return True


def get_movie_reviews(
    db: Session,
    movie_id: int,
):
    return db.query(DbReview).filter(DbReview.movie_id == movie_id).all()


def get_movies_by_category(
    category: int,
    db: Session,
):
    movies = (
        db.query(DbMovie)
        .join(DbMovie.categories)
        .filter(DbCategory.id == category.id)
        .all()
    )

    return movies


def calculate_average(
    movie: DbMovie,
    db: Session,
):
    average_rate = (
        db.query(coalesce(func.avg(DbReview.user_rating), 0))
        .filter(DbReview.movie_id == movie.id)
        .scalar()
    )
    return average_rate


def calculate_reviews(
    movie: DbMovie,
    db: Session,
):
    review_count = (
        db.query(func.count(DbReview.id)).filter(DbReview.movie_id == movie.id).scalar()
    )
    return review_count


def update_movie_poster_url(
    db: Session,
    movie: DbMovie,
    file_path: str,
):
    if movie:
        movie.poster_url = file_path
        db.commit()
        db.refresh(movie)
        return movie


def get_movie_categories(
    db: Session,
    request: MovieBase,
):
    return db.query(DbCategory).filter(DbCategory.id.in_(request.categories)).all()


def create_request_log(
    db: Session,
    movie_id: int,
    user_id: int,
):
    request = DbMovieRequest(
        movie_id=movie_id,
        user_id=int(user_id),
        request_time=datetime.now(),
    )

    db.add(request)
    db.commit()
    db.refresh(request)
    return True


def get_movie_extra(
    movie: DbMovie,
):
    if movie.imdb_id is None:
        return "No imdb_id stored in the DB for this movie."
    else:
        return get_movie_extra_data(movie.imdb_id)
