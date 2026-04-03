from sqlalchemy.orm import Session
from app.api.models.markdown import MarkdownDoc
from app.api.schemas.markdown import MarkdownDocCreate, MarkdownDocUpdate

def get_doc(db: Session, doc_id: int):
    return db.query(MarkdownDoc).filter(MarkdownDoc.id == doc_id, MarkdownDoc.is_deleted == False).first()

def get_docs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(MarkdownDoc).filter(MarkdownDoc.is_deleted == False).offset(skip).limit(limit).all()

def create_doc(db: Session, doc: MarkdownDocCreate, author_id: int, file_path: str = None):
    db_doc = MarkdownDoc(title=doc.title, content=doc.content, author_id=author_id, file_path=file_path)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def update_doc(db: Session, doc_id: int, doc: MarkdownDocUpdate):
    db_doc = get_doc(db, doc_id)
    if not db_doc:
        return None
    if doc.title:
        db_doc.title = doc.title
    if doc.content:
        db_doc.content = doc.content
    db.commit()
    db.refresh(db_doc)
    return db_doc

def delete_doc_logic(db: Session, doc_id: int):
    db_doc = get_doc(db, doc_id)
    if not db_doc:
        return False
    db_doc.is_deleted = True
    db.commit()
    return True