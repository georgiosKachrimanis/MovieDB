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
    """
    Creates a new actor in the database.
    
    This endpoint requires admin authentication. It accepts actor data conforming to the ActorBase schema,
    creates a new actor record in the database, and returns the created actor's data including the generated ID.
    
    Parameters:
    - actor: actors_schemas.ActorBase - The actor data to create.
    - db: Session - The database session.
    - token: str - The OAuth2 token for admin authentication.
    
    Returns:
    - The created actor's data, including the ID.
    """
    if oauth2.admin_authentication(token=token):
        return db_actors.create_actor(db, actor)


# Get All Actors
@router.get("/", response_model=List[actors_schemas.ActorDisplayAll])
def read_all_actors(db: Session = Depends(get_db)):
    """
    Retrieves all actors from the database.
    
    This endpoint fetches and returns a list of all actors currently stored in the database,
    with each actor's information conforming to the ActorDisplayAll schema.
    
    Parameters:
    - db: Session - The database session.
    
    Returns:
    - A list of all actors in the database.
    """
    return db_actors.get_all_actors(db)


# Get Actor By Id
@router.get("/{actor_id}", response_model=actors_schemas.ActorDisplayOne)
def get_actor_by_id(actor_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single actor by their ID.
    
    This endpoint fetches and returns the data of a specific actor, identified by their ID.
    If the actor with the given ID does not exist, it raises a 404 HTTPException.
    
    Parameters:
    - actor_id: int - The ID of the actor to retrieve.
    - db: Session - The database session.
    
    Returns:
    - The data of the requested actor.
    """
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
    """
    Updates an existing actor's information.
    
    This endpoint requires admin authentication and allows updating the data of an existing actor, identified by their ID.
    If the actor does not exist, it raises a 404 HTTPException.
    
    Parameters:
    - actor_id: int - The ID of the actor to update.
    - request: actors_schemas.ActorBase - The new data for the actor.
    - db: Session - The database session.
    - token: str - The OAuth2 token for admin authentication.
    
    Returns:
    - The updated actor's data.
    """
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
    """
    Partially updates an actor's information.
    
    This endpoint is similar to the update operation but is intended for partial updates to an actor's data.
    It requires admin authentication and allows for updating specific fields of an actor's data.
    
    Parameters:
    - request: actors_schemas.ActorBase - The partial data to update.
    - actor: actors_schemas.ActorBase - The current actor data, obtained via dependency injection.
    - db: Session - The database session.
    - token: str - The OAuth2 token for admin authentication.
    
    Returns:
    - The updated actor's data.
    """
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
    """
    Deletes an actor from the database.
    
    This endpoint requires admin authentication and allows for the deletion of an actor by their ID.
    If the actor does not exist or is associated with a movie, it raises an HTTPException.
    
    Parameters:
    - actor_id: int - The ID of the actor to delete.
    - db: Session - The database session.
    - token: str - The OAuth2 token for admin authentication.
    
    Returns:
    - A success message indicating the actor has been deleted.
    """
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
    THIS IS FOR TESTING REASONS ONLY!!!!
    Automatically adds actors to the database from a predefined JSON file.
    
    This endpoint is intended for testing purposes only. It reads actor data from a JSON file and
    adds each actor to the database using the create_actor function.
    
    Parameters:
    - db: Session - The database session.
    
    Returns:
    - A success message indicating that actors have been added successfully.
    """
    import json

    with open("sampleData/example_actors.json", "r") as file:
        actors = json.load(file)

    for actor in actors:
        db_actors.create_actor(db=db, actor=actors_schemas.ActorBase(**actor))
    return {"message": "Actors added successfully"}
