from datetime import datetime
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import (
    DateTime,
    Float,
    String,
)
from db.database import Base


class DbUser(Base):
    __tablename__ = "users"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    username = Column(String)
    email = Column(
        String,
        unique=True,
        index=True,
    )
    user_type = Column(String)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
    password = Column(String)
    # One <--> Many relationship
    reviews = relationship(
        "DbReview",
        back_populates="user",
    )


class DbMovie(Base):
    __tablename__ = "movies"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    title = Column(String)
    released_date = Column(DateTime)
    categories = relationship(
        "DbCategory",
        secondary="movie_categories",
        back_populates="movies",
    )
    reviews = relationship(
        "DbReview",
        back_populates="movie",
    )
    director_id = Column(
        Integer,
        ForeignKey("directors.id"),
    )
    director = relationship(
        "DbDirector",
        back_populates="movies",
    )
    actors = relationship(
        "DbActor",
        secondary="movie_actors",
        back_populates="movies",
    )
    plot = Column(String)
    poster_url = Column(String)
    average_movie_rate = Column(
        Float,
        default=0.0,
    )
    imdb_rate = Column(Float)


class DbActor(Base):
    __tablename__ = "actors"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    actor_name = Column(
        String,
        unique=True,
        index=True,
    )
    movies = relationship(
        "DbMovie",
        secondary="movie_actors",
        back_populates="actors",
    )


class DbReview(Base):
    __tablename__ = "reviews"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    review_content = Column(Text)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
    # Foreign key to establish the one<-->many relationship
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
    )
    user_rating = Column(Float)
    # One<-->many relationship
    user = relationship(
        "DbUser",
        back_populates="reviews",
    )
    # Foreign key to establish the one-to-many relationship
    movie_id = Column(
        Integer,
        ForeignKey("movies.id"),
    )
    # # One<-->many relationship
    movie = relationship(
        "DbMovie",
        back_populates="reviews",
    )


class DbDirector(Base):
    __tablename__ = "directors"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    director_name = Column(
        String,
        unique=True,
        index=True,
    )
    movies = relationship(
        "DbMovie",
        back_populates="director",
    )


class DbMovieActor(Base):
    __tablename__ = "movie_actors"
    movie_id = Column(
        Integer,
        ForeignKey("movies.id"),
        primary_key=True,
    )
    actor_id = Column(
        Integer,
        ForeignKey("actors.id"),
        primary_key=True,
    )


class DbCategory(Base):
    __tablename__ = "categories"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    category_name = Column(
        String,
        unique=True,
    )
    movies = relationship(
        "DbMovie",
        secondary="movie_categories",
        back_populates="categories",
    )  # Many-to-many relationship


"""Special many <--> many relations tables"""
movie_categories = Table(
    "movie_categories",
    Base.metadata,
    Column(
        "movie_id",
        Integer,
        ForeignKey("movies.id"),
    ),
    Column(
        "category_id",
        Integer,
        ForeignKey("categories.id"),
    ),
)


# movie_actors = Table(
#     "movie_actors",
#     Base.metadata,
#     Column(
#         "movie_id",
#         Integer,
#         ForeignKey("movies.id"),
#     ),
#     Column(
#         "actor_id",
#         Integer,
#         ForeignKey("actors.id"),
#     ),
    
# )
