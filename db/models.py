from .database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship


class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, index=True)
  username = Column(String)
  email = Column(String)
  user_type = Column(String)
  created_at = Column(DateTime, default=datetime.utcnow)
  fav_list = Column(String)
  password = Column(String)
  reviews = relationship("Review", back_populates="user")

class Review(Base):
  __tablename__ = 'reviews'
  id = Column(Integer, primary_key=True, index=True)
  review_content = Column(String)
  created_at = Column(DateTime, default=datetime.utcnow)
  user_id = Column(Integer, ForeignKey('users.id'))
  user_rate = Column(Float)
  user = relationship("User", back_populates="reviews")


class Movie(Base):
  __tablename__ = 'movies'
  id = Column(Integer, primary_key=True, index=True)
  title = Column(String)
  released_date = Column(DateTime)
  categories = Column(String)
  director_id = Column(Integer, ForeignKey('directors.id'))
  director = relationship("Director", back_populates="movies")
  actors = relationship("Actor", secondary="movie_actors", back_populates="movies")
  plot = Column(String)
  language = Column(String)
  country = Column(String)
  awards = Column(String)
  poster_url = Column(String)
  average_user_rate = Column(Float)
  imdb_rate = Column(Float)


class Actor(Base):
  __tablename__ = 'actors'
  id = Column(Integer, primary_key=True, index=True)
  actor_name = Column(String)
  photo_url = Column(String)
  movies = relationship("Movie", secondary="movie_actors", back_populates="actors")


class Director(Base):
  __tablename__ = 'directors'
  id = Column(Integer, primary_key=True, index=True)
  director_name = Column(String)
  photo_url = Column(String)
  movies = relationship("Movie", back_populates="director")


class MovieActor(Base):
  __tablename__ = 'movie_actors'
  movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
  actor_id = Column(Integer, ForeignKey('actors.id'), primary_key=True)
