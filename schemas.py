from pydantic import BaseModel, EmailStr
from typing import Optional, List 
from datetime import datetime
from typing import Optional, List

# User inside ReviewDisplay
class User(BaseModel):
    id: int
    username: str

# Review inside UserDisplay
class Review(BaseModel):
    id: int
    review_content: str
    user_rate: int
    created_at: datetime

class UserBase(BaseModel):
        username: str
        email: EmailStr
        user_type: str
        password: str
        created_at: Optional[datetime] = None
    
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    user_type: Optional[str] = None
    password: Optional[str]  = None

class UserDisplay(BaseModel):
    id: int
    username: str
    email: EmailStr
    user_type: str
    created_at: Optional[datetime] = None
    reviews: List[Review] = []
    class Config:
        orm_mode = True



class ReviewDisplay(BaseModel):
    id: int
    review_content: str
    user_rate: int
    created_at: datetime
    user: User
    class Config:
        orm_mode = True



class ReviewBase(BaseModel):
    review_content: str
    user_rate: int
    user_id: int

class ReviewUpdate(BaseModel):
    review_content: Optional[str] = None
    user_rate: Optional[int] = None