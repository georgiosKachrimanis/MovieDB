from sqlalchemy.orm import Session
from sqlalchemy.orm.session import Session
from schemas import actors_schemas
from db.models import  Actor as DbActors
from sqlalchemy import select
from db.models import movie_actors

def create_actor(db: Session, actor_name: str):
    actor = DbActors(actor_name=actor_name)
    db.add(actor)
    db.commit()
    db.refresh(actor)
    return actor

def get_actor(db: Session, actor_id: int):
    return db.query(DbActors).filter(DbActors.id == actor_id).first()

def get_all_actors(db: Session):
    return db.query(DbActors).all()

def update_actor(db: Session, actor_id: int, request: actors_schemas.ActorBase):
    actor = db.query(DbActors).filter(DbActors.id == actor_id).first()
    if actor:
        actor.actor_name = request.actor_name
        db.commit()
        db.refresh(actor)
    return actor

def delete_actor(db: Session, actor_id: int):
    actor = db.query(DbActors).filter(DbActors.id == actor_id).first()
    if actor:
        db.delete(actor)
        db.commit()
    return actor

def check_actors_in_movie(db: Session, actor_id: int) -> bool:
    query = select(movie_actors).where(movie_actors.c.actor_id == actor_id)
    result = db.execute(query).first()
    return result is None # If result is None, actor is not in any movie