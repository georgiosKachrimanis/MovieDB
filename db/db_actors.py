from sqlalchemy.orm import Session
from schemas.actors_schemas import (
    Actor,
    ActorFullUpdate,
    ActorPatch,
)
from db.models import (
    DbActor,
    DbMovie,
)


def create_actor(
    db: Session,
    request: Actor,
):
    actor = DbActor(actor_name=request.actor_name)
    db.add(actor)
    db.commit()
    db.refresh(actor)
    return actor


def get_actor(
    db: Session,
    actor_id: int,
):
    return db.query(DbActor).filter(DbActor.id == actor_id).first()


def get_all_actors(db: Session):
    return db.query(DbActor).all()


def update_actor(
    db: Session,
    actor: Actor,
    request: ActorFullUpdate,
):

    actor.actor_name = request.actor_name

    if request.movies is not None:
        current_movie_ids = {movie.id for movie in actor.movies}
        if request.movies == []:
            actor.movies.clear()
        else:
            new_movies = db.query(DbMovie).filter(DbMovie.id.in_(request.movies)).all()
            for new_movie in new_movies:
                if new_movie.id not in current_movie_ids:
                    actor.movies.append(new_movie)

    db.commit()
    db.refresh(actor)
    return actor


def patch_actor(
    db: Session,
    actor: Actor,
    request: ActorPatch,
):
    if getattr(request, 'actor_name', None) is not None:
        actor.actor_name = request.actor_name
    if getattr(request, 'movies', None) is not None:
        current_movie_ids = {movie.id for movie in actor.movies}
        if request.movies == []:
            actor.movies.clear()
        else:
            new_movies = db.query(DbMovie).filter(DbMovie.id.in_(request.movies)).all()
            for new_movie in new_movies:
                if new_movie.id not in current_movie_ids:
                    actor.movies.append(new_movie)

    db.commit()
    db.refresh(actor)
    return actor


def delete_actor(
    db: Session,
    actor_id: int,
):
    actor = db.query(DbActor).filter(DbActor.id == actor_id).first()
    if actor:
        db.delete(actor)
        db.commit()
    return actor

# TODO: Check if we need this functionality
# def check_actors_in_movie(db: Session, actor_id: int) -> bool:
#     query = select(movie_actors).where(movie_actors.c.actor_id == actor_id)
#     result = db.execute(query).first()
#     return result is None  # If result is None, actor is not in any movie
