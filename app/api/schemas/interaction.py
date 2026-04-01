from pydantic import BaseModel
from datetime import datetime

class FavoriteCreate(BaseModel):
    project_id:int

class LikeCreate(BaseModel):
    project_id:int

class CommentCreate(BaseModel):
    project_id:int
    content:str
    parent_id: int | None = None

class CommentOut(BaseModel):
    id:int
    user_id:int
    project_id:int
    content:str
    status:str
    created_at:datetime
    class Config:
        orm_mode=True