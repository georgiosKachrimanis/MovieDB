from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import (
    directors,
    reviews,
    users,
    movies,
    categories,
    actors,
)
from auth import authentication
from db import models
from db.database import engine
from db.seed_db import create_tables_and_seed


app = FastAPI(
    title="MoviesDB API",
    description="This is an movie DB API from the 40+ of the group!",
    version="1.4.0",
)

origins = ["http://localhost:3000"]

app.include_router(movies.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(categories.router)
app.include_router(directors.router)
app.include_router(actors.router)
app.include_router(authentication.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/assets/posters",
    StaticFiles(directory="assets/posters"),
    name="assets-posters",
)


@app.get("/")
def index():
    return {"message": "Welcome to Movie DB!"}


models.Base.metadata.create_all(engine)

# Auto creating the Movie Categories
create_tables_and_seed()
