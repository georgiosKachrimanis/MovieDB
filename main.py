from fastapi import FastAPI
from routes import categories, directors, movies, reviews, users,actors
from auth import authentication
from db import models
from db.database import engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(movies.router)
app.include_router(reviews.router)
app.include_router(categories.router)
app.include_router(directors.router)
app.include_router(actors.router)

models.Base.metadata.create_all(engine)

origins = ['http://localhost:3000']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/assets/posters', StaticFiles(directory='assets/posters'),name='assets-posters')