from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import (
    Boolean,
    DateTime,
    Float,
    String,
)

from db.database import Base


class DbUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    user_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    fav_list = Column(String)
    password = Column(String)
    reviews = relationship("DbReview", back_populates="user")


class DbMovie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    released_date = Column(DateTime)
    categories = Column(String)
    director_id = Column(Integer, ForeignKey("directors.id"))
    director = relationship("DbDirector", back_populates="movies")
    actors = relationship("DbActor", secondary="movie_actors", back_populates="movies")
    plot = Column(String)
    language = Column(String)
    country = Column(String)
    awards = Column(String)
    poster_url = Column(String)
    average_user_rate = Column(Float)
    imdb_rate = Column(Float)


class DbActor(Base):
    __tablename__ = "actors"
    id = Column(Integer, primary_key=True, index=True)
    actor_name = Column(String)
    photo_url = Column(String)
    movies = relationship("DbMovie", secondary="movie_actors", back_populates="actors")


class DbReview(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    review_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    user_rate = Column(Float)
    user = relationship("DbUser", back_populates="reviews")


class DbDirector(Base):
    __tablename__ = "directors"
    id = Column(Integer, primary_key=True, index=True)
    director_name = Column(String)
    photo_url = Column(String)
    movies = relationship("DbMovie", back_populates="director")


class DbMovieActor(Base):
    __tablename__ = "movie_actors"
    movie_id = Column(Integer, ForeignKey("movies.id"), primary_key=True)
    actor_id = Column(Integer, ForeignKey("actors.id"), primary_key=True)


# class DbReview(Base):
#     __tablename__ = "reviews"
#     id = Column(Integer, primary_key=True, index=True)
#     review_content = Column(String)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     movie_id = Column(Integer, ForeignKey("movies.id"))
#     user_rating = Column(Float)
