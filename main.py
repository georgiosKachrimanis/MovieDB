from fastapi import FastAPI
from routes import user,review,movie,category
from db import models
from db.database import engine

app = FastAPI()

app.include_router(user.router)
app.include_router(movie.router)
app.include_router(review.router)
app.include_router(category.router)




models.Base.metadata.create_all(engine)
"""
    ---> You NEED TO DECLARE THE TYPE IN THE FUNCTIONS <---
"""