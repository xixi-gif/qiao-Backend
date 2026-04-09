from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.db.database import get_db
from app.api.schemas.carousel import CarouselCreate, CarouselUpdate, CarouselResponse
from app.api.crud.carousel import get_carousels, get_carousel_by_id, create_carousel, update_carousel, delete_carousel, \
    update_sort
from app.api.services.auth import get_current_user
from app.api.models.user import User
import os, uuid
import json
from app.api.core.redis_client import cache_get, cache_set, cache_delete

router = APIRouter()


@router.get("/carousels", response_model=List[CarouselResponse])
def get_carousels_endpoint(skip: int = 0, limit: int = 10, is_active: Optional[bool] = True,
                           db: Session = Depends(get_db)):
    cache_key = f"carousels:{skip}:{limit}:{is_active}"
    cached_data = cache_get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    data = get_carousels(db, skip, limit, is_active)

    serialized = []
    for c in data:
        serialized.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "image_path": c.image_path,
            "link": c.link,
            "sort_num": c.sort_num,
            "is_active": c.is_active,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None
        })

    cache_set(cache_key, json.dumps(serialized), ex=60)
    return data


@router.get("/carousels/{carousel_id}", response_model=CarouselResponse)
def get_carousel_endpoint(carousel_id: int, db: Session = Depends(get_db)):
    carousel = get_carousel_by_id(db, carousel_id)
    if not carousel:
        raise HTTPException(status_code=404, detail="轮播图不存在")
    return carousel


@router.post("/admin/carousels", response_model=CarouselResponse)
async def create_carousel_endpoint(title: str = Form(...), description: Optional[str] = Form(None),
                                   link: Optional[str] = Form(None), sort_num: int = Form(0),
                                   is_active: bool = Form(True), image: UploadFile = File(...),
                                   db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not image.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="仅支持图片格式")
    contents = await image.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片不能超过5MB")
    ext = os.path.splitext(image.filename)[-1]
    fname = f"carousel_{uuid.uuid4().hex}{ext}"
    save_dir = "static/carousel"
    os.makedirs(save_dir, exist_ok=True)
    fpath = os.path.join(save_dir, fname)
    with open(fpath, "wb") as f:
        f.write(contents)
    img_path = f"/static/carousel/{fname}"
    data = CarouselCreate(title=title, description=description, link=link, sort_num=sort_num, is_active=is_active)
    result = create_carousel(db, data, img_path)
    cache_delete("carousels:*")
    return result


@router.put("/admin/carousels/{carousel_id}", response_model=CarouselResponse)
async def update_carousel_endpoint(carousel_id: int, title: Optional[str] = Form(None),
                                   description: Optional[str] = Form(None), link: Optional[str] = Form(None),
                                   sort_num: Optional[int] = Form(None), is_active: Optional[bool] = Form(None),
                                   image: UploadFile = File(None), db: Session = Depends(get_db),
                                   current_user: User = Depends(get_current_user)):
    img_path = None
    if image:
        if not image.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            raise HTTPException(status_code=400, detail="仅支持图片格式")
        contents = await image.read()
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="图片不能超过5MB")
        ext = os.path.splitext(image.filename)[-1]
        fname = f"carousel_{uuid.uuid4().hex}{ext}"
        save_dir = "static/carousel"
        os.makedirs(save_dir, exist_ok=True)
        fpath = os.path.join(save_dir, fname)
        with open(fpath, "wb") as f:
            f.write(contents)
        img_path = f"/static/carousel/{fname}"
    data = CarouselUpdate(title=title, description=description, link=link,
                          sort_num=sort_num if sort_num is not None else 0,
                          is_active=is_active if is_active is not None else True)
    res = update_carousel(db, carousel_id, data, img_path)
    if not res:
        raise HTTPException(status_code=404, detail="轮播图不存在")
    cache_delete("carousels:*")
    return res


@router.put("/admin/carousels/sort/{carousel_id}")
def sort_carousel(carousel_id: int, sort_num: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    res = update_sort(db, carousel_id, sort_num)
    if not res:
        raise HTTPException(status_code=404, detail="轮播图不存在")
    cache_delete("carousels:*")
    return {"detail": "排序更新成功"}


@router.delete("/admin/carousels/{carousel_id}")
def delete_carousel_endpoint(carousel_id: int, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    if not delete_carousel(db, carousel_id):
        raise HTTPException(status_code=404, detail="轮播图不存在")
    cache_delete("carousels:*")
    return {"detail": "轮播图已删除"}