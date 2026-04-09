from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.api.db.database import get_db
from app.api.crud.checkin import get_checkin_by_id, get_checkins_by_user, get_all_checkins, create_checkin, \
    update_checkin, delete_checkin, update_status
from app.api.schemas.checkin import CheckinCreate, CheckinUpdate, CheckinResponse
from app.api.services.auth import get_current_user
from app.api.models.user import User, UserRole
from pydantic import BaseModel
from typing import List
import os
import uuid
import json
from app.api.core.redis_client import cache_get, cache_set, cache_delete
from datetime import datetime

router = APIRouter()


class BatchAuditRequest(BaseModel):
    ids: List[int]
    status: str


@router.get("/checkin/my", response_model=list[CheckinResponse])
def get_my_checkins(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_checkins_by_user(db, current_user.id)


@router.get("/checkin/wall", response_model=list[CheckinResponse])
def get_checkin_wall(
    title: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    cache_key = f"checkin:wall:{skip}:{limit}:{title}"
    cached = cache_get(cache_key)
    if cached:
        return json.loads(cached)

    from app.api.models.checkin import Checkin
    query = db.query(Checkin).filter(Checkin.status == "approved", Checkin.is_deleted == False)

    # 搜索功能（我只加了这一段）
    if title:
        query = query.filter(Checkin.title.contains(title))

    data = query.order_by(Checkin.create_time.desc()).offset(skip).limit(limit).all()

    res = []
    for c in data:
        user = db.query(User).filter(User.id == c.user_id).first()
        res.append({
            "id": c.id,
            "title": c.title,
            "content": c.content,
            "image": c.image,
            "tags": c.tags,
            "user_id": c.user_id,
            "username": user.username if user else None,
            "avatar": user.avatar if user else None,
            "status": c.status,
            "create_time": c.create_time.isoformat() if isinstance(c.create_time, datetime) else c.create_time,
            "update_time": c.update_time.isoformat() if isinstance(c.update_time, datetime) else c.update_time,
            "view_count": c.view_count
        })
    cache_set(cache_key, json.dumps(res), ex=60)
    return res


@router.get("/checkin/admin/all", response_model=list[CheckinResponse])
def admin_get_all_checkins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403)
    from app.api.models.checkin import Checkin
    data = db.query(Checkin).filter(Checkin.is_deleted == False).offset(skip).limit(limit).all()
    return data


@router.put("/checkin/admin/batch-audit")
def admin_batch_audit_checkins(body: BatchAuditRequest, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403)
    from app.api.models.checkin import Checkin
    for item in db.query(Checkin).filter(Checkin.id.in_(body.ids)).all():
        item.status = body.status
    db.commit()
    cache_delete("checkin:*")
    return {"msg": "成功"}


@router.get("/checkin/{id}", response_model=CheckinResponse)
def get_checkin(id: int, db: Session = Depends(get_db)):
    cache_key = f"checkin:detail:{id}"
    cached = cache_get(cache_key)
    if cached:
        return json.loads(cached)

    c = get_checkin_by_id(db, id)
    if not c:
        raise HTTPException(status_code=404)
    user = db.query(User).filter(User.id == c.user_id).first()
    c.view_count += 1
    db.commit()

    data = {
        "id": c.id,
        "title": c.title,
        "content": c.content,
        "image": c.image,
        "tags": c.tags,
        "user_id": c.user_id,
        "username": user.username if user else None,
        "avatar": user.avatar if user else None,
        "status": c.status,
        "create_time": c.create_time.isoformat() if isinstance(c.create_time, datetime) else c.create_time,
        "update_time": c.update_time.isoformat() if isinstance(c.update_time, datetime) else c.update_time,
        "view_count": c.view_count
    }
    cache_set(cache_key, json.dumps(data), ex=60)
    return data


@router.post("/checkin", response_model=CheckinResponse)
def create(title: str = Form(...), content: str = Form(...), tags: str = Form(None), image: UploadFile = File(None),
           db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    image_path = None
    if image:
        file_ext = os.path.splitext(image.filename)[-1].lower()
        file_name = f"checkin_{uuid.uuid4().hex}{file_ext}"
        save_dir = "static/checkin"
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        image_path = f"/static/checkin/{file_name}"
    data = CheckinCreate(title=title, content=content, image=image_path, tags=tags)
    res = create_checkin(db, current_user.id, data)
    cache_delete("checkin:*")
    return res


@router.put("/checkin/{id}", response_model=CheckinResponse)
def update_checkin_api(id: int, data: CheckinUpdate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    ci = update_checkin(db, id, data, current_user.id)
    if not ci:
        raise HTTPException(status_code=403)
    cache_delete("checkin:*")
    return ci


@router.delete("/checkin/{id}")
def delete_checkin_api(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkin = get_checkin_by_id(db, id)
    if not checkin:
        raise HTTPException(status_code=404)
    is_admin = current_user.role.value == "admin"
    success = delete_checkin(db, id, current_user.id, is_admin)
    if success:
        cache_delete("checkin:*")
        return {"msg": "ok"}
    raise HTTPException(status_code=403)


@router.put("/checkin/admin/{id}/status")
def admin_status(id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403)
    update_status(db, id, status)
    cache_delete("checkin:*")
    return {"msg": "ok"}