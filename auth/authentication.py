from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from db.database import get_db
from db import models
from db.hash import Hash
from auth import oauth2


router = APIRouter(tags=["Authentication Endpoints"])


# name like this --> oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")
@router.post("/token")
def get_token(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return an access token.

    This endpoint verifies user credentials (username and password) and,
    upon successful authentication,
    generates and returns an OAuth2 access token. This token can be used for
    subsequent requests that require authentication.

    Parameters:
    - request (OAuth2PasswordRequestForm): A form data including 'username'
    and 'password'.
    - db (Session, optional): The database session for executing database
    operations. Injected by FastAPI.

    Returns:
    - A JSON object containing the access token, token type, user ID,
    and username.

    Raises:
    - HTTPException: 404 error if the username does not exist in the database.
    - HTTPException: 418 error if the password is incorrect.

    The returned token should be included in the 'Authorization' header of
    subsequent requests as 'Bearer {token}'.
    """

    user = (
        db.query(models.DbUser)
        .filter(models.DbUser.username == request.username)
        .first()
    )
    if not user or not Hash.verify(
        hashed_password=user.password,
        plain_password=request.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT, detail="Wrong credentials"
        )

    access_token = oauth2.create_access_token(
        data={
            "sub": user.username,
            "username": user.username,
            "user_email": user.email,
            "user_id": user.id,
            "user_type": user.user_type,
        }
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
    """
    Decode and return the payload of the current access token.

    This endpoint decodes the provided OAuth2 access token to extract and
    return its payload. This is useful
    for services that need to validate or inspect the token's contents,
    such as user identity or permissions.

    Parameters:
    - token (str, optional): The OAuth2 token to decode. Injected by FastAPI.

    Returns:
    - The decoded payload of the access token.

    Note: This endpoint assumes the token is valid and does not perform
    any additional authentication or validation.
    """
    payload = oauth2.decode_access_token(token)
    return payload
