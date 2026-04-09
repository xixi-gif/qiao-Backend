from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.db.database import get_db
from app.api.models.river_message import RiverMessage
from app.api.schemas.river_message import RiverMessageCreate, RiverMessageResponse
from typing import List

router = APIRouter()

@router.get("/river/images")
def get_river_images():
    return [
        "http://127.0.0.1:8090/static/river/1.jpg",
        "http://127.0.0.1:8090/static/river/2.jpg",
        "http://127.0.0.1:8090/static/river/3.jpg",
        "http://127.0.0.1:8090/static/river/4.jpg",
        "http://127.0.0.1:8090/static/river/5.jpg",
        "http://127.0.0.1:8090/static/river/6.jpg"
    ]

@router.get("/river/messages", response_model=List[RiverMessageResponse])
def get_messages(db: Session = Depends(get_db)):
    return db.query(RiverMessage).filter(RiverMessage.is_deleted==False).all()

@router.post("/river/messages", response_model=RiverMessageResponse)
def create_message(msg: RiverMessageCreate, db: Session = Depends(get_db)):
    if not msg.name or not msg.image:
        raise HTTPException(status_code=400)
    m = RiverMessage(name=msg.name, image=msg.image)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

@router.delete("/river/messages/{msg_id}")
def delete_message(msg_id: int, db: Session = Depends(get_db)):
    msg = db.query(RiverMessage).filter(RiverMessage.id==msg_id).first()
    if not msg:
        raise HTTPException(status_code=404)
    msg.is_deleted = True
    db.commit()
    return {"detail": "删除成功"}

@router.post("/river/messages/batch_delete")
def batch_delete(body: dict, db: Session = Depends(get_db)):
    ids = body.get("ids", [])
    if not ids:
        raise HTTPException(status_code=400)
    db.query(RiverMessage).filter(RiverMessage.id.in_(ids)).update({RiverMessage.is_deleted: True})
    db.commit()
    return {"detail": "批量删除成功"}