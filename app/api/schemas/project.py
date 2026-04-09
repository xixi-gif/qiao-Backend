from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ProjectCreate(BaseModel):
    title: str
    category: str
    tags: List[str]
    address: str
    start_time: datetime
    end_time: datetime
    price: float
    max_people: int
    description: str
    contact: str

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    address: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    price: Optional[float] = None
    max_people: Optional[int] = None
    description: Optional[str] = None
    contact: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    title: str
    category: str
    tags: str
    cover: Optional[str] = None
    address: str
    start_time: datetime
    end_time: datetime
    price: float
    max_people: int
    description: str
    contact: str
    status: str
    merchant_id: int
    views: int
    orders: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True