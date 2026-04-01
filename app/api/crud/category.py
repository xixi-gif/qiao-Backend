from sqlalchemy.orm import Session
from app.api.models.category import Category
from app.api.schemas.category import CategoryCreate, CategoryUpdate

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Category).filter(Category.is_deleted == False).offset(skip).limit(limit).all()

def get_category_by_id(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()

def create_category(db: Session, category: CategoryCreate):
    exists = db.query(Category).filter(Category.name == category.name, Category.is_deleted == False).first()
    if exists:
        return None
    db_category = Category(name=category.name, sort_num=category.sort_num)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category: CategoryUpdate):
    db_category = get_category_by_id(db, category_id)
    if not db_category:
        return None
    db_category.name = category.name
    db_category.sort_num = category.sort_num
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = get_category_by_id(db, category_id)
    if not db_category:
        return False
    db_category.is_deleted = True
    db.commit()
    return True