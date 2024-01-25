from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str
    password: str
    user_type: str


class UserDisplay(BaseModel):
    username: str
    email: str
    user_type: str

    class Config():
        orm_mode = True
