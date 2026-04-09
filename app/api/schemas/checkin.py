from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CheckinBase(BaseModel):
    title: str
    content: str
    image: Optional[str] = None
    tags: Optional[str] = None

class CheckinCreate(CheckinBase):
    pass

class CheckinUpdate(CheckinBase):
    pass

class CheckinStatusUpdate(BaseModel):
    status: str

class CheckinResponse(CheckinBase):
    id: int
    user_id: int
    username: Optional[str] = None
    avatar: Optional[str] = None
    status: str
    create_time: datetime
    update_time: datetime
    view_count: int

    class Config:
        from_attributes = True