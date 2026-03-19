from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.api.db.base import Base

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    creator_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    status = Column(String(20), default="published")
    is_deleted = Column(Boolean, default=False, nullable=False)

    attachments = relationship(
        "Attachment",
        back_populates="announcement",
        cascade="all, delete-orphan"
    )
    creator = relationship("User")

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    announcement_id = Column(Integer, ForeignKey("announcements.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    announcement = relationship("Announcement", back_populates="attachments")