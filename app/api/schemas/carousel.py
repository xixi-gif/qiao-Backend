from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CarouselBase(BaseModel):
    title:str
    description:Optional[str]=None
    link:Optional[str]=None
    sort_num:int=0
    is_active:bool=True

class CarouselCreate(CarouselBase):
    pass

class CarouselUpdate(CarouselBase):
    pass

class CarouselResponse(CarouselBase):
    id:int
    image_path:str
    created_at:datetime
    updated_at:datetime
    class Config:orm_mode=True