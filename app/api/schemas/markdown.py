from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MarkdownDocCreate(BaseModel):
    title: str
    content: str

class MarkdownDocUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class MarkdownDocResponse(BaseModel):
    id: int
    title: str
    content: str
    file_path: Optional[str]
    author_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True