from pydantic import BaseModel
from datetime import datetime

class CategoryCreate(BaseModel):
    name: str
    sort_num: int = 0

class CategoryUpdate(BaseModel):
    name: str
    sort_num: int = 0

class CategoryResponse(BaseModel):
    id: int
    name: str
    sort_num: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True