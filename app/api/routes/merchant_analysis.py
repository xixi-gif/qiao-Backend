from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from app.api.db.database import get_db
from app.api.models.project import Project
from app.api.models.interaction import  Like, Favorite, Comment
from app.api.services.auth import get_current_user
from app.api.models.user import User
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/merchant/analysis", tags=["商家数据分析"])

@router.get("/dashboard")
def get_merchant_dashboard(
    period: str = Query("month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "merchant":
        raise HTTPException(status_code=403, detail="仅商家可访问")

    now = datetime.utcnow()
    if period == "day":
        start = now - timedelta(days=1)
    elif period == "week":
        start = now - timedelta(days=7)
    elif period == "month":
        start = now - timedelta(days=30)
    elif period == "year":
        start = now - timedelta(days=365)
    else:
        start = now - timedelta(days=30)

    projects = db.query(Project).filter(
        Project.merchant_id == current_user.id,
        Project.is_deleted == False
    ).all()
    project_ids = [p.id for p in projects]

    publish_count = len(projects)
    view_count = sum(p.views for p in projects)

    like_count = db.query(func.count(Like.id)).filter(
        Like.target_type == "project",
        Like.target_id.in_(project_ids),
        Like.created_at >= start,
        Like.is_delete == False
    ).scalar() or 0

    favorite_count = db.query(func.count(Favorite.id)).filter(
        Favorite.target_type == "project",
        Favorite.target_id.in_(project_ids),
        Favorite.created_at >= start,
        Favorite.is_delete == False
    ).scalar() or 0

    comment_count = db.query(func.count(Comment.id)).filter(
        Comment.target_type == "project",
        Comment.target_id.in_(project_ids),
        Comment.created_at >= start,
        Comment.is_delete == False
    ).scalar() or 0

    return {
        "code": 200,
        "data": {
            "period": period,
            "publish_count": publish_count,
            "view_count": view_count,
            "like_count": like_count,
            "favorite_count": favorite_count,
            "comment_count": comment_count
        }
    }

@router.get("/trend")
def get_merchant_trend(
    period: str = Query("month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "merchant":
        raise HTTPException(status_code=403, detail="仅商家可访问")

    projects = db.query(Project).filter(
        Project.merchant_id == current_user.id,
        Project.is_deleted == False
    ).all()
    project_ids = [p.id for p in projects]

    now = datetime.utcnow()
    days = 30 if period == "month" else 7
    start = now - timedelta(days=days)

    trend = []
    current_day = start
    while current_day <= now:
        day_str = current_day.strftime("%Y-%m-%d")
        next_day = current_day + timedelta(days=1)

        likes = db.query(func.count(Like.id)).filter(
            Like.target_type == "project",
            Like.target_id.in_(project_ids),
            Like.created_at.between(current_day, next_day),
            Like.is_delete == False
        ).scalar() or 0

        comments = db.query(func.count(Comment.id)).filter(
            Comment.target_type == "project",
            Comment.target_id.in_(project_ids),
            Comment.created_at.between(current_day, next_day),
            Comment.is_delete == False
        ).scalar() or 0

        favorites = db.query(func.count(Favorite.id)).filter(
            Favorite.target_type == "project",
            Favorite.target_id.in_(project_ids),
            Favorite.created_at.between(current_day, next_day),
            Favorite.is_delete == False
        ).scalar() or 0

        trend.append({
            "date": day_str,
            "views": 0,
            "likes": likes,
            "comments": comments,
            "favorites": favorites
        })
        current_day = next_day

    return {"code": 200, "data": trend}