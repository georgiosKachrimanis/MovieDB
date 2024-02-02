from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi.param_functions import Depends
from db.database import get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from db import models


router = APIRouter(
    tags=['authentication'], 

)

# @router.post("/token")
# def get_token(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#   user = db.query(models.User).filter(models.User.username == request.username).first()
#   if not user:
#     raise HTTPException(status_code=status.)
