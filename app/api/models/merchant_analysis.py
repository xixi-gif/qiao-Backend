from sqlalchemy import Column, Integer, DateTime, BigInteger
from datetime import datetime
from app.api.db.base import Base

class ProjectStat(Base):
    __tablename__ = "project_stat"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(BigInteger, nullable=False)
    project_id = Column(Integer, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    favorites = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow)