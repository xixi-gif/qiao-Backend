from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.db.database import get_db
from app.api.crud.checkin import get_checkin_by_id, get_checkins_by_user, get_all_checkins, create_checkin, update_checkin, delete_checkin, soft_delete_checkin, update_status
from app.api.schemas.checkin import CheckinCreate, CheckinUpdate, CheckinResponse
from app.api.services.auth import get_current_user
from app.api.models.user import User

router = APIRouter()

@router.get("/checkin/my", response_model=list[CheckinResponse])
def get_my_checkins(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkins = get_checkins_by_user(db, current_user.id)
    return [CheckinResponse.from_orm(c) for c in checkins]

@router.get("/checkin/wall", response_model=list[CheckinResponse])
def get_checkin_wall(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    checkins = get_all_checkins(db, skip=skip, limit=limit, status="approved")
    return [CheckinResponse.from_orm(c) for c in checkins]

@router.get("/checkin/{checkin_id}", response_model=CheckinResponse)
def get_checkin(checkin_id: int, db: Session = Depends(get_db)):
    checkin = get_checkin_by_id(db, checkin_id)
    if not checkin:
        raise HTTPException(status_code=404, detail="打卡不存在")
    checkin.view_count += 1
    db.commit()
    db.refresh(checkin)
    return CheckinResponse.from_orm(checkin)

@router.post("/checkin", response_model=CheckinResponse)
def create(data: CheckinCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkin = create_checkin(db, current_user.id, data)
    return CheckinResponse.from_orm(checkin)

@router.put("/checkin/{checkin_id}", response_model=CheckinResponse)
def update(checkin_id: int, data: CheckinUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkin = update_checkin(db, checkin_id, data, current_user.id)
    if not checkin:
        raise HTTPException(status_code=403, detail="无权限或不存在")
    return CheckinResponse.from_orm(checkin)

@router.delete("/checkin/{checkin_id}")
def delete(checkin_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not delete_checkin(db, checkin_id, current_user.id):
        raise HTTPException(status_code=403, detail="无权限")
    return {"msg": "删除成功"}

@router.put("/checkin/admin/{checkin_id}/status")
def admin_update_status(checkin_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403)
    checkin = update_status(db, checkin_id, status)
    if not checkin:
        raise HTTPException(status_code=404)
    return {"msg": "更新成功"}