from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.api.db.base import Base

class Checkin(Base):
    __tablename__ = "checkins"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    image = Column(String(255), nullable=True)
    tags = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    view_count = Column(Integer, default=0)
    user = relationship("User", back_populates="checkins")