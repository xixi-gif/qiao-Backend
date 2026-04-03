from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from app.api.models.chat import ChatConversation, ChatMessage
from app.api.schemas.chat import ChatConversationCreate, ChatMessageCreate, ChatMessageResponse
from app.api.models.user import User

def get_conversation_by_users(db: Session, user1: int, user2: int):
    return db.query(ChatConversation).filter(
        or_(
            and_(ChatConversation.user_a_id == user1, ChatConversation.user_b_id == user2),
            and_(ChatConversation.user_a_id == user2, ChatConversation.user_b_id == user1)
        ),
        ChatConversation.is_deleted == False
    ).first()

def create_conversation(db: Session, obj_in: ChatConversationCreate):
    db_obj = ChatConversation(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_conversations_by_user(db: Session, user_id: int):
    query = db.query(ChatConversation).filter(ChatConversation.is_deleted == False)
    query = query.filter(or_(
        ChatConversation.user_a_id == user_id,
        ChatConversation.user_b_id == user_id
    ))
    convos = query.order_by(desc(ChatConversation.is_pinned), desc(ChatConversation.last_message_time)).all()
    for convo in convos:
        target_id = convo.user_b_id if convo.user_a_id == user_id else convo.user_a_id
        user = db.query(User).filter(User.id == target_id).first()
        if user:
            convo.target_name = user.username
            convo.target_avatar = user.avatar
        else:
            convo.target_name = "用户"
            convo.target_avatar = None
    return convos

def get_conversation(db: Session, conv_id: int):
    conv = db.query(ChatConversation).filter(
        ChatConversation.id == conv_id,
        ChatConversation.is_deleted == False
    ).first()
    if not conv:
        return None
    return conv

def toggle_conversation_pin(db: Session, conv_id: int):
    conv = get_conversation(db, conv_id)
    if not conv:
        return None
    conv.is_pinned = not conv.is_pinned
    db.commit()
    db.refresh(conv)
    return conv

def create_message(db: Session, obj_in: ChatMessageCreate):
    db_obj = ChatMessage(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_messages_by_conversation(db: Session, conv_id: int, skip=0, limit=100):
    db.expire_all()
    messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conv_id
    ).order_by(ChatMessage.created_at).offset(skip).limit(limit).all()

    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        sender_name = sender.username if sender else "用户"
        sender_avatar = sender.avatar if sender else None

        m = ChatMessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender_id=msg.sender_id,
            content=msg.content,
            msg_type=msg.msg_type,
            file_url=msg.file_url,
            file_name=msg.file_name,
            is_read=msg.is_read,
            created_at=msg.created_at,
            sender_name=sender_name,
            sender_avatar=sender_avatar
        )
        result.append(m)
    return result

def mark_messages_read(db: Session, conv_id: int, user_id: int):
    conv = get_conversation(db, conv_id)
    if not conv:
        return
    if conv.user_a_id == user_id:
        conv.unread_count_a = 0
    else:
        conv.unread_count_b = 0
    db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conv_id,
        ChatMessage.sender_id != user_id,
        ChatMessage.is_read == False
    ).update({"is_read": True})
    db.commit()