from sqlalchemy.orm import Session
from app.api.models.tag import Tag
from app.api.schemas.tag import TagCreate, TagUpdate
from fastapi import HTTPException

def get_tags(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Tag).filter(Tag.is_deleted == False).order_by(Tag.sort_num).offset(skip).limit(limit).all()

def get_tag_by_id(db: Session, tag_id: int):
    return db.query(Tag).filter(Tag.id == tag_id, Tag.is_deleted == False).first()

def create_tag(db: Session, tag: TagCreate):
    exists = db.query(Tag).filter(Tag.name == tag.name, Tag.is_deleted == False).first()
    if exists:
        raise HTTPException(status_code=400, detail="标签已存在")
    db_tag = Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def update_tag(db: Session, tag_id: int, tag: TagUpdate):
    db_tag = db.query(Tag).filter(Tag.id == tag_id, Tag.is_deleted == False).first()
    if not db_tag:
        return None
    for k, v in tag.dict(exclude_unset=True).items():
        setattr(db_tag, k, v)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def delete_tag(db: Session, tag_id: int):
    db_tag = db.query(Tag).filter(Tag.id == tag_id, Tag.is_deleted == False).first()
    if not db_tag:
        return False
    db_tag.is_deleted = True
    db.commit()
    return True