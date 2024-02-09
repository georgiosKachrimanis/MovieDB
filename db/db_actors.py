from sqlalchemy.orm import Session
from schemas.mov_dir_actors_schemas import Actor, ActorDisplay
from db.models import DbActor
from sqlalchemy import select



def create_actor(db: Session, request: Actor):
    actor = DbActor(actor_name=request.actor_name)
    db.add(actor)
    db.commit()
    db.refresh(actor)
    return actor


def get_actor(db: Session, actor_id: int):
    return db.query(DbActor).filter(DbActor.id == actor_id).first()


def get_all_actors(db: Session):
    return db.query(DbActor).all()


def update_actor(db: Session, actor_id: int, request: Actor):
    actor = db.query(DbActor).filter(DbActor.id == actor_id).first()
    if actor:
        actor.actor_name = request.actor_name
        db.commit()
        db.refresh(actor)
    return actor


def delete_actor(db: Session, actor_id: int):
    actor = db.query(DbActor).filter(DbActor.id == actor_id).first()
    if actor:
        db.delete(actor)
        db.commit()
    return actor


# def check_actors_in_movie(db: Session, actor_id: int) -> bool:
#     query = select(movie_actors).where(movie_actors.c.actor_id == actor_id)
#     result = db.execute(query).first()
#     return result is None  # If result is None, actor is not in any movie
