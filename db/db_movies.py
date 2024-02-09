from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.functions import coalesce
from db.models import (
    DbCategory,
    DbDirector,
    DbMovie,
    DbReview,
    DbActor
)
from routes.directors import get_director_by_id
from schemas.mov_dir_actors_schemas import (
    MovieBase,
    MoviePatchUpdate,
    MovieUpdate,
)


# TODO: Optimize the code, remove same code
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
    movies = db.query(DbMovie).all()
    for movie in movies:
        movie.average_movie_rate = calculate_average(db=db, movie=movie)
        movie.reviews_count = (
            db.query(func.count(DbReview.id))
            .filter(DbReview.movie_id == movie.id)
            .scalar()
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
        movie.average_movie_rate = calculate_average(db=db, movie=movie)

    return movie


# Maybe I should use a different type of update.
def patch_movie(
    db: Session,
    movie: MovieBase,
    request: MoviePatchUpdate,
):

    if request.title:

        movie.title = request.title
    if request.plot:
        movie.plot = request.plot
    if request.poster_url:
        movie.poster_url = request.poster_url
    if request.categories:
        categories = (
            db.query(DbCategory).filter(DbCategory.id.in_(request.categories)).all()
        )
        movie.categories = categories
    if request.director_id:
        movie.director_id = check_director(request.director_id, db=db)
    db.commit()
    db.refresh(movie)
    return movie


def update_movie(
    db: Session,
    movie: DbMovie,
    request: MovieUpdate,
):

    categories = [category.id for category in movie.categories]
    check_director(request.director_id, db=db)
    for key, value in request.__dict__.items():
        if key == "categories":
            categories = db.query(DbCategory).filter(DbCategory.id.in_(value)).all()
        else:
            setattr(movie, key, value)
    movie.categories = categories
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
