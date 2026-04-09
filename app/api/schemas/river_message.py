from pydantic import BaseModel
from datetime import datetime

class RiverMessageCreate(BaseModel):
    name: str
    image: str

class RiverMessageResponse(BaseModel):
    id: int
    name: str
    image: str
    create_time: datetime

    class Config:
        from_attributes = True