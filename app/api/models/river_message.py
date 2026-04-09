from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.api.db.base import Base

class RiverMessage(Base):
    __tablename__ = "river_message"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    image = Column(String(255), nullable=False)
    create_time = Column(DateTime, default=func.now())
    is_deleted = Column(Boolean, default=False)