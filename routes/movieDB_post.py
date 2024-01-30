from typing import Dict, List, Optional
from fastapi import APIRouter, Body, Path, Query

from schemas.movie_schemas import MovieBase, MovieCategory

router = APIRouter(prefix="/movie", tags=["movie"])


# @router.post("/new")
# def create_blog(blog: BlogModel):
#     return {'data: ': blog}


@router.post("/new/{id}")
def create_blog(movie: MovieBase, id: int, version: int = 1):
    return {"Data: ": movie, "ID:": id, "Version": version}


@router.post("/new/{id}/comment/{comment_id}")
def create_comment(
    movie: MovieBase,
    id: int,
    comment_title: int = Query(
        None,
        title="Title of the comment",
        description="Some Description about the comment!",
        alias="commentTitle",
    ),
    # We can have a default value:
    # content: str = Body("Hello my friend!")
    # If we want to make the value required:
    # or Body(Ellipsis)
    content: str = Body(
        ...,
        min_length=20,
        max_length=30,
        regex="^[a-z\\s]*$",
    ),
    ver: List[str] = Query(["1.0", "1.1", "1.2"]),
    comment_id: int = Path(Ellipsis, gt=5, le=10),
):
    return {
        "Data": movie,
        "ID": id,
        "Comment Title": comment_title,
        "Content": content,
        "Version": ver,
        "Comment ID": comment_id,
    }


def required_functionality():
    return {"message": "Learning FastAPI is important!"}
