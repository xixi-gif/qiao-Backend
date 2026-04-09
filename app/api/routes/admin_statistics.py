from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, case, and_
from sqlalchemy.orm import Session
from app.api.db.database import get_db
from app.api.models.project import Project
from app.api.models.checkin import Checkin
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
    total_checkins = db.query(func.count(Checkin.id)).filter(Checkin.is_deleted == False).scalar() or 0

    total_views = (db.query(func.sum(Project.views)).filter(Project.is_deleted == False).scalar() or 0) + (db.query(func.sum(Checkin.view_count)).filter(Checkin.is_deleted == False).scalar() or 0)

    like_count = db.query(func.count(Like.id)).filter(Like.target_type.in_(["project", "checkin"]), Like.created_at >= start, Like.is_delete == False).scalar() or 0
    favorite_count = db.query(func.count(Favorite.id)).filter(Favorite.target_type.in_(["project", "checkin"]), Favorite.created_at >= start, Favorite.is_delete == False).scalar() or 0
    comment_count = db.query(func.count(Comment.id)).filter(Comment.target_type.in_(["project", "checkin"]), Comment.created_at >= start, Comment.is_delete == False).scalar() or 0

    period_projects = db.query(func.count(Project.id)).filter(Project.is_deleted == False, Project.created_at >= start).scalar() or 0
    period_checkins = db.query(func.count(Checkin.id)).filter(Checkin.is_deleted == False, Checkin.create_time >= start).scalar() or 0

    return {
        "code": 200,
        "data": {
            "period": period,
            "total_users": total_users,
            "total_merchants": total_merchants,
            "total_markdown": total_markdown,
            "total_projects": total_projects,
            "total_checkins": total_checkins,
            "total_views": total_views,
            "like_count": like_count,
            "favorite_count": favorite_count,
            "comment_count": comment_count,
            "period_projects": period_projects,
            "period_checkins": period_checkins
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

        daily_projects = db.query(func.count(Project.id)).filter(Project.is_deleted == False, Project.created_at.between(current_day, next_day)).scalar() or 0
        daily_checkins = db.query(func.count(Checkin.id)).filter(Checkin.is_deleted == False, Checkin.create_time.between(current_day, next_day)).scalar() or 0
        daily_likes = db.query(func.count(Like.id)).filter(Like.target_type.in_(["project", "checkin"]), Like.created_at.between(current_day, next_day), Like.is_delete == False).scalar() or 0
        daily_favorites = db.query(func.count(Favorite.id)).filter(Favorite.target_type.in_(["project", "checkin"]), Favorite.created_at.between(current_day, next_day), Favorite.is_delete == False).scalar() or 0
        daily_comments = db.query(func.count(Comment.id)).filter(Comment.target_type.in_(["project", "checkin"]), Comment.created_at.between(current_day, next_day), Comment.is_delete == False).scalar() or 0

        trend.append({
            "date": day_str,
            "projects": daily_projects,
            "checkins": daily_checkins,
            "likes": daily_likes,
            "favorites": daily_favorites,
            "comments": daily_comments
        })
        current_day = next_day

    return {"code": 200, "data": trend}


@router.get("/user-activity")
def get_user_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return {"code":200,"data":{"active":5,"total":5}}


@router.get("/merchant-activity")
def get_merchant_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    merchants = db.query(User).filter(User.role == UserRole.merchant, User.is_delete == False).all()
    total = len(merchants)
    active = 0
    for m in merchants:
        project_cnt = db.query(func.count(Project.id)).filter(Project.merchant_id == m.id, Project.is_deleted == False).scalar() or 0
        like_cnt = db.query(func.count(Like.id)).filter(Like.target_type == "project", Like.merchant_id == m.id, Like.is_delete == False).scalar() or 0
        score = project_cnt * 5 + like_cnt * 1
        if score >= 10:
            active += 1
    rate = round(active / total * 100, 1) if total > 0 else 0
    return {"code": 200, "data": {"active_rate": rate, "active": active, "total": total}}


@router.get("/top-projects")
def get_top_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    top5 = db.query(
        Project.id,
        Project.title,
        (Project.views * 1 + func.count(Like.id) * 2 + func.count(Favorite.id) * 3)
    ).outerjoin(Like, and_(Project.id == Like.target_id, Like.target_type == "project", Like.is_delete == False)
    ).outerjoin(Favorite, and_(Project.id == Favorite.target_id, Favorite.target_type == "project", Favorite.is_delete == False)
    ).filter(Project.is_deleted == False
    ).group_by(Project.id, Project.title, Project.views
    ).order_by((Project.views * 1 + func.count(Like.id) * 2 + func.count(Favorite.id) * 3).desc()
    ).limit(5).all()

    return {"code": 200, "data": [{"name": i[1], "value": i[2] or 0} for i in top5]}


@router.get("/top-merchants")
def get_top_merchants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    top5 = db.query(
        User.id,
        User.shop_name,
        (func.count(Project.id) * 10 + func.count(Like.id) * 2)
    ).outerjoin(Project, and_(User.id == Project.merchant_id, Project.is_deleted == False)
    ).outerjoin(Like, and_(Project.id == Like.target_id, Like.target_type == "project", Like.is_delete == False)
    ).filter(User.role == UserRole.merchant, User.is_delete == False
    ).group_by(User.id, User.shop_name
    ).order_by((func.count(Project.id) * 10 + func.count(Like.id) * 2).desc()
    ).limit(5).all()

    return {"code": 200, "data": [{"name": i[1] or f"商家{i[0]}", "value": i[2] or 0} for i in top5]}


@router.get("/top-users")
def get_top_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    top5 = db.query(
        User.id,
        User.username,
        (func.count(Like.id) * 1 + func.count(Favorite.id) * 2 + func.count(Comment.id) * 3)
    ).outerjoin(Like, and_(User.id == Like.user_id, Like.is_delete == False)
    ).outerjoin(Favorite, and_(User.id == Favorite.user_id, Favorite.is_delete == False)
    ).outerjoin(Comment, and_(User.id == Comment.user_id, Comment.is_delete == False)
    ).filter(User.is_delete == False
    ).group_by(User.id, User.username
    ).order_by((func.count(Like.id) * 1 + func.count(Favorite.id) * 2 + func.count(Comment.id) * 3).desc()
    ).limit(5).all()

    return {"code": 200, "data": [{"name": i[1], "value": i[2] or 0} for i in top5]}


@router.get("/merchant-status")
def get_merchant_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    normal = db.query(func.count(User.id)).filter(User.role == UserRole.merchant, User.is_delete == False).scalar() or 0
    no_project = db.query(func.count(User.id)).filter(User.role == UserRole.merchant, User.is_delete == False, ~User.id.in_(db.query(Project.merchant_id).filter(Project.is_deleted == False))).scalar() or 0
    return {"code": 200, "data": {"normal": normal, "no_project": no_project, "banned": 0}}