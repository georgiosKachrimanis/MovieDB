import os
from typing import (
    List,
    Optional,
)
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session
from auth import oauth2
from db import db_movies
from db.database import get_db
from routes.actors import (
    get_actor_by_id,
    patch_actor,
)
from db.db_categories import get_category_with_name
from routes.reviews import (
    all_reviews_for_movie,
    create_review,
    delete_review,
    get_review,
    update_review,
)
from schemas.mov_dir_actors_schemas import (
    ActorDisplay,
    ActorPatch,
    Director,
    DirectorDisplay,
    DirectorUpdate,
    MovieBase,
    MovieDisplayAll,
    MovieDisplayOne,
    MovieExtraData,
    MoviePatchUpdate,
    MovieUpdate,
    TestCategory,
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


@router.get(
    "/",
    response_model=Optional[List[MovieDisplayAll]],
)
def get_movies(
    db: Session = Depends(get_db),
    category: TestCategory = None,
    top_movies: int = None,
    director_id: int = None,
    actor_id: int = None,
):
    movies = db_movies.get_all_movies(db=db)
    if not movies:
        raise HTTPException(
            status_code=404,
            detail="The movies list is empty!",
        )

    if category:
        movies = get_movies_by_category(
            db=db,
            category_name=category,
            movies=movies,
        )

    if top_movies:
        movies = sorted(
            movies,
            key=lambda x: x.average_movie_rate if x.average_movie_rate else 0,
            reverse=True,
        )[:top_movies]

    if director_id:
        movies = get_movies_by_director(
            movies=movies,
            director_id=director_id,
        )

    if actor_id:
        movies = get_movies_by_actor(movies=movies, actor_id=actor_id)

    return movies


# Get Movie By Id
@router.get(
    "/{movie_id}",
    response_model=Optional[MovieDisplayOne],
)
def get_movie_by_id(
    movie_id: int,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2.oauth2_schema),
):

    if token:
        payload = oauth2.decode_access_token(token=token)
        user_id = int(payload.get("user_id"))
        movie = db_movies.get_movie(
            db=db,
            movie_id=movie_id,
            user_id=user_id,
        )
    else:
        movie = db_movies.get_movie(
            db=db,
            movie_id=movie_id,
            user_id=0,
        )

    if movie is None:
        raise HTTPException(
            status_code=404,
            detail=f"Movie with Id: {movie_id} not found",
        )

    return movie


@router.get(
    "/{movie_id}/reviews",
    response_model=Optional[List[ReviewDisplayOne]],
)
def get_movie_reviews(
    movie: MovieDisplayOne = Depends(get_movie_by_id),
    db: Session = Depends(get_db),
    reviews: Optional[List[ReviewDisplayOne]] = Depends(all_reviews_for_movie),
    review_id: Optional[int] = None,
):
    if review_id:
        reviews = get_movie_review(
            movie=movie,
            review_id=review_id,
        )

    return reviews


# Return Movie Actors
@router.get(
    "/{movie_id}/actors",
    response_model=List[ActorDisplay],
)
def get_movie_actors(
    db: Session = Depends(get_db),
    movie: MovieDisplayOne = Depends(get_movie_by_id),
    actor_id: Optional[int] = None,
):
    for movie_actor in movie.actors:
        if movie_actor.id == actor_id:
            return [movie_actor]
        raise HTTPException(
            status_code=404,
            detail=f"Actor with ID: {actor_id}, doesn't belong to Movie.",
        )

    return [ActorDisplay.model_validate(actor) for actor in movie.actors]


@router.get(
    "/{movie_id}/director",
    response_model=DirectorDisplay,
)
def get_movie_director(movie: MovieDisplayOne = Depends(get_movie_by_id)):
    return DirectorDisplay.model_validate(movie.director)


# Get Extra Data for a Movie by IMDB Id
@router.get(
    "/{movie_id}/extra_data",
    response_model=MovieExtraData,
)
async def get_movie_extra(
    movie: MovieBase = Depends(get_movie_by_id),
):
    return await db_movies.get_movie_extra(movie=movie)


# ========================== Post Endpoints =====================
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
    """
    Create a new movie entry in the database.

    This endpoint creates a new movie with the details provided in the
    request body. It requires an authenticated admin user token to proceed.
    If a movie with the same title already exists, it raises an
    HTTP 409 Conflict exception.

    Parameters:
    - movie (MovieBase):
        The movie details to be created, excluding the id.
    - db (Session):
        The database session dependency to perform database operations.
    - token (str):
        The admin user's authentication token.

    Raises:
    - HTTPException:
        409 Conflict if a movie with the same title already exists.
    - HTTPException:
        Various authentication related errors handled by the
        `oauth2.admin_authentication` function.

    Returns:
    - The created movie details as an instance of `MovieDisplayOne`.
    """

    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )

    if db_movies.get_movie(db=db, movie_title=movie.title):
        raise HTTPException(
            status_code=409,
            detail=f"A movie with the title {movie.title} already exists.",
        )
    return db_movies.create_movie(db, movie)


# @router.post(
#     "/{movie_id}/reviews/",
#     response_model=ReviewDisplayOne,
#     status_code=status.HTTP_201_CREATED,
# )
# def post_review_for_movie(
#     review_request: ReviewUpdate,
#     movie: MovieBase = Depends(get_movie_by_id),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_schema),
# ):
#     oauth2.admin_authentication(
#         token=token,
#         detail=AUTHENTICATION_TEXT,
#     )

#     new_review = CreateReview(
#         review_content=review_request.review_content,
#         user_rating=review_request.user_rating,
#         movie_id=movie.id,
#     )
#     return create_review(
#         request=new_review,
#         db=db,
#         token=token,
#     )


# Upload Movie Poster Image
@router.post(
    "/{movie_id}/upload_poster",
    response_model=MovieDisplayOne,
)
async def upload_file(
    movie: MovieDisplayOne = Depends(get_movie_by_id),
    upload_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    file_extension = os.path.splitext(upload_file.filename)[-1]
    if file_extension not in [".jpg", ".png"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only jpg and png types accepted.",
        )
    title = movie.title.replace(" ", "_")
    new_filename = f"{movie.id}_{title}{file_extension}"
    contents = await upload_file.read()
    # Check if the directory exists and if not, create it
    directory = "assets/posters"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f"{directory}/{new_filename}", "wb") as f:
        f.write(contents)
    file_path = os.path.abspath(f"{directory}/{new_filename}")

    return db_movies.update_movie_poster_url(
        db=db,
        movie=movie,
        file_path=file_path,
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
    return {"message": "Movies added successfully"}


# ============================= PUT Endpoints ==========================
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
        detail=AUTHENTICATION_TEXT,
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


# @router.put(
#     "/{movie_id}/director/{director_id}",
#     response_model=Director,
# )
# def update_movie_director(
#     director_id: int,
#     movie: MovieDisplayOne = Depends(get_movie_by_id),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_schema),
# ):
#     oauth2.admin_authentication(
#         token=token,
#         detail=AUTHENTICATION_TEXT,
#     )

#     from db import db_directors

#     director = db_directors.get_director(
#         director_id=director_id,
#         db=db,
#     )
#     request = DirectorUpdate(
#         director_name=director.director_name,
#         movies=[movie.id],
#     )
#     return db_directors.update_director(
#         db=db,
#         director=director,
#         request=request,
#     )


# @router.put(
#     "/{movie_id}/reviews/{review_id}",
#     response_model=ReviewDisplayOne,
# )
# def update_review_for_movie(
#     request: ReviewUpdate,
#     review: ReviewDisplayOne = Depends(get_review),
#     movie: MovieBase = Depends(get_movie_by_id),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_schema),
# ):
#     oauth2.admin_authentication(
#         token=token,
#         detail=AUTHENTICATION_TEXT,
#     )
#     checked_review = get_review_for_movie(movie=movie, review=review, db=db)

#     if not checked_review:
#         raise HTTPException(
#             status_code=409,
#             detail=f"Review: {review.id}, doesn't belong to Movie: {movie.id}",
#         )
#     return update_review(
#         review_id=review.id,
#         db=db,
#         token=token,
#         request=request,
#     )


# ================================= PATCH Endpoints =========================
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
        detail=AUTHENTICATION_TEXT,
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


# # Add actor in the movie
# @router.patch(
#     "/{movie_id}/actors/{actor_id}",
#     response_model=ActorDisplay,
#     status_code=status.HTTP_201_CREATED,
# )
# def add_actor_in_movie(
#     actor_id: int,
#     movie: MovieDisplayOne = Depends(get_movie_by_id),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_schema),
# ):

#     return patch_actor(
#         request=ActorPatch(movies=[movie.id]),
#         actor=get_actor_by_id(actor_id=actor_id, db=db),
#         db=db,
#         token=token,
#     )


# ================================= DELETE Endpoints ========================
# @router.delete(
#     "/{movie_id}/reviews/{review_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# def delete_review_for_movie(
#     review: ReviewDisplayOne = Depends(get_review),
#     movie: MovieBase = Depends(get_movie_by_id),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_schema),
# ):
#     checked_review = get_review_for_movie(movie=movie, review=review, db=db)

#     if not checked_review:
#         raise HTTPException(
#             status_code=409,
#             detail=f"Review: {review.id}, doesn't belong to Movie: {movie.id}",
#         )
#     return delete_review(
#         review_id=review.id,
#         db=db,
#         token=token,
#     )


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
        detail=AUTHENTICATION_TEXT,
    )

    reviews = db_movies.get_movie_reviews(db, movie_id)
    if reviews:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete movie with ID: {movie_id}, it has review/s",
        )

    if not db_movies.delete_movie(db=db, movie_id=movie_id):
        raise HTTPException(
            status_code=404, detail=f"Movie with Id :{movie_id} not found"
        )
    return f"Movie with id: {movie_id} deleted successfully"


# To Be used with the get_all_movies
def get_movies_by_category(
    db: Session,
    category_name: str,
    movies: List[MovieBase],
):
    category_id = get_category_with_name(db=db, category_name=category_name)
    filtered_movies = []
    for movie in movies:
        for movie_category in movie.categories:
            if category_id == int(movie_category.id):
                filtered_movies.append(movie)
    if filtered_movies == []:
        raise HTTPException(
            status_code=404,
            detail=f"No movies in {category_name}",
        )
    return filtered_movies


def get_movie_review(
    movie: MovieDisplayOne,
    review_id: int,
):
    for movie_review in movie.reviews:
        if movie_review.id == review_id:
            reviews = [movie_review]
            return reviews

    raise HTTPException(
        status_code=409,
        detail=f"Review: {review_id}, doesn't belong to Movie: {movie.id}",
    )


def get_movies_by_director(
    movies: List[MovieDisplayAll],
    director_id: int,
):
    filtered_movies = []
    for movie in movies:
        if int(movie.director.id) == director_id:
            filtered_movies.append(movie)
    if filtered_movies == []:
        raise HTTPException(
            status_code=404,
            detail=f"No movies for director with ID:{director_id}.",
        )

    return filtered_movies


def get_movies_by_actor(
    movies: List[MovieDisplayAll],
    actor_id: int,
):

    filtered_movies = []
    for movie in movies:
        for movie_actor in movie.actors:
            if actor_id == int(movie_actor.id):
                filtered_movies.append(movie)
    if filtered_movies == []:
        raise HTTPException(
            status_code=404,
            detail=f"No movies with actor ID: {actor_id}",
        )
    return filtered_movies
