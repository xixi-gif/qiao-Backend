from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.db.database import get_db
from app.api.services.auth import get_current_user
from app.api.models.user import User
from app.api.models.interaction import Like, Favorite, Comment, Message
from app.api.models.project import Project
from app.api.models.checkin import Checkin
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class InteractRequest(BaseModel):
    target_type: str
    target_id: int

@router.post("/interact/like")
async def create_like(body: InteractRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    target_type = body.target_type
    target_id = body.target_id
    like = db.query(Like).filter(Like.user_id == current_user.id, Like.target_type == target_type, Like.target_id == target_id).first()
    if like:
        like.is_delete = not like.is_delete
        db.commit()
        return {"is_liked": not like.is_delete}
    new_like = Like(user_id=current_user.id, target_type=target_type, target_id=target_id, created_at=datetime.now(), is_delete=False)
    db.add(new_like)
    db.commit()
    return {"is_liked": True}

@router.get("/interact/like/count")
async def get_like_count(target_type: str, target_id: int, db: Session = Depends(get_db)):
    cnt = db.query(Like).filter(Like.target_type == target_type, Like.target_id == target_id, Like.is_delete == False).count()
    return {"count": cnt}

@router.get("/interact/like/status")
async def get_like_status(target_type: str, target_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exists = db.query(Like).filter(Like.user_id == current_user.id, Like.target_type == target_type, Like.target_id == target_id, Like.is_delete == False).first()
    return {"is_liked": exists is not None}

@router.get("/interact/like/user/list")
async def get_user_likes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    likes = db.query(Like).filter(Like.user_id == current_user.id, Like.is_delete == False).all()
    data = []
    for l in likes:
        proj = db.query(Project).filter(Project.id == l.target_id).first()
        if proj:
            data.append({
                "project_id": proj.id,
                "title": proj.title,
                "cover": proj.cover,
                "created_at": l.created_at
            })
    return data

@router.post("/interact/favorite")
async def create_favorite(body: InteractRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    target_type = body.target_type
    target_id = body.target_id
    fav = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.target_type == target_type, Favorite.target_id == target_id).first()
    if fav:
        fav.is_delete = not fav.is_delete
        db.commit()
        return {"is_favorite": not fav.is_delete}
    new_fav = Favorite(user_id=current_user.id, target_type=target_type, target_id=target_id, created_at=datetime.now(), is_delete=False)
    db.add(new_fav)
    db.commit()
    return {"is_favorite": True}

@router.get("/interact/favorite/count")
async def get_favorite_count(target_type: str, target_id: int, db: Session = Depends(get_db)):
    cnt = db.query(Favorite).filter(Favorite.target_type == target_type, Like.target_id == target_id, Favorite.is_delete == False).count()
    return {"count": cnt}

@router.get("/interact/favorite/status")
async def get_favorite_status(target_type: str, target_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exists = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.target_type == target_type, Favorite.target_id == target_id, Favorite.is_delete == False).first()
    return {"is_favorite": exists is not None}

@router.get("/interact/favorite/user/list")
async def get_user_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favs = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.is_delete == False).all()
    data = []
    for f in favs:
        proj = db.query(Project).filter(Project.id == f.target_id).first()
        if proj:
            data.append({
                "project_id": proj.id,
                "title": proj.title,
                "cover": proj.cover,
                "created_at": f.created_at
            })
    return data

class CommentRequest(BaseModel):
    target_type: str
    target_id: int
    content: str
    parent_id: int = 0

@router.post("/interact/comment")
async def create_comment(body: CommentRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if body.target_type == "project":
        proj = db.query(Project).filter(Project.id == body.target_id).first()
        if not proj:
            raise HTTPException(status_code=404)

    new_comment = Comment(
        user_id=current_user.id,
        target_type=body.target_type,
        target_id=body.target_id,
        parent_id=body.parent_id,
        content=body.content,
        created_at=datetime.now(),
        is_delete=False,
        status="pending"
    )
    db.add(new_comment)
    db.flush()

    target_owner_id = None
    if body.target_type == "project":
        project = db.query(Project).filter(Project.id == body.target_id).first()
        if project:
            target_owner_id = project.merchant_id
    elif body.target_type == "checkin":
        checkin = db.query(Checkin).filter(Checkin.id == body.target_id).first()
        if checkin:
            target_owner_id = checkin.user_id

    if target_owner_id is not None and target_owner_id != current_user.id:
        msg = Message(
            to_user_id=target_owner_id,
            from_user_id=current_user.id,
            project_id=body.target_id,
            comment_id=new_comment.id,
            content=body.content,
            is_read=False,
            created_at=datetime.now()
        )
        db.add(msg)

    if body.parent_id > 0:
        parent_comment = db.query(Comment).filter(Comment.id == body.parent_id).first()
        if parent_comment and parent_comment.user_id != current_user.id:
            new_msg = Message(
                to_user_id=parent_comment.user_id,
                from_user_id=current_user.id,
                project_id=body.target_id,
                comment_id=body.parent_id,
                content=body.content,
                is_read=False,
                created_at=datetime.now()
            )
            db.add(new_msg)

    db.commit()
    return {"msg": "评论成功"}

@router.get("/interact/comment/user/list")
async def get_user_comments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comments = db.query(Comment).filter(
        Comment.user_id == current_user.id
    ).order_by(Comment.created_at.desc()).all()

    data = []
    for c in comments:
        title = "打卡内容"
        if c.target_type == "project":
            proj = db.query(Project).filter(Project.id == c.target_id).first()
            title = proj.title if proj else "项目"

        content = "该评论已删除" if c.is_delete else c.content

        data.append({
            "id": c.id,
            "project_id": c.target_id,
            "target_type": c.target_type,
            "title": title,
            "content": content,
            "status": c.status,
            "created_at": c.created_at,
            "is_delete": c.is_delete
        })
    return data

@router.get("/interact/comment/{target_type}/{target_id}")
async def get_comments(target_type: str, target_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(
        Comment.target_type == target_type,
        Comment.target_id == target_id,
        Comment.status == "approved"
    ).order_by(Comment.created_at.desc()).all()

    result = []
    for c in comments:
        user = db.query(User).filter(User.id == c.user_id).first()
        result.append({
            "id": c.id,
            "user_id": c.user_id,
            "username": user.username if user else "用户",
            "avatar": user.avatar if user else None,
            "parent_id": c.parent_id,
            "content": c.content,
            "is_delete": c.is_delete,
            "created_at": c.created_at,
            "status": c.status
        })
    return result

@router.delete("/interact/comment/{comment_id}")
async def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()
    if not comment:
        raise HTTPException(status_code=403)
    comment.is_delete = True
    db.commit()
    return {"msg": "删除成功"}

@router.get("/interact/admin/comment/all")
async def admin_get_all_comments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comments = db.query(Comment).order_by(Comment.created_at.desc()).all()
    res = []
    for c in comments:
        user = db.query(User).filter(User.id == c.user_id).first()
        proj = None
        if c.target_type == "project":
            proj = db.query(Project).filter(Project.id == c.target_id).first()
        res.append({
            "id": c.id,
            "username": user.username if user else "未知用户",
            "user_id": c.user_id,
            "project_id": c.target_id if c.target_type == "project" else None,
            "project_title": proj.title if proj else "打卡内容",
            "content": c.content,
            "status": c.status,
            "created_at": c.created_at,
            "is_delete": c.is_delete
        })
    return res

@router.put("/interact/admin/comment/audit/{comment_id}")
async def admin_audit_comment(comment_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404)
    comment.status = status
    db.commit()
    return {"msg": "审核成功"}

@router.delete("/interact/admin/comment/{comment_id}")
async def admin_delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404)
    comment.is_delete = True
    db.commit()
    return {"msg": "管理员删除成功"}

@router.get("/interact/message/my")
async def get_my_messages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    messages = db.query(Message).filter(Message.to_user_id == current_user.id).order_by(Message.created_at.desc()).all()
    result = []
    for msg in messages:
        project = db.query(Project).filter(Project.id == msg.project_id).first()
        from_user = db.query(User).filter(User.id == msg.from_user_id).first()
        my_comment = db.query(Comment).filter(Comment.id == msg.comment_id).first()

        my_comment_content = "评论已删除"
        if my_comment and not my_comment.is_delete:
            my_comment_content = my_comment.content

        result.append({
            "msg_id": msg.id,
            "my_comment": my_comment_content,
            "his_reply": msg.content,
            "is_read": msg.is_read,
            "created_at": msg.created_at,
            "project": {"id": project.id if project else 0, "title": project.title if project else "项目已删除"},
            "reply_user": {"username": from_user.username if from_user else "用户", "avatar": from_user.avatar if from_user else None}
        })
    return result

@router.post("/interact/message/read/{msg_id}")
async def read_message(msg_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = db.query(Message).filter(Message.id == msg_id, Message.to_user_id == current_user.id).first()
    if not msg:
        raise HTTPException(status_code=404)
    msg.is_read = True
    db.commit()
    return {"status": "ok"}

@router.post("/interact/message/read/all")
async def read_all_messages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Message).filter(Message.to_user_id == current_user.id, Message.is_read == False).update({Message.is_read: True})
    db.commit()
    return {"status": "ok"}