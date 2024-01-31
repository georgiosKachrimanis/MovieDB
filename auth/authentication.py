from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from db.database import get_db
from db import models
from db.hash import Hash
from auth import oauth2


router = APIRouter(tags=["authentication"])


# name needs to be the same as the  --> oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")
@router.post("/token")
def get_token(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    print(request.username)
    user = (
        db.query(models.DbUser)
        .filter(models.DbUser.username == request.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wrong credentials!"
        )
    if not Hash.verify(hashed_password=user.password, plain_password=request.password):
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT, detail="Wrong credentials!"
        )

    access_token = oauth2.create_access_token(
        data={
            "sub": user.username,
            'username': user.username,
            'user_email': user.email,
            'user_id': user.id,
            "user_type": user.user_type}
        )
    # We can add more information here like user type etc
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
    }

@router.get("/token")
def get_current_token(token: str = Depends(oauth2.oauth2_schema)):
    payload = oauth2.decode_access_token(token)
    return payload
