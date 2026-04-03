from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.api.db.database import Base

class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_a_id = Column(Integer, nullable=False)
    user_b_id = Column(Integer, nullable=False)
    last_message = Column(Text)
    last_message_time = Column(DateTime, server_default=func.now())
    unread_count_a = Column(Integer, default=0)
    unread_count_b = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, nullable=False)
    sender_id = Column(Integer, nullable=False)
    content = Column(Text)
    msg_type = Column(String(20), default="text")
    file_url = Column(String(512))
    file_name = Column(String(255))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())