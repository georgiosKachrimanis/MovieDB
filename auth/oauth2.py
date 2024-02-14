from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "ee86333ec6dba1dc30160f672544010416321d64252950a0f253d13c02118909"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 1000

oauth2_schema = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload  # or return specific user data as needed

# Authenticating Admin User!
def admin_authentication(token: str):
    try:
        payload = decode_access_token(token=token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="You need to log in to perform this action",
        ) from e
    if payload.get("user_type") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to perform this action",
        )
    else:
        return True
        

