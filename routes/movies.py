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
from db.db_categories import get_category_with_name
from routes.reviews import all_reviews_for_movie
from schemas.actors_schemas import ActorDisplay
from schemas.categories_schemas import CategoryMenu
from schemas.directors_schemas import DirectorDisplay
from schemas.movies_schemas import (
    MovieBase,
    MovieDisplayOne,
    MovieExtraData,
    MoviePatchUpdate,
    MovieUpdate,
)
from schemas.reviews_schemas import ReviewDisplayOne
from services.movie_service import get_movie_extra_data

router = APIRouter(
    prefix="/movies",
    tags=["Movies Endpoints"],
)

AUTHENTICATION_TEXT = "You are not authorized to add, edit or delete a movie!"


@router.get(
    "/",
    response_model=Optional[List[MovieDisplayOne]],
)
def get_movies(
    db: Session = Depends(get_db),
    actor_id: int = None,
    director_id: int = None,
    category: CategoryMenu = None,
    top_movies: int = None,
):
    """
    Retrieves a list of movies from the database. Can filter movies by actor ID
    director ID, category, and limit the result to top N movies based on
    average movie rate.

    Parameters:
    - db (Session): Database session for executing database operations.
    - actor_id (int, optional): Filter movies by actor ID.
    - director_id (int, optional): Filter movies by director ID.
    - category (Category, optional): Filter movies by category.
    - top_movies (int, optional): Limit the result to top N movies.

    Raises:
    - HTTPException: 404 error if the movies list is empty or
        specific filters yield no results.

    Returns:
    - Optional[List[MovieDisplayAll]]: List of movies matching
        the criteria or None.
    """
    movies = db_movies.get_all_movies(db=db)
    if not movies:
        raise HTTPException(
            status_code=404,
            detail="The movies list is empty!",
        )
    if actor_id:
        movies = get_movies_by_actor(
            movies=movies,
            actor_id=actor_id,
        )

    if category:
        movies = get_movies_by_category(
            db=db,
            category_name=category,
            movies=movies,
        )

    if director_id:
        movies = get_movies_by_director(
            movies=movies,
            director_id=director_id,
        )

    if top_movies:
        movies = sorted(
            movies,
            key=lambda x: x.average_movie_rate if x.average_movie_rate else 0,
            reverse=True,
        )[:top_movies]

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
    """
    Retrieves a movie by its ID. Requires a valid token to retrieve
    user-specific information if provided.

    Parameters:
    - movie_id (int): The ID of the movie to retrieve.
    - db (Session): Database session for executing database operations.
    - token (Optional[str]): The OAuth2 token for user authentication.

    Raises:
    - HTTPException: 404 error if the movie with the specified ID is not found.

    Returns:
    - Optional[MovieDisplayOne]: The movie matching the ID or None.
    """

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
    """
    Retrieves reviews for a specific movie. Can filter the reviews by
    a specific review ID.

    Parameters:
    - movie (MovieDisplayOne): The movie object obtained by `get_movie_by_id`.
    - db (Session): Database session for executing database operations.
    - reviews (Optional[List[ReviewDisplayOne]]): List of reviews for movie.
    - review_id (Optional[int]): Filter reviews by review ID.

    Returns:
    - Optional[List[ReviewDisplayOne]]: List of reviews for the movie or a
    specific review if review_id is provided.
    """

    # This will return only one review if it is for the movie.
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
    """
    Retrieves actors for a specific movie. Can filter actors by a
    specific actor ID.

    Parameters:
    - db (Session): Database session for executing database operations.
    - movie (MovieDisplayOne): The movie object obtained by `get_movie_by_id`.
    - actor_id (Optional[int]): Filter actors by actor ID.

    Raises:
    - HTTPException: 404 error if the actor with the specified ID does not
        belong to the movie.

    Returns:
    - List[ActorDisplay]: List of actors for the movie or a specific actor
    if actor_id is provided.
    """
    for movie_actor in movie.actors:
        if movie_actor.id == actor_id:
            return [movie_actor]
        raise HTTPException(
            status_code=404,
            detail=f"Actor with ID: {actor_id}, is not in {movie.title}.",
        )

    return [ActorDisplay.model_validate(actor) for actor in movie.actors]


@router.get(
    "/{movie_id}/director",
    response_model=DirectorDisplay,
)
def get_movie_director(movie: MovieDisplayOne = Depends(get_movie_by_id)):
    """
    Retrieves the director of a specific movie.

    Parameters:
    - movie (MovieDisplayOne): The movie object obtained by `get_movie_by_id`.

    Returns:
    - DirectorDisplay: The director of the movie.
    """
    return DirectorDisplay.model_validate(movie.director)


# Get Extra Data for a Movie by IMDB Id
@router.get(
    "/{movie_id}/extra_data",
    response_model=MovieExtraData,
)
async def get_movie_extra(
    movie: MovieBase = Depends(get_movie_by_id),
):
    """
    Retrieves extra data for a movie by its IMDb ID.
    This is an asynchronous function.

    Parameters:
    - movie (MovieBase): The movie object obtained from `get_movie_by_id`.

    Returns:
    - MovieExtraData: Extra data about the movie.
    """
    if movie.imdb_id is None:
        return "No imdb_id stored in the DB for this movie."
    else:
        return await get_movie_extra_data(movie.imdb_id)


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
    Creates a new movie entry in the database. Requires an admin user token
    for authentication.

    Parameters:
    - movie (MovieBase): The movie details to create.
    - db (Session): Database session for executing database operations.
    - token (str): Admin user's authentication token.

    Raises:
    - HTTPException: 409 Conflict if a movie with the same title already
        exists.

    Returns:
    - MovieDisplayOne: The created movie details.
    """

    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )

    return db_movies.create_movie(db, movie)


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
    """
    Uploads a poster image file for a movie. Validates file type and
    updates the movie's poster URL in the database.

    Parameters:
    - movie (MovieDisplayOne): The movie object to upload the poster for.
    - upload_file (UploadFile): The poster image file.
    - db (Session): Database session for executing database operations.
    - token (str): Admin user's authentication token.

    Raises:
    - HTTPException: 400 error if the file type is not jpg or png.

    Returns:
    - MovieDisplayOne: The updated movie details with the new poster URL.
    """
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


@router.post("/auto_add_movies", status_code=status.HTTP_201_CREATED)
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
    """
    Updates the details of an existing movie. Requires an admin user
    token for authentication.

    Parameters:
    - movie_updates (MovieUpdate): The updated movie details.
    - movie (MovieBase): The original movie object obtained `get_movie_by_id`.
    - db (Session): Database session for executing database operations.
    - token (str): Admin user's authentication token.

    Raises:
    - HTTPException: 404 error if the movie with the specified ID is not found.

    Returns:
    - MovieDisplayOne: The updated movie details.
    """

    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )

    updated_movie = db_movies.update_movie(
        db=db,
        movie=movie,
        request=movie_updates,
    )

    return updated_movie


# ================================= PATCH Endpoints =========================
@router.patch(
    "/{movie_id}",
    response_model=Optional[MovieDisplayOne],
)
def patch_movie(
    movie_updates: Optional[MoviePatchUpdate],
    movie: MovieBase = Depends(get_movie_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Partially updates the details of an existing movie. Requires an admin
    user token for authentication.

    Parameters:
    - movie_id (int): The ID of the movie to update.
    - movie_updates (Optional[MoviePatchUpdate]): The updated movie details.
    - db (Session): Database session for executing database operations.
    - token (str): Admin user's authentication token.

    Raises:
    - HTTPException: 404 error if the movie with the specified ID is not found.

    Returns:
    - Optional[MovieDisplayOne]: The updated movie details or None.
    """
    oauth2.admin_authentication(
        token=token,
        detail=AUTHENTICATION_TEXT,
    )

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


# ================================= DELETE Endpoints ========================
@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    """
    Deletes a movie from the database. Requires an admin user token
    for authentication.

    Parameters:
    - movie_id (int): The ID of the movie to delete.
    - db (Session): Database session for executing database operations.
    - token (str): Admin user's authentication token.

    Raises:
    - HTTPException: 409 error if the movie has associated reviews.
    - HTTPException: 404 error if the movie with the specified ID is not found.

    Returns:
    - A success message indicating the movie was deleted.
    """

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
    category_id = get_category_with_name(
        db=db,
        category_name=category_name,
    )

    filtered_movies = []
    for movie in movies:
        for movie_category in movie.categories:
            if category_id == int(movie_category.id):
                filtered_movies.append(movie)
    if filtered_movies == []:
        raise HTTPException(
            status_code=404,
            detail=f"No movies in category with ID: {category_id}",
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
    movies: List[MovieDisplayOne],
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
    movies: List[MovieDisplayOne],
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
