from fastapi import FastAPI
from routes import movieDB_get, movieDB_post, reviews, users
from auth import authentication
from db import models
from db.database import engine

app = FastAPI(
    title="MoviesDB API",
    description="This is an movie DB API from the 40+ of the group!",
    version="1.0.0"
)
# app.include_router(movieDB_get.router)
# app.include_router(movieDB_post.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(authentication.router)


@app.get("/")
def index():
    return {"message": "Welcome to Movie DB!"}


models.Base.metadata.create_all(engine)
"""
    ---> You NEED TO DECLARE THE TYPE IN THE FUNCTIONS <---
"""
