from sqlalchemy.orm import Session
from db.models import DbCategory
from schemas.categories_schemas import CategoryBase


# Create Category
def add_category(
    db: Session,
    category_name: str,
):
    category = DbCategory(category_name=category_name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# Get All Categories
def get_all_categories(db: Session):
    return db.query(DbCategory).all()


# Get Category By Id
def get_category_with_id(
    db: Session,
    category_id: int,
):
    return db.query(DbCategory).filter(DbCategory.id == category_id).first()


def get_category_with_name(
    db: Session,
    category_name: str,
):
    return (
        db.query(DbCategory)
        .filter(DbCategory.category_name == category_name)
        .first()
        .id
    )


# Update Category
def update_category(
    db: Session,
    category_id: int,
    request: CategoryBase,
):
    category = get_category_with_id(db, category_id)
    if category:
        category.category_name = request.category_name
        db.commit()
        db.refresh(category)
    return category


# Delete Category
def delete_category(
    db: Session,
    category_id: int,
):
    category = get_category_with_id(db, category_id)
    if category:
        db.delete(category)
        db.commit()
        return True
    return False
