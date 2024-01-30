from db.models import Category
from sqlalchemy.orm import Session

def add_category(db: Session, category_name: str):
    category = Category(category_name=category_name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def get_category(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()

def get_all_categories(db: Session):
    return db.query(Category).all()

def update_category(db: Session, category_id: int, category_name: str):
    category = db.query(Category).filter(Category.id == category_id).first()
    category.category_name = category_name
    db.commit()
    db.refresh(category)
    return category

def delete_category(db: Session, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()
    db.delete(category)
    db.commit()
    return category
