from sqlalchemy.orm import Session
from sqlalchemy.orm.session import Session
from schemas import actors_schemas
from db.models import  Actor,Movie
from sqlalchemy import select
from db.models import movie_actors

def create_actor(db: Session, actor: actors_schemas.ActorBase):
    actor = Actor(actor_name=actor.actor_name)
    db.add(actor)
    db.commit()
    db.refresh(actor)
    return actor

def get_actor(db: Session, actor_id: int):
    return db.query(Actor).filter(Actor.id == actor_id).first()

def get_all_actors(db: Session):
    return db.query(Actor).all()

def update_actor(db: Session, actor_id: int, request: actors_schemas.ActorBase):
    actor = db.query(Actor).filter(Actor.id == actor_id).first()
    if actor:
        actor.actor_name = request.actor_name
        db.commit()
        db.refresh(actor)
    return actor

def delete_actor(db: Session, actor_id: int):
    actor = db.query(Actor).filter(Actor.id == actor_id).first()
    if actor:
        db.delete(actor)
        db.commit()
    return actor

def check_actors_in_movie(db: Session, actor_id: int) -> bool:
    query = select(movie_actors).where(movie_actors.c.actor_id == actor_id)
    result = db.execute(query).first()
    return result is None # If result is None, actor is not in any movie

def patch_actor(
    db: Session,
    actor: Actor,
    request: actors_schemas.ActorBase,
):
    if getattr(request, 'actor_name', None) is not None:
        actor.actor_name = request.actor_name
    if getattr(request, 'movies', None) is not None:
        current_movie_ids = {movie.id for movie in actor.movies}
        if request.movies == []:
            actor.movies.clear()
        else:
            new_movies = db.query(Movie).filter(Movie.id.in_(request.movies)).all()
            for new_movie in new_movies:
                if new_movie.id not in current_movie_ids:
                    actor.movies.append(new_movie)

    db.commit()
    db.refresh(actor)
    return actor