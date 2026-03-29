from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.api.db.base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    tags = Column(String(500), nullable=True)
    cover = Column(String(255), nullable=True)
    address = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    max_people = Column(Integer, nullable=False)
    description = Column(String(2000), nullable=False)
    contact = Column(String(100), nullable=False)
    status = Column(String(20), default="pending")
    merchant_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    views = Column(Integer, default=0)
    orders = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)

    merchant = relationship("User", back_populates="projects")