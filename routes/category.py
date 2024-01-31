from fastapi import HTTPException, Depends, APIRouter
from db.database import get_db
from sqlalchemy.orm import Session
from db import db_category
from typing import List
from schemas import CategoryBase, CategoryDisplay

router = APIRouter(
    prefix='/category',
    tags=['Category Endpoints']
)



# CRUD Operations for Category
# Create Category
@router.post('/add', response_model=CategoryBase, status_code=201)
def create_category(category_name: str, db: Session = Depends(get_db)):
    return db_category.add_category(db, category_name)

# Get All Categories
@router.get('/', response_model=List[CategoryDisplay])
def read_all_categories(db: Session = Depends(get_db)):
    return db_category.get_all_categories(db)

# Get Category By Id
@router.get('/{category_id}', response_model=CategoryDisplay)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = db_category.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail='Category not found')
    return category

# Update Category
@router.put('/update/{category_id}', response_model=CategoryBase)
def update_category(category_id: int, category_name: str, db: Session = Depends(get_db)):
    category = db_category.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail='Category not found')
    return update_category(db, category_id, category_name)


# Delete Category
@router.delete('/delete/{category_id}', response_model=CategoryDisplay)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db_category.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail='Category not found')
    return delete_category(db, category_id)
