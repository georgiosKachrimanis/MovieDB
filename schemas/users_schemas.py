from pydantic import BaseModel, EmailStr


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserTypeUpdate(BaseModel):
    user_type: str


class UserTypeDisplay(BaseModel):
    user_type: str

    class Config:
        from_attributes = True


class UserDisplay(BaseModel):
    username: str
    email: EmailStr
    user_type: str

    class Config:
        from_attributes = True


# User inside Reviews
class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
