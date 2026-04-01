from sqlalchemy.orm import Session
from app.api.models.checkin import Checkin
from app.api.schemas.checkin import CheckinCreate, CheckinUpdate, CheckinStatusUpdate
from typing import List, Optional
from sqlalchemy.orm import joinedload

def get_checkin_by_id(db: Session, checkin_id: int) -> Optional[Checkin]:
    return db.query(Checkin).options(
        joinedload(Checkin.user)  # 关键：加载对应用户
    ).filter(
        Checkin.id == checkin_id,
        Checkin.is_deleted == False
    ).first()

def get_checkins_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Checkin]:
    return db.query(Checkin).filter(Checkin.user_id == user_id, Checkin.is_deleted == False).offset(skip).limit(limit).all()

def get_all_checkins(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Checkin]:
    query = db.query(Checkin).filter(Checkin.is_deleted == False)
    if status:
        query = query.filter(Checkin.status == status)
    return query.offset(skip).limit(limit).all()

def create_checkin(db: Session, user_id: int, checkin_in: CheckinCreate) -> Checkin:
    db_checkin = Checkin(**checkin_in.dict(), user_id=user_id, status="pending")
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)
    return db_checkin

def update_checkin(db: Session, checkin_id: int, checkin_in: CheckinUpdate, user_id: int) -> Optional[Checkin]:
    db_checkin = get_checkin_by_id(db, checkin_id)
    if not db_checkin or db_checkin.user_id != user_id:
        return None
    for k, v in checkin_in.dict(exclude_unset=True).items():
        setattr(db_checkin, k, v)
    db.commit()
    db.refresh(db_checkin)
    return db_checkin

def delete_checkin(db: Session, checkin_id: int, user_id: int) -> bool:
    db_checkin = get_checkin_by_id(db, checkin_id)
    if not db_checkin or db_checkin.user_id != user_id:
        return False
    db_checkin.is_deleted = True
    db.commit()
    return True

def soft_delete_checkin(db: Session, checkin_id: int):
    db_checkin = get_checkin_by_id(db, checkin_id)
    if db_checkin:
        db_checkin.is_deleted = True
        db.commit()

def update_checkin_status(db: Session, checkin_id: int, status_in: CheckinStatusUpdate) -> Optional[Checkin]:
    db_checkin = get_checkin_by_id(db, checkin_id)
    if not db_checkin:
        return None
    db_checkin.status = status_in.status
    db.commit()
    db.refresh(db_checkin)
    return db_checkin

def update_status(db: Session, checkin_id: int, status: str):
    db_checkin = get_checkin_by_id(db, checkin_id)
    if db_checkin:
        db_checkin.status = status
        db.commit()