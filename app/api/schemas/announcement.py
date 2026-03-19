from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Union

class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    creator_id: Union[int, str] = Field(...)
    status: str = Field(default="published", pattern="^(draft|published)$")
    attachments: Optional[List[Dict[str, str]]] = Field(default=[])

    @validator("creator_id")
    def validate_creator_id(cls, v):
        try:
            return int(v)
        except (ValueError, TypeError):
            raise ValueError("创建人ID必须是整数")

    @validator("status")
    def validate_status(cls, v):
        if v not in ["draft", "published"]:
            raise ValueError("状态只能是 draft 或 published")
        return v

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    attachments: Optional[List[Dict[str, str]]] = Field(default=None)

    @validator("status")
    def validate_status(cls, v):
        if v and v not in ["draft", "published"]:
            raise ValueError("状态只能是 draft 或 published")
        return v

class AttachmentOut(BaseModel):
    id: int
    name: str
    url: str
    created_at: datetime

    class Config:
        from_attributes = True

class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: str
    creator_id: int
    status: str
    created_at: str
    updated_at: str
    attachments: List[AttachmentOut] = []

    class Config:
        from_attributes = True

    @validator("created_at", "updated_at", pre=True)
    def format_datetime(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v or ""

class ResponseModel(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[Union[AnnouncementOut, List[AnnouncementOut], dict]] = None

class UploadResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[dict] = None