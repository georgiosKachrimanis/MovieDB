from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Base
from .models import DbCategory
from schemas.movies_schemas import MovieCategoryType


def seed_categories(session: Session):
    # Fetch existing categories to avoid duplicates
    existing_category_names = session.query(DbCategory.category_name).all()
    existing_category_names = {name[0] for name in existing_category_names}

    for category in MovieCategoryType:
        if category.label not in existing_category_names:
            new_category = DbCategory(category_name=category.label)
            session.add(new_category)

    session.commit()




def create_tables_and_seed():
    Base.metadata.create_all(bind=engine)  # Create database tables

    with SessionLocal() as session:
        seed_categories(session)  # Seed the categories table


# Remember to call create_tables_and_seed() at an appropriate place in your application
