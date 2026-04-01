from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.db.database import get_db
from app.api.schemas.tag import TagCreate, TagUpdate, TagResponse
from app.api.crud.tag import get_tags, get_tag_by_id, create_tag, update_tag, delete_tag

router = APIRouter()

@router.get("/tags", response_model=List[TagResponse])
def get_tags_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tags = get_tags(db, skip, limit)
    for item in tags:
        item.created_at = str(item.created_at)
        item.updated_at = str(item.updated_at)
    return tags

@router.get("/tags/{tag_id}", response_model=TagResponse)
def get_tag_endpoint(tag_id: int, db: Session = Depends(get_db)):
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    tag.created_at = str(tag.created_at)
    tag.updated_at = str(tag.updated_at)
    return tag

@router.post("/tags/create", response_model=TagResponse)
def create_tag_endpoint(tag: TagCreate, db: Session = Depends(get_db)):
    t = create_tag(db, tag)
    t.created_at = str(t.created_at)
    t.updated_at = str(t.updated_at)
    return t

@router.put("/tags/update/{tag_id}", response_model=TagResponse)
def update_tag_endpoint(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db)):
    res = update_tag(db, tag_id, tag)
    if not res:
        raise HTTPException(status_code=404)
    res.created_at = str(res.created_at)
    res.updated_at = str(res.updated_at)
    return res

@router.delete("/tags/delete/{tag_id}")
def delete_tag_endpoint(tag_id: int, db: Session = Depends(get_db)):
    if not delete_tag(db, tag_id):
        raise HTTPException(status_code=404)
    return {"detail": "删除成功"}