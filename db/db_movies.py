from sqlalchemy import func
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.orm import (
    Session,
    joinedload,
)
from db.models import (
    DbCategory,
    DbMovie,
    DbReview,
)
from schemas.movies_schemas import MovieBase, MovieUpdate, MoviePatchUpdate


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
        movie.average_movie_rate = calculate_average(db=db, movie=movie)
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

    if movie:
        movie.average_movie_rate = calculate_average(db=db, movie=movie)

    return movie


def patch_movie(
    db: Session,
    movie: DbMovie,
    request: MoviePatchUpdate,
):
    
    update_request_data = request.dict(exclude_unset=True)
    for key, value in update_request_data.items():
        # Handle 'categories' with special logic
        if (
            key == "categories" and value is not None
        ):  # Proceed only if 'categories' is explicitly provided
            new_categories = (
                db.query(DbCategory).filter(DbCategory.id.in_(value)).all()
                if value
                else []
            )
            movie.categories = new_categories
        else:
            # For other fields, check if the value is meaningfully different from a placeholder
            if (
                value is not None
                and not (isinstance(value, int) and value == 0)
                and not (isinstance(value, str) and value == "")
            ):
                setattr(movie, key, value)

    db.commit()
    db.refresh(movie)
    return movie


def update_movie(db: Session, movie: DbMovie, request: MovieUpdate):
    # get the categories that the movie is having
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


def delete_movie(db: Session, movie_id: int) -> bool:
    movie = db.query(DbMovie).filter(DbMovie.id == movie_id).first()
    if not movie:
        return False
    db.delete(movie)
    db.commit()
    return True


def get_movie_reviews(db: Session, movie_id: int):
    return db.query(DbReview).filter(DbReview.movie_id == movie_id).all()


def get_movies_by_category(category: int, db: Session):
    movies = (
        db.query(DbMovie)
        .join(DbMovie.categories)
        .filter(DbCategory.id == category.id)
        .all()
    )

    return movies


def calculate_average(movie: DbMovie, db: Session):
    average_rate = (
        db.query(coalesce(func.avg(DbReview.user_rate), 0))
        .filter(DbReview.movie_id == movie.id)
        .scalar()
    )
    return average_rate
