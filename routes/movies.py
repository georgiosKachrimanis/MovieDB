from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from schemas import movies_schemas,reviews_schemas
from db import db_movies, db_reviews
from auth import oauth2
import os
from db.db_movies import update_movie_poster_url
from routes import reviews
from services.movie_service import get_movie_extra_data


router = APIRouter(prefix="/movie", tags=["Movie Endpoints"])

AUTHENTICATION_TEXT = "You are not authorized to add, edit or delete a movie!"
# CRUD Operations for Movie
# Create Movie
@router.post("/", response_model=movies_schemas.MovieDisplayOne)
def create_movie(
    movie: movies_schemas.MovieBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):

    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create a movie",
        )
    else:
        return db_movies.create_movie(db, movie)


# Get All Movies
@router.get("/", response_model=List[movies_schemas.MovieDisplayAll])
def read_all_movies(db: Session = Depends(get_db)):
    try:
        return db_movies.get_all_movies(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get Movie By Id
@router.get("/{movie_id}", response_model=movies_schemas.MovieDisplayOne)
def read_movie_by_id(
    movie_id: int, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
    ):
    payload = oauth2.decode_access_token(token=token)
    user_id = payload.get("user_id")
    try:
        movie = db_movies.get_movie(db, movie_id, user_id)
        if movie is None:
            raise HTTPException(
                status_code=404, detail="Movie with Id :{movie_id} not found"
            )
        return movie
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{movie_id}", response_model=Optional[movies_schemas.MovieDisplayOne])
def update_movie(
    movie_id: int,
    movie: movies_schemas.MovieUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") == "admin":
        movie = db_movies.get_movie(db, movie_id)
        if movie is None:
            raise HTTPException(
                status_code=404, detail="Movie with Id :{movie_id} not found"
            )
        return db_movies.update_movie(db, movie_id, movie)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create a movie",
        )

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

@router.delete("/{movie_id}")
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    if payload.get("user_type") == "admin":
        if db_movies.check_movie_in_reviews(db, movie_id):
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete movie with Id :{movie_id} , it has review/s ",
            )
        success = db_movies.delete_movie(db, movie_id)
        if not success:
            raise HTTPException(
                status_code=404, detail=f"Movie with Id :{movie_id} not found"
            )
        return f"Movie with id: {movie_id} deleted successfully"
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete a movie",
        )


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


# Create Review for A Movie by Movie Id
@router.post(
    "/{movie_id}/reviews/",
    response_model=reviews_schemas.ReviewDisplayOne,
    status_code=status.HTTP_201_CREATED,
)
def post_review_for_movie(
    review_request: reviews_schemas.ReviewUpdate,
    movie: movies_schemas.MovieBase = Depends(read_movie_by_id),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2.oauth2_schema),
):
    payload = oauth2.decode_access_token(token=token)
    new_review = reviews_schemas.ReviewBase(
        review_content=review_request.review_content,
        user_id=payload.get("user_id"),  # Provide a valid value for user_id
        movie_id=movie.id,
        movie_rate =review_request.movie_rate,
        
    )
    return reviews.create_review(
        request=new_review,
        db=db,
        token=token,
    )

# Get Extra Data for a Movie by IMDB Id
@router.get("/extra_data/{movie_id}",response_model=movies_schemas.MovieExtraData)
async def get_movie_extra(
    movie_id: int,
    db: Session = Depends(get_db),):
    return await db_movies.get_movie_extra(db=db, movie_id=movie_id)