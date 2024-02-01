from enum import Enum
from typing import Optional
from fastapi import APIRouter, Depends, Response, status
from schemas.movies_schemas import MovieBase, MovieCategory

router = APIRouter(prefix="/movie", tags=["movie"])

""" As we now have the prefix blog, it will be recognized
    automatically to the when we get a request! No need to add it like how it
    is in the commented code bellow!
    @app.get("/blog/all", tags=["blog"])
    @router.get("/all", tags=["blog"])

    Also, now that the tags is in the router we can remove it from all the
    functions using it!
"""


def required_functionality():
    return {"message": "Learning FastAPI is important!"}
# @app.get("/blog/all", tags=["blog"])
# def get_all_blogs():
#     return {"message": "These are all the blogs!"}


# @app.get("/blog/all", tags=["blog"])
# def get_all_blogs(page=1, page_size=10):
#     return {"message": f"All {page_size} blogs on page: {page}"}


# -----> If you want to use optional parameters <-------
@router.get(
    "/all",
    summary="Retrieve all the movies in the DB",
    description="This API simulates fetching all the movies from the DB.",
    response_description="The list of available movies."
)
def get_all_movies(page=1, page_size: Optional[int] = None, req_parameter: dict = Depends(required_functionality)):
    return {"message": f"All {page_size} blogs on page: {page}", 'required message': req_parameter}


# @router.get("/{id}/comments/{comment_id}", tags=["comment"])
# def get_comments(
#     id: int, comment_id: int, valid: bool = True, username: Optional[str] = None
# ):  # <----Declare type or you will get issues!
#     """
#     Retrieve specific comment details for a given blog post.

#     This endpoint fetches details of a specific comment,
#     identified by `comment_id`, under a blog post, identified by `id`.
#     It also provides an option to filter the
#     comments based on their validity and associated username.

#     Parameters:
#     id (int): The unique identifier of the blog post.
#     comment_id (int): The unique identifier of the comment.
#     valid (bool, optional): A flag to indicate if only valid comments
#         should be returned. Defaults to True.
#     username (str, optional): The username associated with the comment.
#         Defaults to None.

#     Returns:
#     dict: A dictionary containing the details of the comment including blog ID,
#           comment ID, validity status, and the username associated (if any).
#     """
#     return {
#         "message": f"Blog_ID: {id}, has comment: {comment_id}, valid: {valid}, username: {username}"
#     }


@router.get("/type/{type}")
def get_movie_type(type: MovieCategory):  # <----Declare type or you will get issues!
    return {"message": f"This is a {type.name} movie."}


@router.get("/{id}", status_code=status.HTTP_202_ACCEPTED)
def get_movie(
    id: int, response: Response
):  # <---- Declare type otherwise you will get issues!!!
    if id < 7:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"Blog post {id} not found!"}
    else:
        response.status_code = status.HTTP_200_OK
        return {"message": f"This is the blog {id}"}
    

# TODO: Add get movies that are in more than one category.
