from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, jwt

SECRET_KEY = "ee86333ec6dba1dc30160f672544010416321d64252950a0f253d13c02118909"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 15

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="token",
    auto_error=False,
)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload  # or return specific user data as needed
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )


# Authenticating Admin User!
def admin_authentication(
    token: str,
    detail: str,
):
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Only authenticated users allowed.",
        )
    if decode_access_token(token=token).get("user_type") != "admin":
        raise HTTPException(
            status_code=401,
            detail=detail,
        )
