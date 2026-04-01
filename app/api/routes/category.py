from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.db.database import get_db
from app.api.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.api.crud.category import get_categories, get_category_by_id, create_category, update_category, delete_category

router = APIRouter()

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = get_categories(db, skip, limit)
    return categories

@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    category = get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category

@router.post("/categories/create", response_model=CategoryResponse)
def create_category_endpoint(category: CategoryCreate, db: Session = Depends(get_db)):
    c = create_category(db, category)
    if not c:
        raise HTTPException(status_code=400, detail="分类名称已存在")
    return c

@router.put("/categories/update/{category_id}", response_model=CategoryResponse)
def update_category_endpoint(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    res = update_category(db, category_id, category)
    if not res:
        raise HTTPException(status_code=404)
    return res

@router.delete("/categories/delete/{category_id}")
def delete_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    if not delete_category(db, category_id):
        raise HTTPException(status_code=404)
    return {"detail": "删除成功"}