from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from schemas import movies_schemas, reviews_schemas,categories_schemas,actors_schemas,directors_schemas
from db import db_movies, db_reviews,db_actors
from auth import oauth2
import os
from db.db_movies import update_movie_poster_url, create_request_log, check_movie
from routes import reviews,categories,actors
from services.movie_service import get_movie_extra_data
from datetime import datetime


router = APIRouter(prefix="/movies", tags=["Movie Endpoints"])



# CRUD Operations for Movie
# Create Movie
@router.post(
    "/",
    response_model=movies_schemas.MovieDisplayOne,
    status_code=status.HTTP_201_CREATED,
)
def create_movie(
    movie: movies_schemas.MovieBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

    if oauth2.admin_authentication(token=token):
        return db_movies.create_movie(db, movie)


# Get All Movies
@router.get("/", response_model=List[movies_schemas.MovieDisplayAll])
def get_all_movies(db: Session = Depends(get_db)):
    movies = db_movies.get_all_movies(db=db)
    if not movies:
        raise HTTPException(
            status_code=404,
            detail="The movies list is empty!",
        )
    return movies


# Get Top10 Movies
@router.get(
    "/top10",
    response_model=Optional[List[movies_schemas.MovieDisplayAll]],
)
def get_top10_movies(
    db: Session = Depends(get_db),
):
    movies = db_movies.get_all_movies(db=db)
    if not movies:
        raise HTTPException(
            status_code=404,
            detail="The movies list is empty!",
        )
    else:
        return db_movies.get_top10_movies(db=db)


# Get Movies Request Counts
@router.get("/request-count", response_model=List[movies_schemas.MovieRequestCount])
def get_movies_request_count(
    start_date: datetime = Query("2024-02-14T00:00:00"),
    end_date: datetime = Query("2024-02-14T00:00:00"),
    db: Session = Depends(get_db),
):
    return db_movies.get_movie_request_count(
        db=db, start_date=start_date, end_date=end_date
    )


# Get Movie By Id
@router.get("/{movie_id}", response_model=movies_schemas.MovieDisplayOne)
def get_movie_by_id(
    movie_id: int,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2.oauth2_schema),
):
    if check_movie(db, movie_id):
        movie = db_movies.get_movie(db, movie_id)
        if token:
            user_id = oauth2.decode_access_token(token=token).get("user_id")
        else:
            user_id = None
        db_movies.patch_movie(
            db,
            movie,
            movies_schemas.MoviePatchUpdate(
                number_of_request=movie.number_of_request + 1
            ),
        )
        create_request_log(db, movie_id, user_id)
        return db_movies.get_movie(db, movie_id)
    else:
        raise HTTPException(
            status_code=404, detail=f"Movie with Id :{movie_id} not found"
        )


# # Create Movie Reviews
# @router.post(
#     "/{movie_id}/reviews/",
#     response_model=reviews_schemas.ReviewDisplayOne,
#     status_code=status.HTTP_201_CREATED,
# )
# def post_review_for_movie(
#     review_request: reviews_schemas.ReviewUpdate,
#     movie: movies_schemas.MovieBase = Depends(get_movie_by_id),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_schema),
# ):
#     try:
#         payload = oauth2.decode_access_token(token=token)
#     except Exception as e:
#         raise HTTPException(
#             status_code=401,
#             detail="You need to log in to create a movie!",
#         ) from e
#     else:
#         new_review = reviews_schemas.ReviewBase(
#             review_content=review_request.review_content,
#             movie_rate=review_request.movie_rate,
#             movie_id=movie.id,
#         )
#         return reviews.create_review(
#             request=new_review,
#             db=db,
#             token=token,
#         )

# # Update Movie Reviews
# @router.put(
#     "/{movie_id}/reviews/{review_id}",
#     response_model=reviews_schemas.ReviewDisplayOne,
# )
# def update_review_for_movie(
#     request: reviews_schemas.ReviewUpdate,
#     review: reviews_schemas.ReviewDisplayOne = Depends(reviews.get_review_by_id),
#     movie: movies_schemas.MovieBase = Depends(get_movie_by_id),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_schema),
# ):
#     oauth2.admin_authentication(
#         token=token,
#     )
#     checked_review = get_review_for_movie(movie=movie, review=review, db=db)

#     if not checked_review:
#         raise HTTPException(
#             status_code=409,
#             detail=f"Review: {review.id}, doesn't belong to Movie: {movie.id}",
#         )
#     return reviews.update_review(
#         review_id=review.id,
#         db=db,
#         token=token,
#         request=request,
#     )


# Get All Reviews for a Movie
@router.get(
    "/{movie_id}/reviews",
    response_model=Optional[List[reviews_schemas.ReviewDisplayOne]],
)
def get_all_reviews_for_movie(
    movie: movies_schemas.MovieDisplayOne = Depends(get_movie_by_id),
    db: Session = Depends(get_db),
    reviews: Optional[List[reviews_schemas.ReviewDisplayOne]] = Depends(db_reviews.all_reviews_for_movie),
    review_id: Optional[int]=None
):
    if review_id:
        for review in reviews:
            if review.id == review_id:
                return [review]
        raise HTTPException(
            status_code=404,
            detail=f"Review with Id :{review_id} not found"
        )
    return reviews


# # Get Review By Id
# @router.get(
#     "/{movie_id}/reviews/{review_id}",
#     response_model=Optional[reviews_schemas.ReviewDisplayOne],
# )
# def get_review_for_movie(
#     movie: movies_schemas.MovieDisplayOne = Depends(get_movie_by_id),
#     db: Session = Depends(get_db),
#     review: reviews_schemas.ReviewDisplayOne = Depends(reviews.get_review_by_id),
# ):
#     for movie_review in movie.reviews:
#         if movie_review.id == review.id:
#             return movie_review

#     raise HTTPException(
#         status_code=409,
#         detail=f"Review: {review.id}, doesn't belong to Movie: {movie.id}",
#     )


# Update Movie
@router.put("/{movie_id}", response_model=Optional[movies_schemas.MovieDisplayOne])
def update_movie(
    movie_id: int,
    movie: movies_schemas.MovieUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    if oauth2.admin_authentication(token=token):
        if check_movie(db, movie_id):
            if movie is None:
                raise HTTPException(
                    status_code=404, detail="Movie with Id :{movie_id} not found"
                )
            else:
                return db_movies.update_movie(db, movie_id, movie)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update a movie",
        )


# Patch Movie (Partially Update)
@router.patch(
    "/{movie_id}",
    response_model=Optional[movies_schemas.MovieDisplayOne],
)
def patch_movie(
    movie_id: int,
    movie_updates: Optional[movies_schemas.MoviePatchUpdate],
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    if oauth2.admin_authentication(token=token,):
        movie = db_movies.get_movie(db, movie_id)
        if movie is None:
            raise HTTPException(
                status_code=404, detail=f"Movie with Id :{movie_id} not found"
            )
        else:
            updated_movie = db_movies.patch_movie(
                db=db,
                movie=movie,
                request=movie_updates,
            )
    return updated_movie


# Delete Movie
@router.delete("/{movie_id}")
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    if oauth2.admin_authentication(token=token,):
        if not check_movie(db, movie_id):
            raise HTTPException(
                status_code=404, detail=f"Movie with Id :{movie_id} not found"
            )
        else:
            if db_movies.check_movie_in_reviews(db, movie_id):
                raise HTTPException(
                    status_code=409,
                    detail=f"Cannot delete movie with Id :{movie_id} , it has review/s ",
            )
        success = db_movies.delete_movie(db, movie_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Movie with Id :{movie_id} could not be deleted",
            )
        return f"Movie with id: {movie_id} deleted successfully"


# Return Movie Categories
@router.get(
    "/{movie_id}/categories/",
)
def get_movie_categories(
    db: Session = Depends(get_db),
    movie: movies_schemas.MovieDisplayOne = Depends(get_movie_by_id),
    categories: List[categories_schemas.CategoryDisplay] = Depends(categories.get_all_categories),
):
    return movie.categories

# =========================== Movie And Actors ========================


# Return Movie Actors
@router.get(
    "/{movie_id}/actors",
    response_model=List[actors_schemas.ActorDisplayAll],
)
def get_movie_actors(
    db: Session = Depends(get_db),
    movie: movies_schemas.MovieDisplayOne = Depends(get_movie_by_id),
):

    return [actors_schemas.ActorDisplayAll.model_validate(actor) for actor in movie.actors]


# # Return Specific Movie Actor
# @router.get(
#     "/{movie_id}/actors/{actor_id}",
#     response_model=actors_schemas.ActorDisplayOne,
# )
# def get_specific_movie_actor(
#     movie: movies_schemas.MovieDisplayOne = Depends(get_movie_by_id),
#     actor: actors_schemas.ActorDisplayAll = Depends(actors.get_actor_by_id),
# ):
#     for movie_actor in movie.actors:
#         if movie_actor.id == actor.id:
#             return actor

#     raise HTTPException(
#         status_code=404,
#         detail=f"Actor: {actor.actor_name} ID: {actor.id} not in the movie.",
#     )


# # Add actor in the movie
# @router.patch(
#     "/{movie_id}/actors/{actor_id}",
#     response_model=actors_schemas.ActorDisplayOne,
#     status_code=status.HTTP_201_CREATED,
# )
# def add_actor_in_movie(
#     actor_id: int,
#     movie: movies_schemas.MovieDisplayOne = Depends(get_movie_by_id),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_schema),
# ):

#     return actors.patch_actor(
#         request=actors_schemas.ActorPatch(movies=[movie.id]),
#         actor=actors.get_actor_by_id(actor_id=actor_id, db=db),
#         db=db,
#         token=token,
#     )


# # ============================ Movie and Director =====================
# Return Movie Director
@router.get(
    "/{movie_id}/director",
    response_model=directors_schemas.DirectorDisplayOne,
)
def get_movie_director(movie: movies_schemas.MovieDisplayOne = Depends(get_movie_by_id)):
    return directors_schemas.DirectorDisplayOne.model_validate(movie.director)

# # Patch Movie Director
# @router.patch(
#     "/{movie_id}/director",
#     response_model=directors_schemas.DirectorDisplayOne,
# )
# def patch_movie_director(
#     director: directors_schemas.DirectorUpdateMovie,
#     movie: movies_schemas.MovieDisplayOne = Depends(get_movie_by_id),
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2.oauth2_schema),
# ):
#     if oauth2.admin_authentication(token=token):
#         if check_movie(db, movie.id):
#             return db_movies.patch_movie_director(
#                 db=db,
#                 movie=movie,
#                 request=director,
#             )
#         else:
#             raise HTTPException(
#                 status_code=404, detail=f"Movie with Id :{movie.id} not found"
#             )
  
# ============================ Movie and Poster =====================

# Upload Movie Poster Image
@router.post("/upload_poster/{movie_id}")
async def upload_file(
    movie_id: int,
    upload_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    file_extension = os.path.splitext(upload_file.filename)[-1]  # get file extension
    if file_extension not in [".jpg", ".png"]:
        return "Invalid file type. Please upload a jpg or png file."

    movie = db_movies.get_movie(db, movie_id)
    title = movie.title.replace(" ", "_")  # replace spaces with underscores
    new_filename = f"{movie_id}_{title}{file_extension}"  # create new filename

    contents = await upload_file.read()

    # Check if the directory exists and if not, create it
    directory = "assets/posters"
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(f"{directory}/{new_filename}", "wb") as f:
        f.write(contents)

    file_path = os.path.abspath(f"{directory}/{new_filename}")

    result = update_movie_poster_url(db, movie, file_path)
    if result is True:
        return f"File uploaded successfully. The file path is: {file_path} "
    else:
        return f"File uploaded successfully. But the file path could not be updated in the database."


# Get Extra Data for a Movie by IMDB Id
@router.get("/extra_data/{movie_id}", response_model=movies_schemas.MovieExtraData)
async def get_movie_extra(
    movie_id: int,
    db: Session = Depends(get_db),
):
    if check_movie(db, movie_id) is False:
        raise HTTPException(
            status_code=404, detail=f"Movie with Id :{movie_id} not found"
        )
    else:
        return await db_movies.get_movie_extra(db=db, movie_id=movie_id)


# Auto Add Movies
@router.post("/auto_add_movies")
def auto_add_movies(db: Session = Depends(get_db)):
    """
    THIS IS ONLY TO BE USED FOR TESTING PURPOSES
    """
    import json

    with open("sampleData/example_movies.json", "r") as file:
        movies = json.load(file)
    for movie in movies:
        db_movies.create_movie(db=db, movie=movies_schemas.MovieBase(**movie))
    return {"message": "Movies added successfully"}
