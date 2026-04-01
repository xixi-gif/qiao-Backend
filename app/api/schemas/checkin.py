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
    view_count: int  # 👈 加上浏览量

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            username=obj.user.username if obj.user else "",
            avatar=obj.user.avatar if obj.user else None,
            title=obj.title,
            content=obj.content,
            image=obj.image,
            tags=obj.tags,
            status=obj.status,
            create_time=obj.create_time,
            update_time=obj.update_time,
            view_count=obj.view_count,
        )

    class Config:
        from_attributes = True