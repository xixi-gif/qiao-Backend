from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import traceback
from app.api.db.database import get_db
from app.api.crud.announcement import create_announcement, get_announcements, get_announcement, update_announcement, \
    delete_announcement, get_announcement_count
from app.api.services.upload import save_upload_file
from app.api.core.config import settings
from app.api.schemas.announcement import (
    AnnouncementCreate, AnnouncementOut, ResponseModel, UploadResponse, AnnouncementUpdate
)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        max_size = getattr(settings, "max_file_size", 10 * 1024 * 1024)
        allowed_types = getattr(settings, "allowed_file_types", ["pdf", "docx", "png", "jpg", "jpeg"])

        if file.size > max_size:
            raise HTTPException(status_code=400, detail=f"文件大小不能超过{max_size / 1024 / 1024}MB")

        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in allowed_types:
            raise HTTPException(status_code=400, detail=f"仅支持{allowed_types}格式文件")

        file_info = await save_upload_file(file)
        return UploadResponse(success=True, message="文件上传成功", data=file_info)
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"文件上传失败：{str(e)}")


@router.post("/", response_model=ResponseModel)
def create_announcement_api(
        announcement_in: AnnouncementCreate,
        db: Session = Depends(get_db)
):
    try:
        db_ann = create_announcement(
            db=db,
            title=announcement_in.title,
            content=announcement_in.content,
            creator_id=announcement_in.creator_id,
            status=announcement_in.status,
            attachments=announcement_in.attachments or []
        )

        ann_out = AnnouncementOut.from_orm(db_ann)
        return ResponseModel(success=True, message="公告发布成功", data=ann_out)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"发布失败：{str(e)}")


@router.get("/", response_model=ResponseModel)
def read_announcements(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    try:
        anns = get_announcements(db, skip=skip, limit=limit)
        total = get_announcement_count(db)
        anns_out = [AnnouncementOut.from_orm(ann) for ann in anns]
        return ResponseModel(success=True, data={"items": anns_out, "total": total})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取公告列表失败：{str(e)}")


@router.get("/{ann_id}", response_model=ResponseModel)
def read_announcement(ann_id: int, db: Session = Depends(get_db)):
    try:
        ann = get_announcement(db, announcement_id=ann_id)
        if not ann:
            raise HTTPException(status_code=404, detail="公告不存在")

        ann_out = AnnouncementOut.from_orm(ann)
        return ResponseModel(success=True, data=ann_out)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取公告失败：{str(e)}")


# @router.put("/{ann_id}", response_model=ResponseModel)
# def update_announcement_api(
#         ann_id: int,
#         announcement_in: AnnouncementUpdate,
#         db: Session = Depends(get_db)
# ):
#     try:
#         ann = get_announcement(db, announcement_id=ann_id)
#         if not ann:
#             raise HTTPException(status_code=404, detail="公告不存在")
#
#         updated_ann = update_announcement(
#             db=db,
#             announcement_id=ann_id,
#             title=announcement_in.title,
#             content=announcement_in.content,
#             status=announcement_in.status,
#             attachments=announcement_in.attachments
#         )
#
#         ann_out = AnnouncementOut.from_orm(updated_ann)
#         return ResponseModel(success=True, message="公告编辑成功", data=ann_out)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"编辑失败：{str(e)}")


@router.delete("/{ann_id}", response_model=ResponseModel)
def delete_announcement_api(ann_id: int, db: Session = Depends(get_db)):
    try:
        ann = get_announcement(db, announcement_id=ann_id)
        if not ann:
            raise HTTPException(status_code=404, detail="公告不存在")

        delete_announcement(db, announcement_id=ann_id)
        return ResponseModel(success=True, message="公告删除成功")
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"删除失败：{str(e)}")