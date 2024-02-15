from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import oauth2
from db import db_actors
from db.database import get_db
from schemas.mov_dir_actors_schemas import (
    Actor,
    ActorDisplay,
    ActorFullUpdate,
    ActorPatch,
)

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
    """
    Creates a new actor in the database. Requires admin authentication.

    Parameters:
    - request (Actor): The actor data to create.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Returns:
    - ActorDisplay: The created actor's information.
    """
    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
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
    """
    Retrieves all actors from the database.

    Parameters:
    - db (Session): Database session for executing database operations.

    Returns:
    - List[ActorDisplay]: A list of all actors.
    """
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
    """
    Retrieves an actor by their ID.

    Parameters:
    - actor_id (int): The ID of the actor to retrieve.
    - db (Session): Database session for executing database operations.

    Raises:
    - HTTPException: 404 Not Found if no actor with the specified ID exists.

    Returns:
    - ActorDisplay: The requested actor's information.
    """
    actor = db_actors.get_actor(db, actor_id)
    if actor is None:
        raise HTTPException(
            status_code=404, detail=f"Actor with id:{actor_id} not found"
        )
    return actor


# Update Actor in DB
@router.put(
    "/{actor_id}",
    response_model=ActorDisplay,
)
def update_actor(
    request: ActorFullUpdate,
    actor: Actor = Depends(get_actor_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Updates an existing actor in the database. Requires admin authentication.

    Parameters:
    - request (ActorFullUpdate): The updated data for the actor.
    - actor (Actor): The current actor object from the database.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Returns:
    - ActorDisplay: The updated actor's information.
    """
    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )

    return db_actors.update_actor(
        db=db,
        actor=actor,
        request=request,
    )


@router.patch(
    "/{actor_id}",
    response_model=ActorDisplay,
)
def patch_actor(
    request: ActorPatch,
    actor: Actor = Depends(get_actor_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Partially updates an actor's information in the database. 
    Requires admin authentication.

    Parameters:
    - request (ActorPatch): The partial update data for the actor.
    - actor (Actor): The current actor object from the database.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Returns:
    - ActorDisplay: The partially updated actor's information.
    """
    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )

    return db_actors.patch_actor(
        db=db,
        actor=actor,
        request=request,
    )


# Delete Actor from DB
@router.delete(
    "/{actor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_actor(
    actor: Actor = Depends(get_actor_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Deletes an actor from the database. Requires admin authentication.

    Parameters:
    - actor (Actor): The actor object to delete.
    - db (Session): Database session for executing database operations.
    - token (str): OAuth2 token to authenticate the request.

    Returns:
    - A confirmation message indicating successful deletion.
    """
    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )

    return db_actors.delete_actor(db=db, actor_id=actor.id)


@router.post(
    "/auto_add_actors",
    status_code=status.HTTP_201_CREATED,
)
def auto_add_actors(db: Session = Depends(get_db)):
    """
    THIS IS ONLY TO BE USED FOR TESTING PURPOSES
    """
    import json

    with open("example_files/example_actors.json", "r") as file:
        actors = json.load(file)

    for actor in actors:
        db_actors.create_actor(db=db, request=Actor(**actor))
    return {"message": "Actors added successfully"}
