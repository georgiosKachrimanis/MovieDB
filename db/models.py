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
    Boolean,
)
from db.database import Base


class DbUser(Base):
    __tablename__ = "users"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        unique=True,
    )
    username = Column(String)
    email = Column(
        String,
        unique=True,
        index=True,
    )
    user_type = Column(String)
    password = Column(String)
    # Users need to be activated.
    user_active = Column(
        Boolean,
        default=False,
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
    reviews = relationship(
        "DbReview",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    requests = relationship(
        "DbMovieRequest",
        back_populates="user",
    )


class DbMovie(Base):
    __tablename__ = "movies"
    id = Column(
        Integer,
        unique=True,
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
        cascade="all, delete-orphan",
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
    imdb_id = Column(String)
    requests_count = Column(
        Integer,
        default=0,
    )
    requests = relationship(
        "DbMovieRequest",
        back_populates="movies",
    )
    created_date = Column(
        DateTime,
        default=datetime.utcnow,
    )


class DbActor(Base):
    __tablename__ = "actors"
    id = Column(
        Integer,
        unique=True,
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
    created_date = Column(
        DateTime,
        default=datetime.utcnow,
    )


class DbReview(Base):
    __tablename__ = "reviews"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        unique=True,
    )
    review_content = Column(Text)
    # Foreign key to establish the one<-->many relationship
    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
    )
    user_rating = Column(Float)
    user = relationship(
        "DbUser",
        back_populates="reviews",
    )
    movie_id = Column(
        Integer,
        ForeignKey(
            "movies.id",
            ondelete="CASCADE",
        ),
    )
    movie = relationship(
        "DbMovie",
        back_populates="reviews",
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


class DbDirector(Base):
    __tablename__ = "directors"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        unique=True,
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
    director_active = Column(
        Boolean,
        default=True,
    )
    created_date = Column(
        DateTime,
        default=datetime.utcnow,
    )


class DbMovieActor(Base):
    __tablename__ = "movie_actors"
    movie_id = Column(
        Integer,
        ForeignKey(
            "movies.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    actor_id = Column(
        Integer,
        ForeignKey(
            "actors.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )


class DbCategory(Base):
    __tablename__ = "categories"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        unique=True,
    )
    category_name = Column(
        String,
        unique=True,
    )
    movies = relationship(
        "DbMovie",
        secondary="movie_categories",
        back_populates="categories",
    )
    category_active = Column(
        Boolean,
        default=True,
    )
    created_date = Column(
        DateTime,
        default=datetime.utcnow,
    )


class DbMovieRequest(Base):
    __tablename__ = "requests"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    movie_id = Column(
        Integer,
        ForeignKey("movies.id"),
    )
    request_time = Column(DateTime)
    movies = relationship(
        "DbMovie",
        back_populates="requests",
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
    )
    user = relationship(
        "DbUser",
        back_populates="requests",
    )


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
