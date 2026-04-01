from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.api.db.base import Base

class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    target_type = Column(String(20), nullable=False, default="project")
    target_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_delete = Column(Boolean, default=False)

class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    target_type = Column(String(20), nullable=False, default="project")
    target_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_delete = Column(Boolean, default=False)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    target_type = Column(String(20), nullable=False, default="project")
    target_id = Column(Integer, nullable=False)
    parent_id = Column(Integer, default=0)
    content = Column(String(500), nullable=False)
    status = Column(String(20), default="pending")
    is_delete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, index=True)
    to_user_id = Column(Integer, nullable=False)
    from_user_id = Column(Integer, nullable=False)
    project_id = Column(Integer, nullable=False)
    comment_id = Column(Integer, nullable=False)
    content = Column(String(500), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)