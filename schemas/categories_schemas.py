from pydantic import BaseModel

class CategoryBase(BaseModel):
    category_name: str

class CategoryDisplay(BaseModel):
    id: int
    category_name: str
    class Config:
        from_attributes = True   

 