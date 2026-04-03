from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.api.db.database import Base

class MarkdownDoc(Base):
    __tablename__ = "markdown_docs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(512), nullable=True)
    author_id = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class MarkdownImage(Base):
    __tablename__ = "markdown_images"
    id = Column(Integer, primary_key=True)
    filename = Column(String(255))
    url = Column(String(512))
    doc_id = Column(Integer, index=True)
    created_at = Column(DateTime, server_default=func.now())


class UserMarkdownFavorite(Base):
    __tablename__ = "user_markdown_favorites"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    doc_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())