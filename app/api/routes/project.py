from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from app.api.db.database import get_db
from app.api.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.api.crud.project import create_project, get_projects_by_merchant, get_project_by_id, delete_project, update_project
from app.api.services.auth import get_current_merchant, get_current_user
from app.api.models.user import User
from app.api.models.project import Project
from pydantic import BaseModel
import os
import uuid

router = APIRouter()

class BatchAuditRequest(BaseModel):
    ids: List[int]
    status: str

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
            cover_path = f"/static/projects/{file_name}"
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
        new_cover = f"/static/projects/{file_name}"
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

@router.get("/admin/projects/list", response_model=list[ProjectResponse])
def admin_get_all_projects(
    title: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")
    query = db.query(Project).filter(Project.is_deleted == False)
    if title:
        query = query.filter(Project.title.contains(title))
    if status:
        query = query.filter(Project.status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/admin/projects/{id}", response_model=ProjectResponse)
def admin_get_project_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")
    project = get_project_by_id(db, id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project

@router.put("/admin/projects/audit/{id}")
def admin_audit_project(
    id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")
    if status not in ["active", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="状态不合法")
    project = get_project_by_id(db, id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    project.status = status
    db.commit()
    return {"detail": "审核成功"}

@router.put("/admin/projects/batch-audit")
def admin_batch_audit_projects(
    body: BatchAuditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")
    if body.status not in ["active", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="状态不合法")
    projects = db.query(Project).filter(Project.id.in_(body.ids), Project.is_deleted == False).all()
    for p in projects:
        p.status = body.status
    db.commit()
    return {"detail": f"批量审核成功，共 {len(projects)} 条"}

@router.delete("/admin/projects/{id}")
def admin_delete_project(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")
    project = get_project_by_id(db, id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    project.is_deleted = True
    db.commit()
    return {"detail": "管理员删除成功"}

@router.get("/tourism/projects")
def tourism_get_active_projects(
    title: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Project, User).join(
        User, Project.merchant_id == User.id
    ).filter(
        Project.status == "active",
        Project.is_deleted == False
    )

    if title:
        query = query.filter(Project.title.contains(title))

    results = query.offset(skip).limit(limit).all()
    res = []
    for project, user in results:
        item = {
            "id": project.id,
            "title": project.title,
            "category": project.category,
            "tags": project.tags,
            "cover": project.cover,
            "address": project.address,
            "start_time": project.start_time,
            "end_time": project.end_time,
            "price": project.price,
            "max_people": project.max_people,
            "description": project.description,
            "contact": project.contact,
            "status": project.status,
            "merchant_id": project.merchant_id,
            "views": project.views,
            "orders": project.orders,
            "merchant": {
                "shopName": user.shop_name,
                "avatar": user.avatar,
                "shopAddress": user.shop_address
            }
        }
        res.append(item)
    return res

@router.post("/tourism/projects/{id}/view")
def add_project_view(
    id: int,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == id,
        Project.status == "active",
        Project.is_deleted == False
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    project.views = (project.views or 0) + 1
    db.commit()
    return {"detail": "success", "views": project.views}

@router.get("/tourism/projects/{id}")
def tourism_get_project_detail(
    id: int,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == id,
        Project.status == "active",
        Project.is_deleted == False
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或未上线")

    user = db.query(User).filter(User.id == project.merchant_id).first()

    return {
        "id": project.id,
        "title": project.title,
        "category": project.category,
        "tags": project.tags,
        "cover": project.cover,
        "address": project.address,
        "start_time": project.start_time,
        "end_time": project.end_time,
        "price": project.price,
        "max_people": project.max_people,
        "description": project.description,
        "contact": project.contact,
        "status": project.status,
        "merchant_id": project.merchant_id,
        "views": project.views,
        "orders": project.orders,
        "merchant": {
            "shopName": user.shop_name,
            "avatar": user.avatar,
            "shopAddress": user.shop_address
        }
    }

@router.get("/tourism/merchant/{merchant_id}")
def tourism_get_merchant_info(
    merchant_id: int,
    db: Session = Depends(get_db)
):
    merchant = db.query(User).filter(User.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")

    projects = db.query(Project).filter(
        Project.merchant_id == merchant_id,
        Project.status == "active",
        Project.is_deleted == False
    ).all()

    return {
        "id": merchant.id,
        "shopName": merchant.shop_name,
        "avatar": merchant.avatar,
        "shopAddress": merchant.shop_address,
        "introduction": "",
        "projects": projects
    }