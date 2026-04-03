import re
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.api.db.database import get_db
from app.api.crud.markdown import get_docs, get_doc, create_doc, update_doc, delete_doc_logic
from app.api.schemas.markdown import MarkdownDocCreate, MarkdownDocUpdate
from app.api.utils.file_util import save_md, save_image
from app.api.models.markdown import MarkdownDoc, MarkdownImage, UserMarkdownFavorite
from typing import List

router = APIRouter(prefix="/api/markdown", tags=["markdown"])


@router.get("/list")
def list_docs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(MarkdownDoc).filter(MarkdownDoc.is_deleted == False) \
        .order_by(MarkdownDoc.created_at.desc()) \
        .offset(skip).limit(limit).all()


@router.get("/{doc_id}")
def get_one(doc_id: int, db: Session = Depends(get_db)):
    doc = get_doc(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404)
    return doc


@router.post("/create")
def create(data: MarkdownDocCreate, db: Session = Depends(get_db)):
    path = save_md(data.title, data.content)
    return create_doc(db, data, author_id=1, file_path=path)


@router.put("/{doc_id}")
def edit(doc_id: int, data: MarkdownDocUpdate, db: Session = Depends(get_db)):
    doc = update_doc(db, doc_id, data)
    if not doc:
        raise HTTPException(status_code=404)
    return doc


@router.delete("/{doc_id}")
def delete(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(MarkdownDoc).filter(MarkdownDoc.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    doc.is_deleted = True
    db.commit()
    return {"ok": True}


@router.post("/image")
async def upimg(file: UploadFile = File(...)):
    suffix = file.filename.split(".")[-1].lower()
    b = await file.read()
    url = save_image(b, suffix)
    return {"url": url}


@router.post("/batch-upload")
async def batch_upload(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    file_map = {f.filename: f for f in files}
    md_files = []
    img_files = []
    for name, f in file_map.items():
        if name.endswith(".md"):
            md_files.append((name, f))
        else:
            img_files.append((name, f))
    img_map = {}
    for name, f in img_files:
        key = re.sub(r"\.\w+$", "", name)
        img_map[key] = f
    success = []
    for md_name, md_file in md_files:
        try:
            title = re.sub(r"\.md$", "", md_name)
            content = (await md_file.read()).decode("utf-8")
            img_obj = None
            if title in img_map:
                img_file = img_map[title]
                img_bytes = await img_file.read()
                img_url = save_image(img_bytes, img_file.filename.split(".")[-1])
                content = f"![{title}]({img_url})\n\n{content}"
                img_obj = MarkdownImage(filename=img_file.filename, url=img_url, doc_id=-1)
                db.add(img_obj)
            doc = create_doc(db, MarkdownDocCreate(title=title, content=content), author_id=1,
                             file_path=save_md(title, content))
            if img_obj:
                img_obj.doc_id = doc.id
            db.commit()
            success.append(doc.id)
        except Exception as e:
            print(e)
            continue
    return {"success": success}



@router.post("/favorite/{doc_id}")
def toggle_favorite(doc_id: int, db: Session = Depends(get_db)):
    user_id = 1  # 你自己的用户ID，后面可改
    doc = db.query(MarkdownDoc).filter(MarkdownDoc.id == doc_id, MarkdownDoc.is_deleted == False).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    fav = db.query(UserMarkdownFavorite).filter(
        UserMarkdownFavorite.user_id == user_id,
        UserMarkdownFavorite.doc_id == doc_id
    ).first()

    if fav:
        db.delete(fav)
        db.commit()
        return {"action": "unfavorite"}
    else:
        new_fav = UserMarkdownFavorite(user_id=user_id, doc_id=doc_id)
        db.add(new_fav)
        db.commit()
        return {"action": "favorite"}



@router.get("/my/favorites")
def get_my_favorites(db: Session = Depends(get_db)):
    user_id = 1
    favs = db.query(UserMarkdownFavorite).filter(UserMarkdownFavorite.user_id == user_id).all()
    doc_ids = [f.doc_id for f in favs]
    docs = db.query(MarkdownDoc).filter(
        MarkdownDoc.id.in_(doc_ids),
        MarkdownDoc.is_deleted == False
    ).all()
    return docs


@router.get("/my/favorite-ids")
def get_my_favorite_ids(db: Session = Depends(get_db)):
    user_id = 1
    favs = db.query(UserMarkdownFavorite).filter(UserMarkdownFavorite.user_id == user_id).all()
    return {"ids": [f.doc_id for f in favs]}