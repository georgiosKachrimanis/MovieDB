from fastapi import (
    HTTPException,
    Depends,
    APIRouter,
    status,
)
from db.database import get_db
from sqlalchemy.orm import Session
from db import db_actors
from typing import List
from schemas.mov_dir_actors_schemas import (
    Actor,
    ActorDisplay,
)
from auth import oauth2


router = APIRouter(
    prefix="/actors",
    tags=["Actors Endpoints"],
)

AUTHENTICATION_TEXT = "You are not authorized to add, edit or delete an actor!"


# CRUD Operations for Actors
# Create Actors
@router.post(
    "/",
    response_model=ActorDisplay,
    status_code=status.HTTP_201_CREATED,
)
def create_actor(
    request: Actor,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    oauth2.admin_authentication(
        token=token,
        exception_text=AUTHENTICATION_TEXT,
    )
    return db_actors.create_actor(
        db=db,
        request=request,
    )


# Get All Actors
@router.get(
    "/",
    response_model=List[ActorDisplay],
)
def get_all_actors(db: Session = Depends(get_db)):
    return db_actors.get_all_actors(db=db)


# Get Actor By Id
@router.get(
    "/{actor_id}",
    response_model=ActorDisplay,
)
def get_actor_by_id(
    actor_id: int,
    db: Session = Depends(get_db),
):
    actor = db_actors.get_actor(db, actor_id)
    if actor is None:
        raise HTTPException(
            status_code=404, detail=f"Actor with id:{actor_id} not found"
        )
    return actor


# Update Actor
@router.put("/{actor_id}", response_model=ActorDisplay)
def update_actor(
    request: Actor,
    actor: Actor = Depends(get_actor_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    oauth2.admin_authentication(
        token=token,
        exception_text=AUTHENTICATION_TEXT,
    )

    return db_actors.update_actor(
        db=db,
        actor_id=actor.id,
        request=request,
    )


@router.delete(
    "/{actor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_actor(
    actor: Actor = Depends(get_actor_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    oauth2.admin_authentication(
        token=token,
        exception_text=AUTHENTICATION_TEXT,
    )

    return db_actors.delete_actor(db=db, actor_id=actor.id)
