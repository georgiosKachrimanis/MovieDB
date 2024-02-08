from fastapi import FastAPI
from routes import reviews, users, movies, categories
from auth import authentication
from db import models
from db.database import engine
from db.seed_db import create_tables_and_seed

app = FastAPI(
    title="MoviesDB API",
    description="This is an movie DB API from the 40+ of the group!",
    version="1.3.0",
)

app.include_router(movies.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(categories.router)
app.include_router(authentication.router)


@app.get("/")
def index():
    return {"message": "Welcome to Movie DB!"}


models.Base.metadata.create_all(engine)

# Auto creating the Movie Categories
create_tables_and_seed()


"""
    ---> You NEED TO DECLARE THE TYPE IN THE FUNCTIONS <---
"""
