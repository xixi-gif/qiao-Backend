from sqlalchemy.orm import Session
from app.api.models.interaction import Favorite, Like, Comment, Message
from app.api.models.project import Project
from app.api.models.user import User
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

def create_favorite(db: Session, user_id: int, data):
    try:
        existing = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.project_id == data.project_id
        ).first()

        if existing:
            existing.is_delete = not existing.is_delete
            db.commit()
            return {"status": "success", "action": "unfavorite" if existing.is_delete else "favorite"}
        else:
            new_fav = Favorite(
                user_id=user_id,
                project_id=data.project_id,
                created_at=datetime.now(),
                is_delete=False
            )
            db.add(new_fav)
            db.commit()
            db.refresh(new_fav)
            return {"status": "success", "action": "favorite"}

    except IntegrityError:
        db.rollback()
        return {"status": "exists", "action": "none"}

def check_user_fav(db: Session, user_id: int, project_id: int):
    res = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.project_id == project_id,
        Favorite.is_delete == False
    ).first()
    return res is not None

def get_fav_count(db: Session, project_id: int):
    return db.query(Favorite).filter(
        Favorite.project_id == project_id,
        Favorite.is_delete == False
    ).count()

def delete_favorite(db: Session, user_id: int, project_id: int):
    fav = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.project_id == project_id
    ).first()
    if fav:
        fav.is_delete = True
        db.commit()

def create_like(db: Session, user_id: int, data):
    try:
        existing = db.query(Like).filter(
            Like.user_id == user_id,
            Like.project_id == data.project_id
        ).first()

        if existing:
            existing.is_delete = not existing.is_delete
            db.commit()
            return {"status": "success", "action": "unlike" if existing.is_delete else "like"}
        else:
            new_like = Like(
                user_id=user_id,
                project_id=data.project_id,
                created_at=datetime.now(),
                is_delete=False
            )
            db.add(new_like)
            db.commit()
            return {"status": "success", "action": "like"}
    except IntegrityError:
        db.rollback()
        return {"status": "exists"}

def check_user_like(db: Session, user_id: int, project_id: int):
    res = db.query(Like).filter(
        Like.user_id == user_id,
        Like.project_id == project_id,
        Like.is_delete == False
    ).first()
    return res is not None

def get_like_count(db: Session, project_id: int):
    return db.query(Like).filter(
        Like.project_id == project_id,
        Like.is_delete == False
    ).count()

def delete_like(db: Session, user_id: int, project_id: int):
    like = db.query(Like).filter(
        Like.user_id == user_id,
        Like.project_id == project_id
    ).first()
    if like:
        like.is_delete = True
        db.commit()

def send_message(db: Session, to_user_id, from_user_id, project_id, comment_id, content):
    msg = Message(
        to_user_id=to_user_id,
        from_user_id=from_user_id,
        project_id=project_id,
        comment_id=comment_id,
        content=content
    )
    db.add(msg)
    db.commit()

def create_comment(db: Session, user_id: int, data):
    new_comment = Comment(
        user_id=user_id,
        project_id=data.project_id,
        parent_id=data.parent_id,
        content=data.content,
        created_at=datetime.now(),
        status="pending"
    )
    db.add(new_comment)
    db.flush()

    if data.parent_id:
        parent = db.query(Comment).filter(Comment.id == data.parent_id).first()
        if parent and parent.user_id != user_id:
            send_message(
                db=db,
                to_user_id=parent.user_id,
                from_user_id=user_id,
                project_id=data.project_id,
                comment_id=new_comment.id,
                content=data.content
            )

    db.commit()
    return new_comment

def delete_comment(db: Session, comment_id: int, user_id: int):
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.user_id == user_id
    ).first()
    if comment:
        comment.is_delete = True
        db.commit()
        return True
    return False

def get_comments(db: Session, project_id: int):
    return db.query(Comment, User).join(User, Comment.user_id == User.id).filter(
        Comment.project_id == project_id,
        Comment.status == "approved",
        Comment.is_delete == False
    ).order_by(Comment.created_at.desc()).all()

def audit_comment(db: Session, comment_id: int, status: str):
    c = db.query(Comment).get(comment_id)
    if c:
        c.status = status
        db.commit()

def admin_get_all_comments(db: Session):
    return db.query(Comment, User, Project).join(User, Comment.user_id == User.id).join(Project, Comment.project_id == Project.id).order_by(Comment.id.desc()).all()

def get_user_favorites(db: Session, user_id: int):
    return db.query(Favorite, Project).join(Project, Favorite.project_id == Project.id).filter(Favorite.user_id == user_id, Favorite.is_delete == False).all()

def get_user_likes(db: Session, user_id: int):
    return db.query(Like, Project).join(Project, Like.project_id == Project.id).filter(Like.user_id == user_id, Like.is_delete == False).all()

def get_user_comments(db: Session, user_id: int):
    return []


def get_user_messages(db: Session, user_id):
    reply_comment = aliased(Comment)
    parent_comment = aliased(Comment)

    return db.query(
        Message,
        User.username,
        User.avatar,
        Project.title,
        parent_comment.content.label("my_original_comment"),
        reply_comment.content.label("his_reply_comment")
    )\
    .join(User, Message.from_user_id == User.id)\
    .join(Project, Message.project_id == Project.id)\
    .outerjoin(reply_comment, Message.comment_id == reply_comment.id)\
    .outerjoin(parent_comment, reply_comment.parent_id == parent_comment.id)\
    .filter(Message.to_user_id == user_id)\
    .order_by(Message.id.desc())\
    .all()

def mark_message_read(db: Session, msg_id, user_id):
    msg = db.query(Message).filter(Message.id == msg_id, Message.to_user_id == user_id).first()
    if msg:
        msg.is_read = True
        db.commit()

def mark_all_read(db: Session, user_id):
    db.query(Message).filter(Message.to_user_id == user_id).update({Message.is_read: True})
    db.commit()