from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.db.database import get_db
from app.api.models.project import Project
from app.api.models.interaction import Like, Favorite, Comment
from app.api.models.user import User, UserRole
from app.api.models.markdown import MarkdownDoc
from app.api.services.auth import get_current_admin
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/admin/statistics", tags=["管理员-平台数据"])

@router.get("/dashboard")
def get_admin_dashboard(
    period: str = Query("month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
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

    total_users = db.query(func.count(User.id)).filter(User.is_delete == False).scalar() or 0
    total_merchants = db.query(func.count(User.id)).filter(User.role == UserRole.merchant, User.is_delete == False).scalar() or 0
    total_markdown = db.query(func.count(MarkdownDoc.id)).filter(MarkdownDoc.is_deleted == False).scalar() or 0
    total_projects = db.query(func.count(Project.id)).filter(Project.is_deleted == False).scalar() or 0
    total_views = db.query(func.sum(Project.views)).filter(Project.is_deleted == False).scalar() or 0

    like_count = db.query(func.count(Like.id)).filter(
        Like.target_type == "project",
        Like.created_at >= start,
        Like.is_delete == False
    ).scalar() or 0

    favorite_count = db.query(func.count(Favorite.id)).filter(
        Favorite.target_type == "project",
        Favorite.created_at >= start,
        Favorite.is_delete == False
    ).scalar() or 0

    comment_count = db.query(func.count(Comment.id)).filter(
        Comment.target_type == "project",
        Comment.created_at >= start,
        Comment.is_delete == False
    ).scalar() or 0

    return {
        "code": 200,
        "data": {
            "period": period,
            "total_users": total_users,
            "total_merchants": total_merchants,
            "total_markdown": total_markdown,
            "total_projects": total_projects,
            "total_views": total_views,
            "like_count": like_count,
            "favorite_count": favorite_count,
            "comment_count": comment_count
        }
    }

@router.get("/trend")
def get_admin_trend(
    period: str = Query("month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    now = datetime.utcnow()
    days = 30 if period == "month" else 7 if period == "week" else 1 if period == "day" else 365
    start = now - timedelta(days=days)

    trend = []
    current_day = start
    while current_day <= now:
        day_str = current_day.strftime("%Y-%m-%d")
        next_day = current_day + timedelta(days=1)

        daily_projects = db.query(func.count(Project.id)).filter(
            Project.is_deleted == False,
            Project.created_at.between(current_day, next_day)
        ).scalar() or 0

        daily_likes = db.query(func.count(Like.id)).filter(
            Like.target_type == "project",
            Like.created_at.between(current_day, next_day),
            Like.is_delete == False
        ).scalar() or 0

        daily_favorites = db.query(func.count(Favorite.id)).filter(
            Favorite.target_type == "project",
            Favorite.created_at.between(current_day, next_day),
            Favorite.is_delete == False
        ).scalar() or 0

        daily_comments = db.query(func.count(Comment.id)).filter(
            Comment.target_type == "project",
            Comment.created_at.between(current_day, next_day),
            Comment.is_delete == False
        ).scalar() or 0

        trend.append({
            "date": day_str,
            "projects": daily_projects,
            "likes": daily_likes,
            "favorites": daily_favorites,
            "comments": daily_comments
        })
        current_day = next_day

    return {"code": 200, "data": trend}