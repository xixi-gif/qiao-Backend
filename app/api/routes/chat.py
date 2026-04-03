from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.db.database import get_db
from app.api.crud.chat import *
from app.api.schemas.chat import *
from app.api.utils.file_util import save_file
from app.api.utils.websocket import manager
from app.api.models.user import User
from typing import List

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/conversation", response_model=ChatConversationResponse)
def create_or_get_conversation(
        user_id: int = Form(...),
        to_user_id: int = Form(...),
        db: Session = Depends(get_db)
):
    if user_id == to_user_id:
        raise HTTPException(status_code=400, detail="不能和自己聊天")
    conv = get_conversation_by_users(db, user_id, to_user_id)
    if not conv:
        conv = create_conversation(db, ChatConversationCreate(
            user_a_id=user_id,
            user_b_id=to_user_id
        ))
    target = db.query(User).filter(User.id == to_user_id).first()
    if target:
        conv.target_name = target.username
        conv.target_avatar = target.avatar
    else:
        conv.target_name = "用户"
        conv.target_avatar = None
    return conv

@router.get("/conversations/{user_id}", response_model=List[ChatConversationResponse])
def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    convos = get_conversations_by_user(db, user_id)
    for conv in convos:
        if conv.user_a_id == user_id:
            conv.unread_count_user = conv.unread_count_a
        else:
            conv.unread_count_user = conv.unread_count_b
    return convos

@router.get("/conversation/{conv_id}", response_model=ChatConversationResponse)
def get_conversation_api(conv_id: int, db: Session = Depends(get_db)):
    conv = get_conversation(db, conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")
    target_id = None
    for u in db.query(User).all():
        if conv.user_a_id != u.id and conv.user_b_id == u.id:
            target_id = conv.user_a_id
        elif conv.user_b_id != u.id and conv.user_a_id == u.id:
            target_id = conv.user_b_id
    if not target_id:
        target_id = conv.user_b_id
    target = db.query(User).filter(User.id == target_id).first()
    if target:
        conv.target_name = target.username
        conv.target_avatar = target.avatar
    else:
        conv.target_name = "用户"
        conv.target_avatar = None
    return conv

@router.get("/conversation/{conv_id}/messages", response_model=List[ChatMessageResponse])
def get_conversation_messages(conv_id: int, db: Session = Depends(get_db)):
    return get_messages_by_conversation(db, conv_id)

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
        conversation_id: int = Form(...),
        sender_id: int = Form(...),
        content: str = Form(None),
        msg_type: str = Form("text"),
        file_url: str = Form(None),
        file_name: str = Form(None),
        db: Session = Depends(get_db)
):
    msg = create_message(db, ChatMessageCreate(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content,
        msg_type=msg_type,
        file_url=file_url,
        file_name=file_name
    ))
    sender = db.query(User).filter(User.id == sender_id).first()
    if sender:
        msg.sender_name = sender.username
        msg.sender_avatar = sender.avatar
    else:
        msg.sender_name = "用户"
        msg.sender_avatar = None
    conv = get_conversation(db, conversation_id)
    if conv:
        conv.last_message = content or file_name
        conv.last_message_time = msg.created_at
        target_id = conv.user_b_id if conv.user_a_id == sender_id else conv.user_a_id
        if conv.user_a_id == sender_id:
            conv.unread_count_b += 1
        else:
            conv.unread_count_a += 1
        db.commit()
        await manager.send_personal_message({
            "type": "message",
            "conversation_id": conversation_id,
            "message": {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "sender_id": msg.sender_id,
                "sender_name": msg.sender_name,
                "sender_avatar": msg.sender_avatar,
                "content": msg.content,
                "msg_type": msg.msg_type,
                "file_url": msg.file_url,
                "file_name": msg.file_name,
                "is_read": msg.is_read,
                "created_at": msg.created_at.isoformat()
            }
        }, target_id)
    return msg

@router.put("/conversation/{conv_id}/read")
def mark_read(conv_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    mark_messages_read(db, conv_id, user_id)
    return {"ok": True}

@router.put("/conversation/{conv_id}/pin", response_model=ChatConversationResponse)
def toggle_pin(conv_id: int, db: Session = Depends(get_db)):
    conv = toggle_conversation_pin(db, conv_id)
    target_id = conv.user_b_id
    target = db.query(User).filter(User.id == target_id).first()
    if target:
        conv.target_name = target.username
        conv.target_avatar = target.avatar
    else:
        conv.target_name = "用户"
        conv.target_avatar = None
    return conv

@router.post("/upload", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    suffix = file.filename.split(".")[-1].lower()
    file_data = await file.read()
    url = save_file(file_data, suffix)
    return {"url": url, "name": file.filename}