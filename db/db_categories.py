from .models import Category
from sqlalchemy.orm import Session
from schemas import categories_schemas
from db.models import movie_categories
from sqlalchemy import select

# Create Category
def create_category(db: Session, category_name: str):
    category = Category(category_name=category_name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

# Get All Categories
def get_all_categories(db: Session):
    return db.query(Category).all()

# Get Category By Id
def get_category(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()


# Update Category
def update_category(db: Session, category_id: int, request: categories_schemas.CategoryBase):
    category = get_category(db, category_id)
    if category:
        category.category_name = request.category_name
        db.commit()
        db.refresh(category)
    return category

# Delete Category
def delete_category(db: Session, category_id: int):
    category = get_category(db, category_id)
    if category:
        db.delete(category)
        db.commit()
        return True
    return False

# Check if director is in any movie
def check_category_in_movie(db: Session, category_id: int) -> bool:
    return db.query(Category).filter(Category.id == category_id).first().movies != []