from .database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float,Table
from datetime import datetime
from sqlalchemy.orm import relationship
from .database import Base



movie_categories = Table('movie_categories', Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id')),     # Many-to-many relationship
    Column('category_id', Integer, ForeignKey('categories.id')) # Many-to-many relationship
)

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, index=True)
  username = Column(String)
  email = Column(String)
  user_type = Column(String)
  created_at = Column(DateTime, default=datetime.utcnow)
  password = Column(String)
  reviews = relationship("Review", back_populates="user") # One-to-many relationship

class Review(Base):
  __tablename__ = 'reviews'
  id = Column(Integer, primary_key=True, index=True)
  review_content = Column(String)
  created_at = Column(DateTime, default=datetime.utcnow)
  user_id = Column(Integer, ForeignKey('users.id')) # Foreign key to establish the one-to-many relationship
  movie_rate = Column(Float)
  user = relationship("User", back_populates="reviews") # One-to-many relationship
  movie_id = Column(Integer, ForeignKey('movies.id')) # Foreign key to establish the one-to-many relationship
  movie = relationship("Movie", back_populates="reviews") # One-to-many relationship


class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    released_date = Column(DateTime)
    categories = relationship("Category", secondary="movie_categories", back_populates="movies")
    reviews = relationship("Review", back_populates="movie") # One-to-many relationship
    actors = relationship("Actors", secondary="movie_actors", back_populates="movies") # Many-to-many relationship
    director_id = Column(Integer, ForeignKey('directors.id'))  # Foreign key to establish the one-to-many relationship
    director = relationship("Directors", back_populates="movies") # One-to-many relationship
    plot = Column(String)
    poster_url = Column(String)
    average_movie_rate = Column(Float, default=0.0)
    imdb_rate = Column(Float)


class Category(Base):
  __tablename__ = 'categories'
  id = Column(Integer, primary_key=True, index=True)
  category_name = Column(String)
  movies = relationship("Movie", secondary="movie_categories", back_populates="categories") # Many-to-many relationship

# class Actors(Base):
#   __tablename__ = 'actors'
#   id = Column(Integer, primary_key=True, index=True)
#   actor_name = Column(String)
#   movies = relationship("Movie", secondary="movie_actors", back_populates="actors") # Many-to-many relationship

# class Directors(Base):
#   __tablename__ = 'directors'
#   id = Column(Integer, primary_key=True, index=True)
#   director_name = Column(String)
#   movies = relationship("Movie", back_populates="director") # One-to-many relationship
