from fastapi import FastAPI
# from routes import movieDB_get
# from routes import movieDB_post
from routes import user,review
from db import models
from db.database import engine

app = FastAPI()
#app.include_router(movieDB_get.router)
# app.include_router(blog_post.router)
app.include_router(user.router)
app.include_router(review.router)





models.Base.metadata.create_all(engine)
"""
    ---> You NEED TO DECLARE THE TYPE IN THE FUNCTIONS <---
"""