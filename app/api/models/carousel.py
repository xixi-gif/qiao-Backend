from sqlalchemy import Column,Integer,String,Boolean,DateTime
from datetime import datetime
from app.api.db.base import Base

class Carousel(Base):
    __tablename__="carousels"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String(100),nullable=False)
    description=Column(String(500),nullable=True)
    image_path=Column(String(255),nullable=False)
    link=Column(String(255),nullable=True)
    sort_num=Column(Integer,default=0)
    is_active=Column(Boolean,default=True)
    is_deleted=Column(Boolean,default=False)
    created_at=Column(DateTime,default=datetime.utcnow)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)