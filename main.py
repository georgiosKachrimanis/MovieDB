from fastapi import FastAPI
from routes import movieDB_get
from routes import movieDB_post
from routes import user
from routes import review
from db import models
from db.database import engine

app = FastAPI()
# app.include_router(movieDB_get.router)
# app.include_router(movieDB_post.router)
app.include_router(user.router)
app.include_router(review.router)


@app.get("/")
def index():
    return {"message": "Welcome to Movie DB!"}


models.Base.metadata.create_all(engine)
"""
    ---> You NEED TO DECLARE THE TYPE IN THE FUNCTIONS <---
"""
