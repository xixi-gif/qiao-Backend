from sqlalchemy.orm import Session
from app.api.models.project import Project
from app.api.schemas.project import ProjectCreate, ProjectUpdate

def create_project(db: Session, project: ProjectCreate, merchant_id: int, cover_path: str = None):
    db_project = Project(
        title=project.title,
        category=project.category,
        tags=",".join(project.tags),
        cover=cover_path,
        address=project.address,
        start_time=project.start_time,
        end_time=project.end_time,
        price=project.price,
        max_people=project.max_people,
        description=project.description,
        contact=project.contact,
        merchant_id=merchant_id,
        status="pending",
        views=0,
        orders=0,
        is_deleted=False
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()

def get_projects_by_merchant(db: Session, merchant_id: int, skip: int = 0, limit: int = 10):
    return db.query(Project).filter(
        Project.merchant_id == merchant_id,
        Project.is_deleted == False
    ).offset(skip).limit(limit).all()

def update_project(db: Session, project_id: int, project_update: ProjectUpdate, cover_path: str = None):
    db_project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not db_project:
        return None
    update_data = project_update.dict(exclude_unset=True)
    if "tags" in update_data and isinstance(update_data["tags"], list):
        update_data["tags"] = ",".join(update_data["tags"])
    if cover_path:
        update_data["cover"] = cover_path

    update_data["status"] = "pending"

    for key, value in update_data.items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        project.is_deleted = True
        db.commit()
    return project