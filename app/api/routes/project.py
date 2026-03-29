from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from app.api.db.database import get_db
from app.api.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.api.crud.project import create_project, get_projects_by_merchant, get_project_by_id, delete_project, update_project
from app.api.services.auth import get_current_merchant
from app.api.models.user import User
from app.api.models.project import Project
import os
import uuid

router = APIRouter()

@router.post("/merchant/projects", response_model=ProjectResponse)
async def create_project_endpoint(
    title: str = Form(...),
    category: str = Form(...),
    tags: str = Form(...),
    address: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    price: float = Form(...),
    max_people: int = Form(...),
    description: str = Form(...),
    contact: str = Form(...),
    cover: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_merchant: User = Depends(get_current_merchant)
):
    try:
        start_time_dt = datetime.fromisoformat(start_time.replace("Z", ""))
        end_time_dt = datetime.fromisoformat(end_time.replace("Z", ""))
        cover_path = None
        if cover:
            contents = await cover.read()
            if not cover.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                raise HTTPException(status_code=400, detail="仅支持图片格式")
            if len(contents) > 2 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="图片不能超过2MB")
            file_ext = os.path.splitext(cover.filename)[-1]
            file_name = f"project_{uuid.uuid4().hex}{file_ext}"
            save_dir = "static/projects"
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(contents)
            cover_path = f"/{file_path}"
        project_create = ProjectCreate(
            title=title,
            category=category,
            tags=tags.split(","),
            address=address,
            start_time=start_time_dt,
            end_time=end_time_dt,
            price=price,
            max_people=max_people,
            description=description,
            contact=contact
        )
        project = create_project(db, project_create, current_merchant.id, cover_path)
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")

@router.get("/merchant/projects", response_model=list[ProjectResponse])
def get_merchant_projects(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_merchant: User = Depends(get_current_merchant)
):
    return get_projects_by_merchant(db, current_merchant.id, skip, limit)

@router.get("/merchant/projects/{id}", response_model=ProjectResponse)
def get_project_detail(
    id: int,
    db: Session = Depends(get_db),
    current_merchant: User = Depends(get_current_merchant)
):
    project = get_project_by_id(db, id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    if project.merchant_id != current_merchant.id:
        raise HTTPException(status_code=403, detail="无权限访问")
    return project

@router.delete("/merchant/projects/{id}")
def delete_project_endpoint(
    id: int,
    db: Session = Depends(get_db),
    current_merchant: User = Depends(get_current_merchant)
):
    project = get_project_by_id(db, id)
    if not project or project.merchant_id != current_merchant.id:
        raise HTTPException(status_code=404, detail="项目不存在或无权限")
    project.is_deleted = True
    db.commit()
    return {"detail": "删除成功"}

@router.put("/merchant/projects/{id}", response_model=ProjectResponse)
async def update_project_endpoint(
    id: int,
    title: str = Form(None),
    category: str = Form(None),
    tags: str = Form(None),
    address: str = Form(None),
    start_time: str = Form(None),
    end_time: str = Form(None),
    price: float = Form(None),
    max_people: int = Form(None),
    description: str = Form(None),
    contact: str = Form(None),
    cover: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_merchant: User = Depends(get_current_merchant)
):
    project = get_project_by_id(db, id)
    if not project or project.merchant_id != current_merchant.id:
        raise HTTPException(status_code=404, detail="项目不存在或无权限")
    new_cover = project.cover
    if cover:
        contents = await cover.read()
        if not cover.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            raise HTTPException(status_code=400, detail="仅支持图片格式")
        if len(contents) > 2 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="图片不能超过2MB")
        file_ext = os.path.splitext(cover.filename)[-1]
        file_name = f"project_{uuid.uuid4().hex}{file_ext}"
        save_dir = "static/projects"
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(contents)
        if project.cover and os.path.exists(project.cover.strip("/")):
            os.remove(project.cover.strip("/"))
        new_cover = f"/{file_path}"
    update_data = ProjectUpdate(
        title=title,
        category=category,
        tags=tags.split(",") if tags else None,
        address=address,
        start_time=datetime.fromisoformat(start_time.replace("Z", "")) if start_time else None,
        end_time=datetime.fromisoformat(end_time.replace("Z", "")) if end_time else None,
        price=price,
        max_people=max_people,
        description=description,
        contact=contact
    )
    return update_project(db, id, update_data, new_cover)