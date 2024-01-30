from db.database import get_db
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter
from db.db_category import get_category, get_all_categories, update_category, delete_category, add_category
from typing import List
from schemas import CategoryBase, CategoryDisplay

router = APIRouter(
    prefix='/category',
    tags=['Category Endpoints']
)

router.post('/add', response_model=CategoryBase, status_code=201)
def create_category(category_name: str, db: Session = Depends(get_db)):
    return add_category(db, category_name)

router.get('/', response_model=List[CategoryDisplay])
def read_all_categories(db: Session = Depends(get_db)):
    return get_all_categories(db)


router.get('/{category_id}', response_model=CategoryDisplay)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail='Category not found')
    return category


router.put('/update/{category_id}', response_model=CategoryBase)
def update_category(category_id: int, category_name: str, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail='Category not found')
    return update_category(db, category_id, category_name)

router.delete('/delete/{category_id}', response_model=CategoryDisplay)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail='Category not found')
    return delete_category(db, category_id)
