from typing import (
    List,
    Optional,
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session
from auth import oauth2
from db import db_movies
from db.database import get_db
from routes.reviews import (
    create_review,
    all_reviews_for_movie,
    get_review,
    update_review,
    delete_review,
)
from routes.categories import (
    get_categories,
)
from routes.actors import get_actor_by_id, patch_actor
from schemas.mov_dir_actors_schemas import (
    MovieBase,
    MovieDisplayOne,
    MovieDisplayAll,
    MoviePatchUpdate,
    MovieUpdate,
    Category,
    ActorDisplay,
    ActorPatch,
)
from schemas.users_reviews_schemas import (
    CreateReview,
    ReviewDisplayOne,
    ReviewUpdate,
)

router = APIRouter(
    prefix="/movies",
    tags=["Movies Endpoints"],
)

AUTHENTICATION_TEXT = "You are not authorized to add, edit or delete a movie!"


# Create a new movie
@router.post(
    "/",
    response_model=MovieDisplayOne,
    status_code=status.HTTP_201_CREATED,
)
def create_movie(
    movie: MovieBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

    oauth2.admin_authentication(
        token=token,
        exception_text=AUTHENTICATION_TEXT,
    )

    if db_movies.get_movie(db=db, movie_title=movie.title):
        raise HTTPException(
            status_code=409,
            detail=f"A movie with the title {movie.title} already exists.",
        )
    return db_movies.create_movie(db, movie)


@router.get(
    "/",
    response_model=Optional[List[MovieDisplayAll]],
)
def get_movies(db: Session = Depends(get_db)):
    movies = db_movies.get_all_movies(db=db)
    if not movies:
        raise HTTPException(
            status_code=404,
            detail="The movies list is empty!",
        )
    return movies


# Get Movie By Id
@router.get(
    "/{movie_id}",
    response_model=Optional[MovieDisplayOne],
)
def get_movie_by_id(
    movie_id: int,
    db: Session = Depends(get_db),
):
    movie = db_movies.get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(
            status_code=404,
            detail=f"Movie with Id: {movie_id} not found",
        )

    return movie


@router.post(
    "/{movie_id}/reviews/",
    response_model=ReviewDisplayOne,
    status_code=status.HTTP_201_CREATED,
)
def post_review_for_movie(
    review_request: ReviewUpdate,
    movie: MovieBase = Depends(get_movie_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

    new_review = CreateReview(
        review_content=review_request.review_content,
        user_rating=review_request.user_rating,
        movie_id=movie.id,
    )
    return create_review(
        request=new_review,
        db=db,
        token=token,
    )


@router.put(
    "/{movie_id}/reviews/{review_id}",
    response_model=ReviewDisplayOne,
)
def update_review_for_movie(
    request: ReviewUpdate,
    review: ReviewDisplayOne = Depends(get_review),
    movie: MovieBase = Depends(get_movie_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    checked_review = get_review_for_movie(movie=movie, review=review, db=db)

    if not checked_review:
        raise HTTPException(
            status_code=409,
            detail=f"Review: {review.id}, doesn't belong to Movie: {movie.id}",
        )
    return update_review(
        review_id=review.id,
        db=db,
        token=token,
        request=request,
    )


@router.delete(
    "/{movie_id}/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review_for_movie(
    review: ReviewDisplayOne = Depends(get_review),
    movie: MovieBase = Depends(get_movie_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    checked_review = get_review_for_movie(movie=movie, review=review, db=db)

    if not checked_review:
        raise HTTPException(
            status_code=409,
            detail=f"Review: {review.id}, doesn't belong to Movie: {movie.id}",
        )
    return delete_review(
        review_id=review.id,
        db=db,
        token=token,
    )


@router.get(
    "/{movie_id}/reviews",
    response_model=Optional[List[ReviewDisplayOne]],
)
def get_all_reviews_for_movie(
    movie: MovieDisplayOne = Depends(get_movie_by_id),
    db: Session = Depends(get_db),
    reviews: Optional[List[ReviewDisplayOne]] = Depends(all_reviews_for_movie),
):
    return reviews


# Get Review By Id
@router.get(
    "/{movie_id}/reviews/{review_id}",
    response_model=Optional[ReviewDisplayOne],
)
def get_review_for_movie(
    movie: MovieDisplayOne = Depends(get_movie_by_id),
    db: Session = Depends(get_db),
    review: ReviewDisplayOne = Depends(get_review),
):
    for movie_review in movie.reviews:
        if movie_review.id == review.id:
            return movie_review

    raise HTTPException(
        status_code=409,
        detail=f"Review: {review.id}, doesn't belong to Movie: {movie.id}",
    )


# Update Movie
@router.put(
    "/{movie_id}",
    response_model=MovieDisplayOne,
)
def update_movie_data(
    movie_updates: MovieUpdate,
    movie: MovieBase = Depends(get_movie_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

    oauth2.admin_authentication(
        token=token,
        exception_text=AUTHENTICATION_TEXT,
    )

    if movie is None:
        raise HTTPException(
            status_code=404, detail="Movie with Id :{movie_id} not found"
        )
    else:
        updated_movie = db_movies.update_movie(
            db=db,
            movie=movie,
            request=movie_updates,
        )

    return updated_movie


@router.patch(
    "/{movie_id}",
    response_model=Optional[MovieDisplayOne],
)
def patch_movie(
    movie_id: int,
    movie_updates: Optional[MoviePatchUpdate],
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

    oauth2.admin_authentication(
        token=token,
        exception_text=AUTHENTICATION_TEXT,
    )

    movie = db_movies.get_movie(db, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=404, detail="Movie with Id :{movie_id} not found"
        )
    else:
        updated_movie = db_movies.patch_movie(
            db=db,
            movie=movie,
            request=movie_updates,
        )

    return updated_movie


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

    oauth2.admin_authentication(
        token=token,
        exception_text=AUTHENTICATION_TEXT,
    )

    reviews = db_movies.get_movie_reviews(db, movie_id)
    if reviews:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete movie with Id: {movie_id}, it has review/s",
        )

    if not db_movies.delete_movie(db, movie_id):
        raise HTTPException(
            status_code=404, detail=f"Movie with Id :{movie_id} not found"
        )
    return f"Movie with id: {movie_id} deleted successfully"


# Return Movie Categories
@router.get(
    "/{movie_id}/categories/",
)
def get_movie_categories(
    db: Session = Depends(get_db),
    movie: MovieDisplayOne = Depends(get_movie_by_id),
    categories: List[Category] = Depends(get_categories),
):
    return movie.categories


# =================================== Movie And Actors ========================


# Return Movie Actors
@router.get("/{movie_id}/actors")
def get_movie_actors(
    db: Session = Depends(get_db),
    movie: MovieDisplayOne = Depends(get_movie_by_id),
):
    return movie.actors


# Return Specific Movie Actor
@router.get("/{movie_id}/actors/{actor_id}")
def get_specific_movie_actor(
    movie: MovieDisplayOne = Depends(get_movie_by_id),
    actor: ActorDisplay = Depends(get_actor_by_id),
):
    for movie_actor in movie.actors:
        if movie_actor.id == actor.id:
            return actor

    raise HTTPException(
        status_code=404,
        detail=f"Actor: {actor.actor_name} ID: {actor.id} not in the movie.",
    )


# Add actor in the movie
@router.patch(
    "/{movie_id}/actors/{actor_id}",
    status_code=status.HTTP_201_CREATED,
)
def add_actor_in_movie(
    actor_id: int,
    movie: MovieDisplayOne = Depends(get_movie_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

    return patch_actor(
        request=ActorPatch(movies=[movie.id]),
        actor=get_actor_by_id(actor_id=actor_id, db=db),
        db=db,
        token=token,
    )


@router.post("/auto_add_movies")
def auto_add_movies(db: Session = Depends(get_db)):
    """
    THIS IS ONLY TO BE USED FOR TESTING PURPOSES
    """
    import json

    with open("example_files/example_movies.json", "r") as file:
        movies = json.load(file)
    for movie in movies:
        db_movies.create_movie(db=db, request=MovieBase(**movie))
    return {"message": "Directors added successfully"}
