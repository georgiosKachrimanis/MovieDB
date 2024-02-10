from fastapi import HTTPException, Depends, APIRouter, status
from db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from db import db_actors
from typing import List
from schemas import actors_schemas
from auth import oauth2
from fastapi import APIRouter

router = APIRouter(prefix="/actors", tags=["Actors Endpoints"])


# CRUD Operations for Actors
# Create Actors
@router.post("/", response_model=actors_schemas.ActorDisplay)
def create_actor(
    actor: actors_schemas.ActorBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create a actor",
        )
    else:
        return db_actors.create_actor(db, actor)


# Get All Actors
@router.get("/", response_model=List[actors_schemas.ActorDisplay])
def read_all_actors(db: Session = Depends(get_db)):
    return db_actors.get_all_actors(db)


# Get Actor By Id
@router.get("/{actor_id}", response_model=actors_schemas.ActorDisplay)
def read_actor_by_id(actor_id: int, db: Session = Depends(get_db)):
    actor = db_actors.get_actor(db, actor_id)
    if actor is None:
        raise HTTPException(status_code=404, detail=f"Actor with id:{actor_id} not found")
    return actor


# Update Actor
@router.put("/{actor_id}", response_model=actors_schemas.ActorDisplay)
def update_actor(
    actor_id: int,
    request: actors_schemas.ActorBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") == "admin":
        actor = db_actors.get_actor(db, actor_id)
        if actor is None:
            raise HTTPException(status_code=404, detail=f"Actor with id:{actor_id} not found")
        return db_actors.update_actor(
            db=db, actor_id=actor_id, request=request
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to update a actor",
        )


@router.delete("/{actor_id}")
def delete_actor(
    actor_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") == "admin":
        actor = db_actors.get_actor(db, actor_id)
        if actor is None:
            raise HTTPException(status_code=404, detail=f"Actor with id: {actor_id} not found")
        else:
            if db_actors.check_actors_in_movie(db, actor_id):
                db_actors.delete_actor(db, actor_id)  
            else:
                raise HTTPException(status_code=409, detail="This actor is associated with a movie. Cannot delete.")
        return f"Actor with id: {actor_id} deleted successfully"
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete a actor",
        )

