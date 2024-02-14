from fastapi import HTTPException, Depends, APIRouter,status
from db.database import get_db
from sqlalchemy.orm import Session
from db import db_actors
from typing import List
from schemas import actors_schemas
from auth import oauth2
from fastapi import APIRouter

router = APIRouter(prefix="/actors", tags=["Actors Endpoints"])


# CRUD Operations for Actors
# Create Actors
@router.post("/", response_model=actors_schemas.ActorDisplayOne)
def create_actor(
    actor: actors_schemas.ActorBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    if oauth2.admin_authentication(token=token):
        return db_actors.create_actor(db, actor)


# Get All Actors
@router.get("/", response_model=List[actors_schemas.ActorDisplayAll])
def read_all_actors(db: Session = Depends(get_db)):
    return db_actors.get_all_actors(db)


# Get Actor By Id
@router.get("/{actor_id}", response_model=actors_schemas.ActorDisplayOne)
def get_actor_by_id(actor_id: int, db: Session = Depends(get_db)):
    actor = db_actors.get_actor(db, actor_id)
    if actor is None:
        raise HTTPException(status_code=404, detail=f"Actor with id:{actor_id} not found")
    return actor


# Update Actor
@router.put("/{actor_id}", response_model=actors_schemas.ActorDisplayOne)
def update_actor(
    actor_id: int,
    request: actors_schemas.ActorBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    if oauth2.admin_authentication(token=token):
        actor = db_actors.get_actor(db, actor_id)
        if actor is None:
            raise HTTPException(status_code=404, detail=f"Actor with id:{actor_id} not found")
        return db_actors.update_actor(
            db=db, actor_id=actor_id, request=request
        )

# Patch Actor
@router.patch(
    "/{actor_id}",
    response_model=actors_schemas.ActorDisplayOne,
)
def patch_actor(
    request: actors_schemas.ActorBase,
    actor: actors_schemas.ActorBase = Depends(get_actor_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    oauth2.admin_authentication(
        token=token,
    )

    return db_actors.patch_actor(
        db=db,
        actor=actor,
        request=request,
    )


# Delete Actor
@router.delete("/{actor_id}")
def delete_actor(
    actor_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    if oauth2.admin_authentication(token=token):
        actor = db_actors.get_actor(db, actor_id)
        if actor is None:
            raise HTTPException(status_code=404, detail=f"Actor with id: {actor_id} not found")
        else:
            if db_actors.check_actors_in_movie(db, actor_id):
                db_actors.delete_actor(db, actor_id)  
            else:
                raise HTTPException(status_code=409, detail="This actor is associated with a movie. Cannot delete.")
        return f"Actor with id: {actor_id} deleted successfully"


@router.post(
    "/auto_add_actors",
    status_code=status.HTTP_201_CREATED,
)
def auto_add_actors(db: Session = Depends(get_db)):
    """
    THIS IS ONLY TO BE USED FOR TESTING PURPOSES
    """
    import json

    with open("sampleData/example_actors.json", "r") as file:
        actors = json.load(file)

    for actor in actors:
        db_actors.create_actor(db=db, actor=actors_schemas.ActorBase(**actor))
    return {"message": "Actors added successfully"}