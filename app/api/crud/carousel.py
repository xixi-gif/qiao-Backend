from sqlalchemy.orm import Session
from app.api.models.carousel import Carousel
from app.api.schemas.carousel import CarouselCreate,CarouselUpdate
from typing import List,Optional

def get_carousels(db:Session,skip:int=0,limit:int=10,is_active:Optional[bool]=True)->List[Carousel]:
    query=db.query(Carousel).filter(Carousel.is_deleted==False)
    if is_active is not None:
        query=query.filter(Carousel.is_active==is_active)
    return query.order_by(Carousel.sort_num.asc()).offset(skip).limit(limit).all()

def get_carousel_by_id(db:Session,carousel_id:int)->Optional[Carousel]:
    return db.query(Carousel).filter(Carousel.id==carousel_id,Carousel.is_deleted==False).first()

def create_carousel(db:Session,carousel:CarouselCreate,image_path:str)->Carousel:
    db_carousel=Carousel(title=carousel.title,description=carousel.description,image_path=image_path,link=carousel.link,sort_num=carousel.sort_num,is_active=carousel.is_active)
    db.add(db_carousel)
    db.commit()
    db.refresh(db_carousel)
    return db_carousel

def update_carousel(db:Session,carousel_id:int,carousel:CarouselUpdate,image_path:Optional[str]=None)->Optional[Carousel]:
    db_carousel=db.query(Carousel).filter(Carousel.id==carousel_id,Carousel.is_deleted==False).first()
    if not db_carousel:
        return None
    for k,v in carousel.dict(exclude_unset=True).items():
        setattr(db_carousel,k,v)
    if image_path:
        db_carousel.image_path=image_path
    db.commit()
    db.refresh(db_carousel)
    return db_carousel

def delete_carousel(db:Session,carousel_id:int)->bool:
    db_carousel=db.query(Carousel).filter(Carousel.id==carousel_id,Carousel.is_deleted==False).first()
    if not db_carousel:
        return False
    db_carousel.is_deleted=True
    db.commit()
    return True

def update_sort(db:Session,carousel_id:int,sort_num:int)->Optional[Carousel]:
    db_carousel=db.query(Carousel).filter(Carousel.id==carousel_id,Carousel.is_deleted==False).first()
    if not db_carousel:
        return None
    db_carousel.sort_num=sort_num
    db.commit()
    db.refresh(db_carousel)
    return db_carousel