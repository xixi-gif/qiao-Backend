from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict
from app.api.models.announcement import Announcement, Attachment
from datetime import datetime


def create_announcement(
        db: Session,
        title: str,
        content: str,
        creator_id: int,
        status: str = "published",
        attachments: Optional[List[Dict[str, str]]] = None
) -> Announcement:
    if not all([title.strip(), content.strip(), creator_id]):
        raise ValueError("标题、内容、创建人ID为必填项且不能为空")

    if status not in ["draft", "published"]:
        raise ValueError("状态只能是 draft 或 published")

    try:
        db_announcement = Announcement(
            title=title,
            content=content,
            creator_id=creator_id,
            status=status
        )
        db.add(db_announcement)
        db.flush()

        valid_attachments = []
        if attachments and isinstance(attachments, list):
            for idx, att in enumerate(attachments):
                if not isinstance(att, dict):
                    raise ValueError(f"第{idx + 1}个附件格式错误，必须是字典类型")

                att_name = att.get("name", "").strip()
                att_url = att.get("url", "").strip()

                if not att_name or not att_url:
                    raise ValueError(f"第{idx + 1}个附件格式错误，必须包含非空的name和url字段")

                valid_attachments.append({
                    "name": att_name,
                    "url": att_url
                })

        for att in valid_attachments:
            db_attachment = Attachment(
                name=att["name"],
                url=att["url"],
                announcement_id=db_announcement.id
            )
            db.add(db_attachment)

        db.commit()
        db.refresh(db_announcement)
        return db_announcement

    except Exception as e:
        db.rollback()
        raise e


def get_announcements(db: Session, skip: int = 0, limit: int = 10) -> List[Announcement]:
    return db.query(Announcement).options(
        joinedload(Announcement.attachments)
    ).filter(Announcement.is_deleted == False).order_by(Announcement.created_at.desc()).offset(skip).limit(limit).all()


def get_announcement(db: Session, announcement_id: int) -> Optional[Announcement]:
    return db.query(Announcement).options(
        joinedload(Announcement.attachments)
    ).filter(Announcement.id == announcement_id, Announcement.is_deleted == False).first()


def update_announcement(
        db: Session,
        announcement_id: int,
        title: str = None,
        content: str = None,
        status: str = None,
        attachments: Optional[List[Dict[str, str]]] = None
) -> Optional[Announcement]:
    db_ann = db.query(Announcement).filter(Announcement.id == announcement_id, Announcement.is_deleted == False).first()
    if not db_ann:
        return None

    try:
        if title:
            db_ann.title = title.strip()
        if content:
            db_ann.content = content.strip()
        if status and status in ["draft", "published"]:
            db_ann.status = status

        if attachments is not None:
            db.query(Attachment).filter(Attachment.announcement_id == announcement_id).delete()

            valid_attachments = []
            if isinstance(attachments, list) and attachments:
                for att in attachments:
                    if isinstance(att, dict):
                        att_name = att.get("name", "").strip()
                        att_url = att.get("url", "").strip()
                        if att_name and att_url:
                            valid_attachments.append({
                                "name": att_name,
                                "url": att_url
                            })

            for att in valid_attachments:
                db_attachment = Attachment(
                    name=att["name"],
                    url=att["url"],
                    announcement_id=announcement_id
                )
                db.add(db_attachment)

        db.commit()
        db.refresh(db_ann)
        return db_ann
    except Exception as e:
        db.rollback()
        raise e


def delete_announcement(db: Session, announcement_id: int) -> Optional[Announcement]:
    db_ann = db.query(Announcement).filter(
        Announcement.id == announcement_id,
        Announcement.is_deleted == False
    ).first()
    if not db_ann:
        return None

    db_ann.is_deleted = True
    db.commit()
    db.refresh(db_ann)
    return db_ann


def get_announcement_count(db: Session) -> int:
    return db.query(Announcement).filter(Announcement.is_deleted == False).count()